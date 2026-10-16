# Online Kütüphane Yönetim Sistemi — VS Code Kurulum ve Kod Rehberi

Bu dosya projeyi sıfırdan kurman için referanstır. Önce klasör yapısını oluştur, sonra
bölüm 5'teki her dosyayı aynı yola, aynı adla kopyala ve bölüm 3'teki komutlarla çalıştır.

**Teknolojiler:** Python (FastAPI + SQLAlchemy) · React (Vite) · PostgreSQL (Docker)

---

## 1. Gerekenler

| Araç | Kontrol komutu | Not |
|------|----------------|-----|
| Python 3.11+ | `python --version` | Windows'ta kurulumda "Add to PATH" işaretli olsun |
| Node.js 18+ | `node -v` | npm ile birlikte gelir |
| Docker Desktop | `docker --version` | PostgreSQL için. Yoksa bölüm 3.2'deki SQLite yolunu kullan |
| VS Code eklentileri | — | Python, ES7+ React snippets (isteğe bağlı), PlantUML (diyagramlar için) |

---

## 2. Klasör yapısı

```
kutuphane-projesi/
├── docker-compose.yml          ← PostgreSQL
├── backend/                    ← API (Python)
│   ├── requirements.txt
│   ├── pytest.ini
│   ├── app/
│   │   ├── __init__.py         (boş)
│   │   ├── main.py             ← uygulamanın giriş noktası
│   │   ├── database.py         ← veritabanı bağlantısı
│   │   ├── ayarlar.py          ← iş kuralı sabitleri (14 gün, max 3 kitap)
│   │   ├── hatalar.py          ← özel hata sınıfları
│   │   ├── semalar.py          ← API giriş/çıkış şemaları
│   │   ├── api.py              ← REST uç noktaları
│   │   ├── ornek_veri.py       ← başlangıç verisi
│   │   ├── uyelik/             ← PAKET: Uye, Yonetici
│   │   │   ├── __init__.py     (boş)
│   │   │   └── models.py
│   │   ├── katalog/            ← PAKET: Kitap, Stok
│   │   │   ├── __init__.py     (boş)
│   │   │   ├── models.py
│   │   │   └── servis.py
│   │   ├── odunc_islemleri/    ← PAKET: Odunc
│   │   │   ├── __init__.py     (boş)
│   │   │   ├── models.py
│   │   │   └── servis.py
│   │   └── raporlama/          ← PAKET: GecikmeRaporu
│   │       ├── __init__.py     (boş)
│   │       └── rapor.py
│   └── tests/
│       ├── __init__.py         (boş)
│       └── test_api.py
└── frontend/                   ← Web arayüzü (React)
    ├── package.json
    ├── vite.config.js
    ├── index.html
    └── src/
        ├── main.jsx
        ├── App.jsx
        ├── api.js
        ├── style.css
        └── sayfalar/
            ├── Katalog.jsx
            ├── Oduncler.jsx
            └── Yonetim.jsx
```

UML ile eşleşme: `uyelik`, `katalog`, `odunc_islemleri`, `raporlama` klasörleri Package Diagram'daki
dört pakettir. Class Diagram'daki metotlar sınıfların içinde aynı adla yazılmıştır
(`Uye.odunc_al()`, `Odunc.iade_et()`, `Stok.azalt()`, `Yonetici.kitap_ekle()` …).
Deployment Diagram'daki üç katman da burada: tarayıcı → React (frontend) → FastAPI (backend) → PostgreSQL.

---

## 3. Çalıştırma

VS Code'da `kutuphane-projesi` klasörünü aç. Üç ayrı terminal kullanacaksın
(Terminal → New Terminal, sağ üstteki **+** ile yenisini açabilirsin).

### 3.1 Terminal 1 — Veritabanı (PostgreSQL)

```bash
docker compose up -d
```

Durdurmak için: `docker compose down` (veriler silinmez).

### 3.2 Terminal 2 — Backend (API)

```bash
cd backend
python -m venv .venv
```

Sanal ortamı etkinleştir:

| Sistem | Komut |
|--------|-------|
| Windows (PowerShell) | `.venv\Scripts\Activate.ps1` |
| Windows (cmd) | `.venv\Scripts\activate.bat` |
| macOS / Linux | `source .venv/bin/activate` |

> PowerShell "running scripts is disabled" hatası verirse bir kez şunu çalıştır:
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

Sonra:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

`http://localhost:8000/docs` adresinde tüm API uç noktalarını deneyebileceğin Swagger sayfası açılır.
İlk çalıştırmada tablolar ve örnek veriler otomatik oluşur.

**Docker yoksa (SQLite ile):** `uvicorn` komutundan önce ortam değişkenini ayarla:

