# Online Kütüphane Yönetim Sistemi

Öğrencilerin kitap arayıp ödünç alabildiği, yöneticinin kitap ekleyip gecikmeleri takip edebildiği
bir web uygulaması. Ders projesi olarak UML diyagramlarına (Class, Package, Object, Deployment)
birebir uyacak şekilde tasarlanmıştır.

**Teknolojiler:** Python (FastAPI + SQLAlchemy) · React (Vite) · PostgreSQL (Docker)

## Özellikler

| Rol | Yapabildikleri |
|-----|----------------|
| Öğrenci | Başlık / yazar / ISBN ile kitap arama, raftaki kopya sayısını görme, ödünç alma, iade etme, ödünç geçmişi |
| Yönetici | Stok adediyle kitap ekleme, gecikme raporu |

## Ekran görüntüleri

**Kitap arama (öğrenci):** Rafta kaç kopya kaldığı görünür, kopya kalmadıysa ödünç alma düğmesi kapanır.

![Kitap arama ekranı](docs/ekran-goruntuleri/katalog.png)

**Ödünçlerim (öğrenci):** Elindeki kitaplar, son teslim tarihi, gecikme durumu ve geçmiş.

![Ödünçlerim ekranı](docs/ekran-goruntuleri/oduncler.png)

**Yönetim (yönetici):** Kitap ekleme formu ve en çok gecikenden başlayan gecikme raporu.

![Yönetim ekranı](docs/ekran-goruntuleri/yonetim.png)

**İş kuralları** ([backend/app/ayarlar.py](backend/app/ayarlar.py) dosyasından değiştirilebilir):

- Ödünç süresi 14 gündür.
- Bir öğrenci aynı anda en fazla 3 kitap tutabilir.
- Aynı kitap aynı öğrencide iki kez olamaz.
- Rafta kopya kalmadıysa ödünç verilmez.
- Aynı ISBN ile ikinci kitap eklenemez.

## Hızlı başlangıç

Gerekenler: Python 3.11+, Node.js 18+, Docker Desktop.

```bash
# 1. Veritabanı (proje kök klasöründe)
docker compose up -d

# 2. Backend (yeni terminalde)
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1        # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# 3. Frontend (yeni terminalde)
cd frontend
npm install
npm run dev
```

- Uygulama: http://localhost:5173
- API dokümantasyonu (Swagger): http://localhost:8000/docs

İlk çalıştırmada tablolar ve örnek veriler (3 öğrenci, 1 yönetici, 8 kitap) otomatik oluşur.
Üst çubuktaki **Oturum** listesinden öğrenci ya da yönetici seçerek rol değiştirebilirsin.
Ders projesi olduğu için şifreli giriş yoktur.

Docker olmadan çalıştırmak, sık karşılaşılan hatalar ve tüm dosyaların açıklaması için
[KURULUM_REHBERI.md](KURULUM_REHBERI.md) dosyasına bak.

## Testler

```bash
cd backend
pytest
```

Testler geçici bir SQLite veritabanı kullanır, PostgreSQL gerektirmez.

## Proje yapısı

```
├── docker-compose.yml        PostgreSQL
├── backend/
│   ├── app/
│   │   ├── main.py           Uygulamanın giriş noktası
│   │   ├── api.py            REST uç noktaları
│   │   ├── uyelik/           Paket: Uye, Yonetici
│   │   ├── katalog/          Paket: Kitap, Stok
│   │   ├── odunc_islemleri/  Paket: Odunc
│   │   └── raporlama/        Paket: GecikmeRaporu
│   └── tests/
└── frontend/
    └── src/
        ├── App.jsx
        └── sayfalar/         Katalog, Ödünçlerim, Yönetim ekranları
```

`uyelik`, `katalog`, `odunc_islemleri` ve `raporlama` klasörleri Package Diagram'daki dört pakete karşılık gelir.
Class Diagram'daki metotlar sınıfların içinde aynı adla yazılmıştır
(`Uye.odunc_al()`, `Odunc.iade_et()`, `Stok.azalt()`, `Yonetici.kitap_ekle()` …).

## UML diyagramları

Aşağıdaki diyagramlar koddan çıkarılmıştır; sınıf, metot ve paket adları koddakilerle aynıdır.

### Class Diagram

