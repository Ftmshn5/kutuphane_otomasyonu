"""Üyelik paketi: Uye ve Yonetici sınıfları."""
from __future__ import annotations

from datetime import date, timedelta
from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.ayarlar import MAKS_AKTIF_ODUNC, ODUNC_SURESI_GUN
from app.database import Base
from app.hatalar import IsKuraliHatasi
from app.katalog.models import Kitap, Stok

if TYPE_CHECKING:
    from app.katalog.servis import Katalog
    from app.odunc_islemleri.models import Odunc
    from app.raporlama.rapor import GecikmeRaporu


class Uye(Base):
    __tablename__ = "uyeler"

    uye_id: Mapped[int] = mapped_column(primary_key=True)
    ad: Mapped[str] = mapped_column(String(100))
    ogrenci_no: Mapped[str] = mapped_column(String(20), unique=True)
    email: Mapped[str] = mapped_column(String(120), unique=True)

    # Uye 1 —— 0..* Odunc
    oduncler: Mapped[list[Odunc]] = relationship(back_populates="uye")

    def aktif_oduncler(self) -> list[Odunc]:
        return [o for o in self.oduncler if o.iade_tarihi is None]

    def kitap_ara(self, katalog: Katalog, anahtar: str) -> list[Kitap]:
        return katalog.ara(anahtar)

    def odunc_al(self, kitap: Kitap, tarih: date) -> Odunc:
        from app.odunc_islemleri.models import Odunc

        aktif = self.aktif_oduncler()
        if any(o.kitap_id == kitap.kitap_id for o in aktif):
            raise IsKuraliHatasi("Bu kitap zaten sizde.")
        if len(aktif) >= MAKS_AKTIF_ODUNC:
            raise IsKuraliHatasi(f"Aynı anda en fazla {MAKS_AKTIF_ODUNC} kitap alabilirsiniz.")
        if not kitap.musait_mi():
            raise IsKuraliHatasi("Bu kitabın rafta kopyası kalmadı.")

        kitap.stok.azalt()
        return Odunc(
            uye=self,
            kitap=kitap,
            alis_tarihi=tarih,
            son_teslim_tarihi=tarih + timedelta(days=ODUNC_SURESI_GUN),
        )


class Yonetici(Base):
    __tablename__ = "yoneticiler"

    yonetici_id: Mapped[int] = mapped_column(primary_key=True)
    ad: Mapped[str] = mapped_column(String(100))

    # Yonetici 1 —— 0..* Kitap
    eklenen_kitaplar: Mapped[list[Kitap]] = relationship(back_populates="ekleyen")

    def kitap_ekle(self, baslik: str, yazar: str, isbn: str, adet: int) -> Kitap:
        return Kitap(
            baslik=baslik.strip(),
            yazar=yazar.strip(),
            isbn=isbn.strip(),
            stok=Stok(toplam_adet=adet),
            ekleyen=self,
        )

    def gecikme_raporu_al(self, oduncler: list[Odunc], tarih: date) -> GecikmeRaporu:
        from app.raporlama.rapor import GecikmeRaporu

        rapor = GecikmeRaporu(olusturma_tarihi=tarih)
        rapor.olustur(oduncler)
        return rapor
