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
