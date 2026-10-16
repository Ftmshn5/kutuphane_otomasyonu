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
