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
