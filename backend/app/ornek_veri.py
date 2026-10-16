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
