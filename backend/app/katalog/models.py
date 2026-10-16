"""Katalog paketi: Kitap ve Stok sınıfları."""
from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.hatalar import IsKuraliHatasi

if TYPE_CHECKING:
    from app.odunc_islemleri.models import Odunc
    from app.uyelik.models import Yonetici


class Kitap(Base):
    __tablename__ = "kitaplar"

    kitap_id: Mapped[int] = mapped_column(primary_key=True)
    baslik: Mapped[str] = mapped_column(String(200))
    yazar: Mapped[str] = mapped_column(String(120))
    isbn: Mapped[str] = mapped_column(String(20), unique=True)
    ekleyen_id: Mapped[int | None] = mapped_column(ForeignKey("yoneticiler.yonetici_id"))

    # Composition: Kitap 1 ◆— 1 Stok (kitap silinirse stoğu da silinir)
    stok: Mapped[Stok] = relationship(
        back_populates="kitap", uselist=False, cascade="all, delete-orphan"
    )
    oduncler: Mapped[list[Odunc]] = relationship(back_populates="kitap")
    ekleyen: Mapped[Yonetici | None] = relationship(back_populates="eklenen_kitaplar")

    def musait_mi(self) -> bool:
        return self.stok is not None and self.stok.mevcut_adet > 0


class Stok(Base):
    __tablename__ = "stoklar"

    stok_id: Mapped[int] = mapped_column(primary_key=True)
    kitap_id: Mapped[int] = mapped_column(ForeignKey("kitaplar.kitap_id"), unique=True)
    toplam_adet: Mapped[int]
    mevcut_adet: Mapped[int]

    kitap: Mapped[Kitap] = relationship(back_populates="stok")

    def __init__(self, toplam_adet: int, **kw):
        if toplam_adet < 1:
            raise IsKuraliHatasi("Stok adedi en az 1 olmalı.")
        super().__init__(toplam_adet=toplam_adet, mevcut_adet=toplam_adet, **kw)

    def azalt(self) -> None:
        if self.mevcut_adet <= 0:
            raise IsKuraliHatasi("Bu kitabın rafta kopyası kalmadı.")
        self.mevcut_adet -= 1

    def arttir(self) -> None:
        if self.mevcut_adet >= self.toplam_adet:
            raise IsKuraliHatasi("Mevcut adet toplam adedi aşamaz.")
        self.mevcut_adet += 1
