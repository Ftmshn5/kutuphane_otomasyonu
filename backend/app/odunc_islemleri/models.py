"""Ödünç işlemleri paketi: Odunc sınıfı (Uye ile Kitap arasındaki ilişki sınıfı)."""
from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.hatalar import IsKuraliHatasi

if TYPE_CHECKING:
    from app.katalog.models import Kitap
    from app.uyelik.models import Uye


class Odunc(Base):
    __tablename__ = "oduncler"

    odunc_id: Mapped[int] = mapped_column(primary_key=True)
    uye_id: Mapped[int] = mapped_column(ForeignKey("uyeler.uye_id"))
    kitap_id: Mapped[int] = mapped_column(ForeignKey("kitaplar.kitap_id"))
    alis_tarihi: Mapped[date]
    son_teslim_tarihi: Mapped[date]
    iade_tarihi: Mapped[date | None]

    uye: Mapped[Uye] = relationship(back_populates="oduncler")
    kitap: Mapped[Kitap] = relationship(back_populates="oduncler")

    def iade_et(self, tarih: date) -> None:
        if self.iade_tarihi is not None:
            raise IsKuraliHatasi("Bu kitap zaten iade edilmiş.")
        self.iade_tarihi = tarih
        self.kitap.stok.arttir()

    def gecikme_gunu(self, tarih: date) -> int:
        """İade edildiyse iade gününe, edilmediyse verilen tarihe göre gecikmeyi hesaplar."""
        referans = self.iade_tarihi or tarih
        return max(0, (referans - self.son_teslim_tarihi).days)

    def gecikmis_mi(self, tarih: date) -> bool:
        return self.iade_tarihi is None and self.gecikme_gunu(tarih) > 0