```mermaid
classDiagram
    direction LR

    class Uye {
        +int uye_id
        +str ad
        +str ogrenci_no
        +str email
        +aktif_oduncler() list~Odunc~
        +kitap_ara(katalog, anahtar) list~Kitap~
        +odunc_al(kitap, tarih) Odunc
    }
    class Yonetici {
        +int yonetici_id
        +str ad
        +kitap_ekle(baslik, yazar, isbn, adet) Kitap
        +gecikme_raporu_al(oduncler, tarih) GecikmeRaporu
    }
    class Kitap {
        +int kitap_id
        +str baslik
        +str yazar
        +str isbn
        +musait_mi() bool
    }
    class Stok {
        +int stok_id
        +int toplam_adet
        +int mevcut_adet
        +azalt()
        +arttir()
    }
    class Odunc {
        +int odunc_id
        +date alis_tarihi
        +date son_teslim_tarihi
        +date iade_tarihi
        +iade_et(tarih)
        +gecikme_gunu(tarih) int
        +gecikmis_mi(tarih) bool
    }
    class GecikmeRaporu {
        +date olusturma_tarihi
        +list~GecikmeSatiri~ satirlar
        +olustur(oduncler)
        +toplam() int
    }

    Uye "1" -- "0..*" Odunc : yapar
    Odunc "0..*" -- "1" Kitap : konu
    Kitap "1" *-- "1" Stok : sahip
    Yonetici "1" -- "0..*" Kitap : ekler
    Yonetici ..> GecikmeRaporu : oluşturur
    GecikmeRaporu o-- "0..*" Odunc : listeler
```

- **Odunc**, Uye ile Kitap arasındaki ilişki sınıfıdır. Ödünç tarihi, son teslim tarihi ve iade tarihi burada tutulur.
- **Kitap ◆— Stok** bir composition ilişkisidir: kitap silinirse stoğu da silinir.
- **GecikmeRaporu ◇— Odunc** bir aggregation ilişkisidir: rapor ödünçleri listeler ama onlara sahip değildir ve veritabanında saklanmaz.

### Package Diagram

```mermaid
flowchart LR
    subgraph app["app"]
        uyelik["uyelik<br/><small>Uye, Yonetici</small>"]
        katalog["katalog<br/><small>Kitap, Stok, Katalog</small>"]
        odunc["odunc_islemleri<br/><small>Odunc, OduncServisi</small>"]
        rapor["raporlama<br/><small>GecikmeRaporu</small>"]
    end

    uyelik -. import .-> katalog
    uyelik -. import .-> odunc
    uyelik -. import .-> rapor
    odunc -. import .-> katalog
    odunc -. import .-> uyelik
    rapor -. import .-> odunc
```

### Object Diagram

Örnek verideki senaryo: Ali Yılmaz, 3 kopyası olan "Suç ve Ceza"yı bugün ödünç alıyor.

```mermaid
flowchart LR
    ali["<u>ali : Uye</u><br/>ad = Ali Yılmaz<br/>ogrenci_no = 220101045"]
    o1["<u>o1 : Odunc</u><br/>alis_tarihi = bugün<br/>son_teslim_tarihi = bugün + 14 gün<br/>iade_tarihi = null"]
    kitap["<u>sucVeCeza : Kitap</u><br/>baslik = Suç ve Ceza<br/>yazar = Fyodor Dostoyevski"]
    stok["<u>stok1 : Stok</u><br/>toplam_adet = 3<br/>mevcut_adet = 2"]

    ali --- o1
    o1 --- kitap
    kitap --- stok
```

### Deployment Diagram

```mermaid
flowchart LR
    subgraph istemci["Kullanıcı bilgisayarı"]
        tarayici["Web tarayıcısı"]
    end
    subgraph sunucu["Sunucu"]
        react["Frontend<br/>React + Vite<br/>:5173"]
        api["Backend<br/>FastAPI + Uvicorn<br/>:8000"]
        subgraph docker["Docker"]
            db[("PostgreSQL 16<br/>:5432")]
        end
    end

    tarayici -- HTTP --> react
    react -- "REST /api (JSON)" --> api
    api -- "SQLAlchemy / psycopg" --> db
```

## API uç noktaları

| Yöntem | Yol | Ne yapar |
|--------|-----|----------|
| GET | `/api/kitaplar?q=` | Kitap arar |
| POST | `/api/kitaplar` | Yönetici kitap ekler |
| POST | `/api/oduncler` | Öğrenci kitap ödünç alır |
| POST | `/api/oduncler/{id}/iade` | Kitabı iade eder |
| GET | `/api/uyeler/{id}/oduncler` | Öğrencinin ödünçleri |
| GET | `/api/raporlar/gecikme?yonetici_id=` | Gecikme raporu |
| GET | `/api/uyeler`, `/api/yoneticiler` | Kullanıcı listeleri |
