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
