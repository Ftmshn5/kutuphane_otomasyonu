"""API'nin giriş/çıkış veri şemaları (Pydantic)."""
from datetime import date

from pydantic import BaseModel, ConfigDict, Field


class _OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class UyeCikti(_OrmModel):
    uye_id: int
    ad: str
    ogrenci_no: str
    email: str


class YoneticiCikti(_OrmModel):
    yonetici_id: int
    ad: str


class KitapCikti(BaseModel):
    kitap_id: int
    baslik: str
    yazar: str
    isbn: str
    toplam_adet: int
    mevcut_adet: int
    musait: bool


class KitapEkleGirdi(BaseModel):
    yonetici_id: int
    baslik: str = Field(min_length=1, max_length=200)
    yazar: str = Field(min_length=1, max_length=120)
    isbn: str = Field(min_length=10, max_length=20)
    adet: int = Field(ge=1, le=100)


class OduncAlGirdi(BaseModel):
    uye_id: int
    kitap_id: int


class OduncCikti(BaseModel):
    odunc_id: int
    uye_id: int
    kitap_id: int
    kitap_basligi: str
    alis_tarihi: date
    son_teslim_tarihi: date
    iade_tarihi: date | None
    gecikme_gunu: int


class GecikmeSatiriCikti(_OrmModel):
    odunc_id: int
    uye_adi: str
    ogrenci_no: str
    kitap_basligi: str
    son_teslim_tarihi: date
    gecikme_gunu: int


class GecikmeRaporuCikti(_OrmModel):
    olusturma_tarihi: date
    toplam: int
    satirlar: list[GecikmeSatiriCikti]
