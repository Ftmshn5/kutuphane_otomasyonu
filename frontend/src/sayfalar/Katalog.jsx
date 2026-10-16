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
