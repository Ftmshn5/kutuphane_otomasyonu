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