| Sistem | Komut |
|--------|-------|
| PowerShell | `$env:DATABASE_URL="sqlite:///./kutuphane.db"` |
| cmd | `set DATABASE_URL=sqlite:///./kutuphane.db` |
| macOS / Linux | `export DATABASE_URL=sqlite:///./kutuphane.db` |

### 3.3 Terminal 3 — Frontend (React)

```bash
cd frontend
npm install
npm run dev
```

Tarayıcıda `http://localhost:5173` adresini aç.

### 3.4 Testler

Backend klasöründe, sanal ortam etkinken:

```bash
pytest
```

Testler PostgreSQL gerektirmez, geçici SQLite kullanır. Dokuz testin hepsi geçmeli.

---

## 4. Uygulamada ne yapılabiliyor

| Kim | Ekran | İşlem |
|-----|-------|-------|
| Öğrenci | Kitap ara | Başlık / yazar / ISBN ile arama, rafta kaç kopya olduğunu görme, ödünç alma |
| Öğrenci | Ödünçlerim | Elindeki kitaplar, son teslim tarihi, gecikme durumu, iade etme, geçmiş |
| Yönetici | Yönetim | Kitap ekleme (stok adediyle), gecikme raporu |

Üst çubuktaki "Oturum" listesinden öğrenci ya da yönetici seçerek rol değiştirirsin
(ders projesi olduğu için şifreli giriş yok).

**İş kuralları** (`app/ayarlar.py` dosyasından değiştirilebilir):

- Ödünç süresi 14 gün
- Bir öğrenci aynı anda en fazla 3 kitap tutabilir
- Aynı kitap aynı öğrencide iki kez olamaz
- Rafta kopya kalmadıysa ödünç verilmez
- Aynı ISBN ile ikinci kitap eklenemez

