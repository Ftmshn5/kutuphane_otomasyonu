"""Katalog servisi: kitapları arar ve getirir."""
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.hatalar import BulunamadiHatasi
from app.katalog.models import Kitap


class Katalog:
    def __init__(self, db: Session):
        self.db = db

    def ara(self, anahtar: str = "") -> list[Kitap]:
        sorgu = select(Kitap).order_by(Kitap.baslik)
        anahtar = anahtar.strip()
        if anahtar:
            desen = f"%{anahtar}%"
            sorgu = sorgu.where(
                or_(Kitap.baslik.ilike(desen), Kitap.yazar.ilike(desen), Kitap.isbn.ilike(desen))
            )
        return list(self.db.scalars(sorgu))

    def getir(self, kitap_id: int) -> Kitap:
        kitap = self.db.get(Kitap, kitap_id)
        if kitap is None:
            raise BulunamadiHatasi(f"{kitap_id} numaralı kitap bulunamadı.")
        return kitap

    def isbn_var_mi(self, isbn: str) -> bool:
        return self.db.scalar(select(Kitap).where(Kitap.isbn == isbn)) is not None
