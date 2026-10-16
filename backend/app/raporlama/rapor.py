"""Raporlama paketi: GecikmeRaporu sınıfı.

Rapor veritabanında saklanmaz; her istendiğinde güncel ödünçlerden üretilir.
Ödünçleri listeler ama onlara sahip değildir (aggregation).
"""
from dataclasses import dataclass
from datetime import date

from app.odunc_islemleri.models import Odunc


@dataclass
class GecikmeSatiri:
    odunc_id: int
    uye_adi: str
    ogrenci_no: str
    kitap_basligi: str
    son_teslim_tarihi: date
    gecikme_gunu: int


class GecikmeRaporu:
    def __init__(self, olusturma_tarihi: date):
        self.olusturma_tarihi = olusturma_tarihi
        self.satirlar: list[GecikmeSatiri] = []

    def olustur(self, oduncler: list[Odunc]) -> None:
        tarih = self.olusturma_tarihi
        self.satirlar = sorted(
            (
                GecikmeSatiri(
                    odunc_id=o.odunc_id,
                    uye_adi=o.uye.ad,
                    ogrenci_no=o.uye.ogrenci_no,
                    kitap_basligi=o.kitap.baslik,
                    son_teslim_tarihi=o.son_teslim_tarihi,
                    gecikme_gunu=o.gecikme_gunu(tarih),
                )
                for o in oduncler
                if o.gecikmis_mi(tarih)
            ),
            key=lambda s: s.gecikme_gunu,
            reverse=True,
        )

    @property
    def toplam(self) -> int:
        return len(self.satirlar)