**Örnek veri:** Ali Yılmaz bugün "Suç ve Ceza"yı almış durumda (Object Diagram'daki senaryo).
Ayşe Demir ve Mehmet Kaya'nın gecikmiş birer kitabı var, yönetici raporunda görünürler.
Örnek veriyi sıfırlamak için: `docker compose down -v` ve `docker compose up -d`
(SQLite kullanıyorsan `backend/kutuphane.db` dosyasını sil).

### API uç noktaları

| Yöntem | Yol | Ne yapar |
|--------|-----|----------|
| GET | `/api/kitaplar?q=` | Kitap arar |
| POST | `/api/kitaplar` | Yönetici kitap ekler |
| POST | `/api/oduncler` | Öğrenci kitap ödünç alır |
| POST | `/api/oduncler/{id}/iade` | Kitabı iade eder |
| GET | `/api/uyeler/{id}/oduncler` | Öğrencinin ödünçleri |
| GET | `/api/raporlar/gecikme?yonetici_id=` | Gecikme raporu |
| GET | `/api/uyeler`, `/api/yoneticiler` | Kullanıcı listeleri |

---

## 5. Dosyalar

Her başlıktaki yol, dosyanın `kutuphane-projesi/` altındaki yeridir. Klasörler yoksa oluştur.
`__init__.py` dosyaları boştur, sadece oluşturman yeterli:
`app/`, `app/uyelik/`, `app/katalog/`, `app/odunc_islemleri/`, `app/raporlama/`, `tests/`.


### `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16
    container_name: kutuphane-db
    environment:
      POSTGRES_USER: kutuphane
      POSTGRES_PASSWORD: kutuphane
      POSTGRES_DB: kutuphane_db
    ports:
      - "5432:5432"
    volumes:
      - kutuphane_veri:/var/lib/postgresql/data

volumes:
  kutuphane_veri:
```

### `backend/requirements.txt`

```text
fastapi>=0.115
uvicorn[standard]>=0.30
sqlalchemy>=2.0,<3
psycopg[binary]>=3.2
pydantic>=2.7
pytest>=8
httpx>=0.27
```

### `backend/pytest.ini`

```ini
[pytest]
pythonpath = .
testpaths = tests
```

### `backend/app/main.py`

```python
"""Uygulamanın giriş noktası: uvicorn app.main:app"""
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import router
from app.database import Base, SessionLocal, engine
from app.hatalar import BulunamadiHatasi, IsKuraliHatasi
from app.katalog import models as _katalog_models  # noqa: F401
from app.odunc_islemleri import models as _odunc_models  # noqa: F401
from app.ornek_veri import ornek_veri_yukle
from app.uyelik import models as _uyelik_models  # noqa: F401


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    if os.getenv("ORNEK_VERI", "1") == "1":
        with SessionLocal() as db:
            ornek_veri_yukle(db)
    yield


app = FastAPI(title="Online Kütüphane API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(IsKuraliHatasi)
async def is_kurali_hatasi(_: Request, hata: IsKuraliHatasi):
    return JSONResponse(status_code=400, content={"detail": str(hata)})


@app.exception_handler(BulunamadiHatasi)
async def bulunamadi_hatasi(_: Request, hata: BulunamadiHatasi):
    return JSONResponse(status_code=404, content={"detail": str(hata)})


app.include_router(router)
```

### `backend/app/database.py`

```python
"""Veritabanı bağlantısı. DATABASE_URL ortam değişkeniyle değiştirilebilir."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg://kutuphane:kutuphane@localhost:5432/kutuphane_db",
)

_connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=_connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    """Tüm tablo sınıflarının ortak atası."""


def get_db():
    """Her istek için ayrı bir veritabanı oturumu açar ve sonunda kapatır."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### `backend/app/ayarlar.py`

```python
"""İş kuralı sabitleri ve tarih yardımcısı."""
from datetime import date

ODUNC_SURESI_GUN = 14
"""Bir kitap kaç gün ödünç tutulabilir."""

MAKS_AKTIF_ODUNC = 3
"""Bir üye aynı anda en fazla kaç kitap tutabilir."""


def bugun() -> date:
    """Bugünün tarihi. Testlerde sabit bir tarihle değiştirilebilsin diye ayrı fonksiyon."""
    return date.today()
```

### `backend/app/hatalar.py`

```python
"""Uygulamaya özel hata sınıfları."""


class IsKuraliHatasi(Exception):
    """Bir iş kuralı ihlal edildiğinde fırlatılır (ör. stokta kitap kalmadı). HTTP 400 döner."""


class BulunamadiHatasi(Exception):
    """Aranan kayıt yoksa fırlatılır. HTTP 404 döner."""
```

### `backend/app/uyelik/models.py`

```python
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
```

### `backend/app/katalog/models.py`

```python
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
```

### `backend/app/katalog/servis.py`

```python
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
```

### `backend/app/odunc_islemleri/models.py`

```python
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
```

### `backend/app/odunc_islemleri/servis.py`

```python
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
```

### `backend/app/raporlama/rapor.py`

```python
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
```

### `backend/app/semalar.py`

```python
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
```

### `backend/app/api.py`

```python
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
```

### `backend/app/ornek_veri.py`

```python
"""Veritabanı boşsa örnek üye, yönetici, kitap ve ödünç kayıtları ekler."""
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.ayarlar import bugun
from app.uyelik.models import Uye, Yonetici

KITAPLAR = [
    ("Suç ve Ceza", "Fyodor Dostoyevski", "9789750719387", 3),
    ("Kürk Mantolu Madonna", "Sabahattin Ali", "9789753638029", 4),
    ("Tutunamayanlar", "Oğuz Atay", "9789754700114", 2),
    ("Saatleri Ayarlama Enstitüsü", "Ahmet Hamdi Tanpınar", "9789754700701", 2),
    ("1984", "George Orwell", "9789750718533", 3),
    ("Temiz Kod", "Robert C. Martin", "9786055231183", 2),
    ("Tasarım Desenleri", "Gamma, Helm, Johnson, Vlissides", "9780201633610", 1),
    ("Veritabanı Sistemleri", "Ramez Elmasri", "9780133970777", 2),
]


def ornek_veri_yukle(db: Session) -> None:
    if db.scalar(select(Uye).limit(1)) is not None:
        return

    ali = Uye(ad="Ali Yılmaz", ogrenci_no="220101045", email="ali@ogr.edu.tr")
    ayse = Uye(ad="Ayşe Demir", ogrenci_no="220101078", email="ayse@ogr.edu.tr")
    mehmet = Uye(ad="Mehmet Kaya", ogrenci_no="230102011", email="mehmet@ogr.edu.tr")
    yonetici = Yonetici(ad="Zeynep Arslan (Kütüphane Görevlisi)")
    db.add_all([ali, ayse, mehmet, yonetici])

    kitaplar = [yonetici.kitap_ekle(*k) for k in KITAPLAR]
    db.add_all(kitaplar)
    db.flush()

    t = bugun()
    # Object Diagram'daki senaryo: Ali bugün "Suç ve Ceza"yı alıyor
    db.add(ali.odunc_al(kitaplar[0], t))
    # Gecikme raporunda görünsün diye geçmiş tarihli ödünçler
    db.add(ayse.odunc_al(kitaplar[4], t - timedelta(days=25)))
    db.add(mehmet.odunc_al(kitaplar[2], t - timedelta(days=18)))
    # İade edilmiş eski bir kayıt
    eski = ayse.odunc_al(kitaplar[1], t - timedelta(days=40))
    eski.iade_et(t - timedelta(days=30))
    db.add(eski)

    db.commit()
```

### `backend/tests/test_api.py`

```python
"""Uçtan uca API testleri. PostgreSQL gerekmez, geçici SQLite kullanır.

Çalıştırma (backend klasöründe):  pytest
"""
import os
import tempfile

_db = os.path.join(tempfile.mkdtemp(), "test.db")
os.environ["DATABASE_URL"] = f"sqlite:///{_db}"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.main import app  # noqa: E402


@pytest.fixture(scope="module")
def istemci():
    with TestClient(app) as c:
        yield c


def _uye(istemci, ad):
    return next(u for u in istemci.get("/api/uyeler").json() if u["ad"] == ad)


def _kitap(istemci, baslik):
    return istemci.get("/api/kitaplar", params={"q": baslik}).json()[0]


def test_saglik(istemci):
    assert istemci.get("/api/saglik").json() == {"durum": "ok"}


def test_kitap_arama(istemci):
    sonuc = istemci.get("/api/kitaplar", params={"q": "orwell"}).json()
    assert [k["baslik"] for k in sonuc] == ["1984"]


def test_ornek_veride_ali_suc_ve_ceza_almis(istemci):
    ali = _uye(istemci, "Ali Yılmaz")
    oduncler = istemci.get(f"/api/uyeler/{ali['uye_id']}/oduncler").json()
    assert oduncler[0]["kitap_basligi"] == "Suç ve Ceza"
    kitap = _kitap(istemci, "Suç ve Ceza")
    assert (kitap["toplam_adet"], kitap["mevcut_adet"]) == (3, 2)


def test_odunc_al_ve_iade_et_stogu_gunceller(istemci):
    mehmet = _uye(istemci, "Mehmet Kaya")
    kitap = _kitap(istemci, "Temiz Kod")
    once = kitap["mevcut_adet"]

    r = istemci.post("/api/oduncler", json={"uye_id": mehmet["uye_id"], "kitap_id": kitap["kitap_id"]})
    assert r.status_code == 201
    odunc = r.json()
    assert _kitap(istemci, "Temiz Kod")["mevcut_adet"] == once - 1

    r = istemci.post(f"/api/oduncler/{odunc['odunc_id']}/iade")
    assert r.status_code == 200 and r.json()["iade_tarihi"] is not None
    assert _kitap(istemci, "Temiz Kod")["mevcut_adet"] == once

    # İkinci iade reddedilir
    assert istemci.post(f"/api/oduncler/{odunc['odunc_id']}/iade").status_code == 400


def test_ayni_kitap_iki_kez_alinamaz(istemci):
    ali = _uye(istemci, "Ali Yılmaz")
    kitap = _kitap(istemci, "Suç ve Ceza")
    r = istemci.post("/api/oduncler", json={"uye_id": ali["uye_id"], "kitap_id": kitap["kitap_id"]})
    assert r.status_code == 400
    assert "zaten" in r.json()["detail"]


def test_stok_bitince_odunc_verilmez(istemci):
    kitap = _kitap(istemci, "Tasarım Desenleri")  # tek kopya
    ali, ayse = _uye(istemci, "Ali Yılmaz"), _uye(istemci, "Ayşe Demir")
    assert istemci.post("/api/oduncler", json={"uye_id": ali["uye_id"], "kitap_id": kitap["kitap_id"]}).status_code == 201
    r = istemci.post("/api/oduncler", json={"uye_id": ayse["uye_id"], "kitap_id": kitap["kitap_id"]})
    assert r.status_code == 400 and "kopyası" in r.json()["detail"]


def test_yonetici_kitap_ekler(istemci):
    yonetici = istemci.get("/api/yoneticiler").json()[0]
    yeni = {"yonetici_id": yonetici["yonetici_id"], "baslik": "Sefiller", "yazar": "Victor Hugo",
            "isbn": "9789750738609", "adet": 2}
    r = istemci.post("/api/kitaplar", json=yeni)
    assert r.status_code == 201 and r.json()["mevcut_adet"] == 2
    # Aynı ISBN tekrar eklenemez
    assert istemci.post("/api/kitaplar", json=yeni).status_code == 400


def test_yonetici_olmadan_kitap_eklenemez(istemci):
    r = istemci.post("/api/kitaplar", json={"yonetici_id": 999, "baslik": "X", "yazar": "Y",
                                            "isbn": "1234567890", "adet": 1})
    assert r.status_code == 404


def test_gecikme_raporu(istemci):
    yonetici = istemci.get("/api/yoneticiler").json()[0]
    rapor = istemci.get("/api/raporlar/gecikme", params={"yonetici_id": yonetici["yonetici_id"]}).json()
    basliklar = [s["kitap_basligi"] for s in rapor["satirlar"]]
    assert basliklar == ["1984", "Tutunamayanlar"]  # en çok geciken önce
    assert rapor["satirlar"][0]["gecikme_gunu"] == 11
```

### `frontend/package.json`

```json
{
  "name": "kutuphane-web",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.0"
  }
}
```

### `frontend/vite.config.js`

```javascript
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// Geliştirme sırasında /api isteklerini FastAPI'ye (8000) yönlendirir.
export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: { "/api": "http://localhost:8000" },
  },
});
```

### `frontend/index.html`

```html
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Online Kütüphane</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

### `frontend/src/main.jsx`

```jsx
import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App.jsx";
import "./style.css";

ReactDOM.createRoot(document.getElementById("root")).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

### `frontend/src/App.jsx`

```jsx
import { useEffect, useState } from "react";
import { api } from "./api.js";
import Katalog from "./sayfalar/Katalog.jsx";
import Oduncler from "./sayfalar/Oduncler.jsx";
import Yonetim from "./sayfalar/Yonetim.jsx";

// Basit "giriş": üst çubuktan öğrenci ya da yönetici seçilir.
export default function App() {
  const [uyeler, setUyeler] = useState([]);
  const [yoneticiler, setYoneticiler] = useState([]);
  const [kullanici, setKullanici] = useState(null); // { tur: "uye"|"yonetici", id, ad }
  const [sekme, setSekme] = useState("katalog");
  const [bildirim, setBildirim] = useState(null);
  const [baglantiHatasi, setBaglantiHatasi] = useState(false);

  useEffect(() => {
    Promise.all([api.uyeler(), api.yoneticiler()])
      .then(([u, y]) => {
        setUyeler(u);
        setYoneticiler(y);
        if (u.length) setKullanici({ tur: "uye", id: u[0].uye_id, ad: u[0].ad });
      })
      .catch(() => setBaglantiHatasi(true));
  }, []);

  const bildir = (mesaj, tur = "basari") => {
    setBildirim({ mesaj, tur });
    setTimeout(() => setBildirim(null), 3500);
  };

  const kullaniciSec = (deger) => {
    const [tur, id] = deger.split(":");
    const liste = tur === "uye" ? uyeler : yoneticiler;
    const k = liste.find((x) => String(tur === "uye" ? x.uye_id : x.yonetici_id) === id);
    setKullanici({ tur, id: Number(id), ad: k.ad });
    setSekme(tur === "uye" ? "katalog" : "yonetim");
  };

  if (baglantiHatasi) {
    return (
      <div className="bos-ekran">
        <h2>API'ye bağlanılamadı</h2>
        <p>Backend'in çalıştığından emin ol: <code>uvicorn app.main:app --reload</code></p>
      </div>
    );
  }
  if (!kullanici) return <div className="bos-ekran">Yükleniyor…</div>;

  const ogrenci = kullanici.tur === "uye";
  const sekmeler = ogrenci
    ? [["katalog", "Kitap ara"], ["oduncler", "Ödünçlerim"]]
    : [["yonetim", "Yönetim"], ["katalog", "Katalog"]];

  return (
    <div className="kapsayici">
      <header className="ust-cubuk">
        <div className="logo">📚 Online Kütüphane</div>
        <label className="kullanici-sec">
          <span>Oturum:</span>
          <select value={`${kullanici.tur}:${kullanici.id}`} onChange={(e) => kullaniciSec(e.target.value)}>
            <optgroup label="Öğrenciler">
              {uyeler.map((u) => (
                <option key={u.uye_id} value={`uye:${u.uye_id}`}>{u.ad} ({u.ogrenci_no})</option>
              ))}
            </optgroup>
            <optgroup label="Yöneticiler">
              {yoneticiler.map((y) => (
                <option key={y.yonetici_id} value={`yonetici:${y.yonetici_id}`}>{y.ad}</option>
              ))}
            </optgroup>
          </select>
        </label>
      </header>

      <nav className="sekmeler">
        {sekmeler.map(([anahtar, ad]) => (
          <button key={anahtar} className={sekme === anahtar ? "aktif" : ""} onClick={() => setSekme(anahtar)}>
            {ad}
          </button>
        ))}
      </nav>

      <main>
        {sekme === "katalog" && <Katalog kullanici={kullanici} bildir={bildir} />}
        {sekme === "oduncler" && ogrenci && <Oduncler uyeId={kullanici.id} bildir={bildir} />}
        {sekme === "yonetim" && !ogrenci && <Yonetim yoneticiId={kullanici.id} bildir={bildir} />}
      </main>

      {bildirim && <div className={`bildirim ${bildirim.tur}`}>{bildirim.mesaj}</div>}
    </div>
  );
}
```

### `frontend/src/api.js`

```javascript
// Backend ile konuşan tek yer. Hata olursa backend'in "detail" mesajını fırlatır.
async function istek(yol, secenekler = {}) {
  const yanit = await fetch(`/api${yol}`, {
    headers: { "Content-Type": "application/json" },
    ...secenekler,
  });
  const veri = await yanit.json().catch(() => ({}));
  if (!yanit.ok) {
    const detay = Array.isArray(veri.detail)
      ? "Lütfen alanları kontrol edin."
      : veri.detail || "Bir hata oluştu.";
    throw new Error(detay);
  }
  return veri;
}

export const api = {
  uyeler: () => istek("/uyeler"),
  yoneticiler: () => istek("/yoneticiler"),
  kitapAra: (q = "") => istek(`/kitaplar?q=${encodeURIComponent(q)}`),
  kitapEkle: (kitap) => istek("/kitaplar", { method: "POST", body: JSON.stringify(kitap) }),
  oduncAl: (uyeId, kitapId) =>
    istek("/oduncler", { method: "POST", body: JSON.stringify({ uye_id: uyeId, kitap_id: kitapId }) }),
  iadeEt: (oduncId) => istek(`/oduncler/${oduncId}/iade`, { method: "POST" }),
  uyeninOduncleri: (uyeId) => istek(`/uyeler/${uyeId}/oduncler`),
  gecikmeRaporu: (yoneticiId) => istek(`/raporlar/gecikme?yonetici_id=${yoneticiId}`),
};

export const tarihYaz = (t) => (t ? new Date(t).toLocaleDateString("tr-TR") : "—");
```

### `frontend/src/sayfalar/Katalog.jsx`

```jsx
import { useEffect, useState } from "react";
import { api } from "../api.js";

export default function Katalog({ kullanici, bildir }) {
  const [arama, setArama] = useState("");
  const [kitaplar, setKitaplar] = useState([]);
  const [yukleniyor, setYukleniyor] = useState(true);

  const yukle = (q = arama) => {
    setYukleniyor(true);
    api.kitapAra(q)
      .then(setKitaplar)
      .catch((e) => bildir(e.message, "hata"))
      .finally(() => setYukleniyor(false));
  };

  useEffect(() => {
    const zamanlayici = setTimeout(() => yukle(arama), 250);
    return () => clearTimeout(zamanlayici);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [arama]);

  const oduncAl = async (kitap) => {
    try {
      const odunc = await api.oduncAl(kullanici.id, kitap.kitap_id);
      bildir(`"${kitap.baslik}" alındı. Son teslim: ${new Date(odunc.son_teslim_tarihi).toLocaleDateString("tr-TR")}`);
      yukle();
    } catch (e) {
      bildir(e.message, "hata");
    }
  };

  return (
    <section>
      <input
        className="arama"
        placeholder="Başlık, yazar veya ISBN ile ara…"
        value={arama}
        onChange={(e) => setArama(e.target.value)}
        autoFocus
      />

      {!yukleniyor && kitaplar.length === 0 && <p className="soluk">Sonuç bulunamadı.</p>}

      <div className="kart-izgara">
        {kitaplar.map((k) => (
          <article key={k.kitap_id} className="kart">
            <h3>{k.baslik}</h3>
            <p className="yazar">{k.yazar}</p>
            <p className="isbn">ISBN {k.isbn}</p>
            <div className="kart-alt">
              <span className={`rozet ${k.musait ? "yesil" : "kirmizi"}`}>
                {k.mevcut_adet}/{k.toplam_adet} rafta
              </span>
              {kullanici.tur === "uye" && (
                <button disabled={!k.musait} onClick={() => oduncAl(k)}>
                  Ödünç al
                </button>
              )}
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}
```

### `frontend/src/sayfalar/Oduncler.jsx`

```jsx
import { useEffect, useState } from "react";
import { api, tarihYaz } from "../api.js";

export default function Oduncler({ uyeId, bildir }) {
  const [oduncler, setOduncler] = useState([]);

  const yukle = () => api.uyeninOduncleri(uyeId).then(setOduncler).catch((e) => bildir(e.message, "hata"));
  useEffect(() => { yukle(); }, [uyeId]); // eslint-disable-line react-hooks/exhaustive-deps

  const iadeEt = async (o) => {
    try {
      await api.iadeEt(o.odunc_id);
      bildir(`"${o.kitap_basligi}" iade edildi.`);
      yukle();
    } catch (e) {
      bildir(e.message, "hata");
    }
  };

  const aktif = oduncler.filter((o) => !o.iade_tarihi);
  const gecmis = oduncler.filter((o) => o.iade_tarihi);

  return (
    <section>
      <h2>Şu an bende olanlar ({aktif.length})</h2>
      {aktif.length === 0 ? (
        <p className="soluk">Elinde ödünç kitap yok.</p>
      ) : (
        <table>
          <thead>
            <tr><th>Kitap</th><th>Alış</th><th>Son teslim</th><th>Durum</th><th></th></tr>
          </thead>
          <tbody>
            {aktif.map((o) => (
              <tr key={o.odunc_id}>
                <td>{o.kitap_basligi}</td>
                <td>{tarihYaz(o.alis_tarihi)}</td>
                <td>{tarihYaz(o.son_teslim_tarihi)}</td>
                <td>
                  {o.gecikme_gunu > 0
                    ? <span className="rozet kirmizi">{o.gecikme_gunu} gün gecikti</span>
                    : <span className="rozet yesil">Süresi var</span>}
                </td>
                <td><button onClick={() => iadeEt(o)}>İade et</button></td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {gecmis.length > 0 && (
        <>
          <h2>Geçmiş</h2>
          <table>
            <thead>
              <tr><th>Kitap</th><th>Alış</th><th>İade</th><th>Gecikme</th></tr>
            </thead>
            <tbody>
              {gecmis.map((o) => (
                <tr key={o.odunc_id} className="soluk">
                  <td>{o.kitap_basligi}</td>
                  <td>{tarihYaz(o.alis_tarihi)}</td>
                  <td>{tarihYaz(o.iade_tarihi)}</td>
                  <td>{o.gecikme_gunu > 0 ? `${o.gecikme_gunu} gün` : "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}
    </section>
  );
}
```

### `frontend/src/sayfalar/Yonetim.jsx`

```jsx
import { useEffect, useState } from "react";
import { api, tarihYaz } from "../api.js";

const BOS_FORM = { baslik: "", yazar: "", isbn: "", adet: 1 };

export default function Yonetim({ yoneticiId, bildir }) {
  const [form, setForm] = useState(BOS_FORM);
  const [rapor, setRapor] = useState(null);
  const [gonderiliyor, setGonderiliyor] = useState(false);

  const raporYukle = () => api.gecikmeRaporu(yoneticiId).then(setRapor).catch((e) => bildir(e.message, "hata"));
  useEffect(() => { raporYukle(); }, [yoneticiId]); // eslint-disable-line react-hooks/exhaustive-deps

  const degistir = (alan) => (e) => setForm({ ...form, [alan]: e.target.value });

  const kitapEkle = async (e) => {
    e.preventDefault();
    setGonderiliyor(true);
    try {
      const kitap = await api.kitapEkle({ ...form, adet: Number(form.adet), yonetici_id: yoneticiId });
      bildir(`"${kitap.baslik}" kataloğa eklendi.`);
      setForm(BOS_FORM);
    } catch (err) {
      bildir(err.message, "hata");
    } finally {
      setGonderiliyor(false);
    }
  };

  return (
    <section className="yonetim">
      <div className="panel">
        <h2>Kitap ekle</h2>
        <form onSubmit={kitapEkle}>
          <label>Başlık<input required value={form.baslik} onChange={degistir("baslik")} /></label>
          <label>Yazar<input required value={form.yazar} onChange={degistir("yazar")} /></label>
          <label>ISBN<input required minLength={10} maxLength={20} value={form.isbn} onChange={degistir("isbn")} /></label>
          <label>Adet<input required type="number" min={1} max={100} value={form.adet} onChange={degistir("adet")} /></label>
          <button type="submit" disabled={gonderiliyor}>{gonderiliyor ? "Ekleniyor…" : "Ekle"}</button>
        </form>
      </div>

      <div className="panel genis">
        <div className="panel-baslik">
          <h2>Gecikme raporu</h2>
          <button className="ikincil" onClick={raporYukle}>Yenile</button>
        </div>
        {rapor && (
          <>
            <p className="soluk">
              {tarihYaz(rapor.olusturma_tarihi)} itibarıyla {rapor.toplam} geciken ödünç
            </p>
            {rapor.toplam > 0 && (
              <table>
                <thead>
                  <tr><th>Öğrenci</th><th>No</th><th>Kitap</th><th>Son teslim</th><th>Gecikme</th></tr>
                </thead>
                <tbody>
                  {rapor.satirlar.map((s) => (
                    <tr key={s.odunc_id}>
                      <td>{s.uye_adi}</td>
                      <td>{s.ogrenci_no}</td>
                      <td>{s.kitap_basligi}</td>
                      <td>{tarihYaz(s.son_teslim_tarihi)}</td>
                      <td><span className="rozet kirmizi">{s.gecikme_gunu} gün</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </>
        )}
      </div>
    </section>
  );
}
```

### `frontend/src/style.css`

```css
:root {
  --bg: #f6f4ef;
  --kart: #ffffff;
  --yazi: #2b2a27;
  --soluk: #7a776f;
  --cizgi: #e2ded4;
  --vurgu: #2f5d50;
  --vurgu-acik: #e3efe9;
  --kirmizi: #a33a2d;
  --kirmizi-acik: #f8e4e0;
  font-family: system-ui, -apple-system, "Segoe UI", Roboto, sans-serif;
  color: var(--yazi);
  background: var(--bg);
}

* { box-sizing: border-box; }
body { margin: 0; }
h2 { font-size: 1.1rem; margin: 1.5rem 0 0.75rem; }
h3 { font-size: 1rem; margin: 0 0 0.25rem; }
code { background: var(--cizgi); padding: 2px 6px; border-radius: 4px; }

.kapsayici { max-width: 1040px; margin: 0 auto; padding: 0 16px 48px; }

.ust-cubuk {
  display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 12px;
  padding: 20px 0; border-bottom: 1px solid var(--cizgi);
}
.logo { font-weight: 600; font-size: 1.25rem; color: var(--vurgu); }
.kullanici-sec { display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: var(--soluk); }

select, input {
  font: inherit; padding: 8px 10px; border: 1px solid var(--cizgi); border-radius: 8px; background: var(--kart);
}
button {
  font: inherit; padding: 8px 14px; border: none; border-radius: 8px; cursor: pointer;
  background: var(--vurgu); color: white;
}
button:disabled { background: var(--cizgi); color: var(--soluk); cursor: not-allowed; }
button.ikincil { background: var(--vurgu-acik); color: var(--vurgu); }

.sekmeler { display: flex; gap: 4px; margin: 16px 0 8px; }
.sekmeler button { background: transparent; color: var(--soluk); }
.sekmeler button.aktif { background: var(--vurgu-acik); color: var(--vurgu); font-weight: 600; }

.arama { width: 100%; padding: 12px 14px; font-size: 1rem; margin: 8px 0 16px; }

.kart-izgara { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; }
.kart {
  background: var(--kart); border: 1px solid var(--cizgi); border-radius: 12px; padding: 16px;
  display: flex; flex-direction: column;
}
.yazar { margin: 0; color: var(--soluk); }
.isbn { margin: 4px 0 12px; font-size: 0.8rem; color: var(--soluk); }
.kart-alt { margin-top: auto; display: flex; justify-content: space-between; align-items: center; }

.rozet { font-size: 0.8rem; padding: 3px 8px; border-radius: 999px; white-space: nowrap; }
.rozet.yesil { background: var(--vurgu-acik); color: var(--vurgu); }
.rozet.kirmizi { background: var(--kirmizi-acik); color: var(--kirmizi); }

table { width: 100%; border-collapse: collapse; background: var(--kart); border-radius: 12px; overflow: hidden; }
th, td { text-align: left; padding: 10px 12px; border-bottom: 1px solid var(--cizgi); font-size: 0.92rem; }
th { font-weight: 600; color: var(--soluk); font-size: 0.8rem; }
tr:last-child td { border-bottom: none; }

.soluk { color: var(--soluk); }

.yonetim { display: grid; grid-template-columns: 300px 1fr; gap: 16px; align-items: start; }
.panel { background: var(--kart); border: 1px solid var(--cizgi); border-radius: 12px; padding: 16px; }
.panel h2 { margin-top: 0; }
.panel table { border: 1px solid var(--cizgi); }
.panel-baslik { display: flex; justify-content: space-between; align-items: center; }
form { display: flex; flex-direction: column; gap: 10px; }
form label { display: flex; flex-direction: column; gap: 4px; font-size: 0.85rem; color: var(--soluk); }

.bildirim {
  position: fixed; bottom: 24px; left: 50%; transform: translateX(-50%);
  padding: 12px 18px; border-radius: 10px; box-shadow: 0 4px 16px rgba(0,0,0,.12); max-width: 90vw;
}
.bildirim.basari { background: var(--vurgu); color: white; }
.bildirim.hata { background: var(--kirmizi); color: white; }

.bos-ekran { max-width: 520px; margin: 20vh auto; text-align: center; color: var(--soluk); }

@media (max-width: 720px) {
  .yonetim { grid-template-columns: 1fr; }
  table { font-size: 0.85rem; }
  th, td { padding: 8px; }
}
```

---

## 6. Sık karşılaşılan sorunlar

| Sorun | Çözüm |
|-------|-------|
| Arayüzde "API'ye bağlanılamadı" | Backend terminalinde `uvicorn` çalışıyor mu kontrol et |
| `connection refused ... 5432` | Docker Desktop açık mı? `docker compose up -d` çalıştır ya da SQLite yolunu kullan |
| `ModuleNotFoundError: app` | `uvicorn` ve `pytest` komutlarını `backend` klasörünün içinden çalıştır |
| `pip` / `uvicorn` bulunamadı | Sanal ortam etkin değil; terminal satırının başında `(.venv)` görünmeli |
| 5432 portu dolu | Bilgisayarda başka bir PostgreSQL çalışıyor; onu durdur ya da compose'da `"5433:5432"` yapıp DATABASE_URL'deki portu 5433 yap |
