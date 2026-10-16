"""Ödünç servisi: ödünç alma ve iade akışlarını yönetir, işlemi kaydeder."""
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ayarlar import bugun
from app.hatalar import BulunamadiHatasi
from app.katalog.servis import Katalog
from app.odunc_islemleri.models import Odunc
from app.uyelik.models import Uye


class OduncServisi:
    def __init__(self, db: Session):
        self.db = db
        self.katalog = Katalog(db)

    def _uye(self, uye_id: int) -> Uye:
        uye = self.db.get(Uye, uye_id)
        if uye is None:
            raise BulunamadiHatasi(f"{uye_id} numaralı üye bulunamadı.")
        return uye

    def odunc_al(self, uye_id: int, kitap_id: int) -> Odunc:
        uye = self._uye(uye_id)
        kitap = self.katalog.getir(kitap_id)
        odunc = uye.odunc_al(kitap, bugun())
        self.db.add(odunc)
        self.db.commit()
        return odunc

    def iade_et(self, odunc_id: int) -> Odunc:
        odunc = self.db.get(Odunc, odunc_id)
        if odunc is None:
            raise BulunamadiHatasi(f"{odunc_id} numaralı ödünç kaydı bulunamadı.")
        odunc.iade_et(bugun())
        self.db.commit()
        return odunc

    def uyenin_oduncleri(self, uye_id: int) -> list[Odunc]:
        self._uye(uye_id)
        sorgu = (
            select(Odunc)
            .where(Odunc.uye_id == uye_id)
            .order_by(Odunc.iade_tarihi.is_not(None), Odunc.alis_tarihi.desc())
        )
        return list(self.db.scalars(sorgu))

    def aktif_oduncler(self) -> list[Odunc]:
        return list(self.db.scalars(select(Odunc).where(Odunc.iade_tarihi.is_(None))))
