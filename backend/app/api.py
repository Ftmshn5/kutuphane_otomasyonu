"""REST uç noktaları. İş mantığı sınıflarda, burada sadece istek/yanıt dönüşümü var."""
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ayarlar import bugun
from app.database import get_db
from app.hatalar import BulunamadiHatasi, IsKuraliHatasi
from app.katalog.models import Kitap
from app.katalog.servis import Katalog
from app.odunc_islemleri.models import Odunc
from app.odunc_islemleri.servis import OduncServisi
from app.semalar import (
    GecikmeRaporuCikti,
    KitapCikti,
    KitapEkleGirdi,
    OduncAlGirdi,
    OduncCikti,
    UyeCikti,
    YoneticiCikti,
)
from app.uyelik.models import Uye, Yonetici

router = APIRouter(prefix="/api")


def _kitap_cikti(k: Kitap) -> KitapCikti:
    return KitapCikti(
        kitap_id=k.kitap_id,
        baslik=k.baslik,
        yazar=k.yazar,
        isbn=k.isbn,
        toplam_adet=k.stok.toplam_adet,
        mevcut_adet=k.stok.mevcut_adet,
        musait=k.musait_mi(),
    )


def _odunc_cikti(o: Odunc) -> OduncCikti:
    return OduncCikti(
        odunc_id=o.odunc_id,
        uye_id=o.uye_id,
        kitap_id=o.kitap_id,
        kitap_basligi=o.kitap.baslik,
        alis_tarihi=o.alis_tarihi,
        son_teslim_tarihi=o.son_teslim_tarihi,
        iade_tarihi=o.iade_tarihi,
        gecikme_gunu=o.gecikme_gunu(bugun()),
    )


def _yonetici(db: Session, yonetici_id: int) -> Yonetici:
    yonetici = db.get(Yonetici, yonetici_id)
    if yonetici is None:
        raise BulunamadiHatasi("Bu işlem için geçerli bir yönetici gerekli.")
    return yonetici


@router.get("/saglik")
def saglik():
    return {"durum": "ok"}


# ---- Üyelik ----
@router.get("/uyeler", response_model=list[UyeCikti])
def uyeleri_listele(db: Session = Depends(get_db)):
    return db.scalars(select(Uye).order_by(Uye.ad)).all()


@router.get("/yoneticiler", response_model=list[YoneticiCikti])
def yoneticileri_listele(db: Session = Depends(get_db)):
    return db.scalars(select(Yonetici).order_by(Yonetici.ad)).all()


# ---- Katalog ----
@router.get("/kitaplar", response_model=list[KitapCikti])
def kitap_ara(q: str = "", db: Session = Depends(get_db)):
    return [_kitap_cikti(k) for k in Katalog(db).ara(q)]


@router.post("/kitaplar", response_model=KitapCikti, status_code=201)
def kitap_ekle(girdi: KitapEkleGirdi, db: Session = Depends(get_db)):
    yonetici = _yonetici(db, girdi.yonetici_id)
    if Katalog(db).isbn_var_mi(girdi.isbn.strip()):
        raise IsKuraliHatasi("Bu ISBN ile kayıtlı bir kitap zaten var.")
    kitap = yonetici.kitap_ekle(girdi.baslik, girdi.yazar, girdi.isbn, girdi.adet)
    db.add(kitap)
    db.commit()
    return _kitap_cikti(kitap)


# ---- Ödünç işlemleri ----
@router.post("/oduncler", response_model=OduncCikti, status_code=201)
def odunc_al(girdi: OduncAlGirdi, db: Session = Depends(get_db)):
    return _odunc_cikti(OduncServisi(db).odunc_al(girdi.uye_id, girdi.kitap_id))


@router.post("/oduncler/{odunc_id}/iade", response_model=OduncCikti)
def iade_et(odunc_id: int, db: Session = Depends(get_db)):
    return _odunc_cikti(OduncServisi(db).iade_et(odunc_id))


@router.get("/uyeler/{uye_id}/oduncler", response_model=list[OduncCikti])
def uyenin_oduncleri(uye_id: int, db: Session = Depends(get_db)):
    return [_odunc_cikti(o) for o in OduncServisi(db).uyenin_oduncleri(uye_id)]


# ---- Raporlama ----
@router.get("/raporlar/gecikme", response_model=GecikmeRaporuCikti)
def gecikme_raporu(yonetici_id: int, db: Session = Depends(get_db)):
    yonetici = _yonetici(db, yonetici_id)
    rapor = yonetici.gecikme_raporu_al(OduncServisi(db).aktif_oduncler(), bugun())
    return GecikmeRaporuCikti(
        olusturma_tarihi=rapor.olusturma_tarihi, toplam=rapor.toplam, satirlar=rapor.satirlar
    )
