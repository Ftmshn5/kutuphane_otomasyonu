"""Uygulamaya özel hata sınıfları."""


class IsKuraliHatasi(Exception):
    """Bir iş kuralı ihlal edildiğinde fırlatılır (ör. stokta kitap kalmadı). HTTP 400 döner."""


class BulunamadiHatasi(Exception):
    """Aranan kayıt yoksa fırlatılır. HTTP 404 döner."""
