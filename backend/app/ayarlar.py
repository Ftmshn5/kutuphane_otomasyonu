"""İş kuralı sabitleri ve tarih yardımcısı."""
from datetime import date

ODUNC_SURESI_GUN = 14
"""Bir kitap kaç gün ödünç tutulabilir."""

MAKS_AKTIF_ODUNC = 3
"""Bir üye aynı anda en fazla kaç kitap tutabilir."""


def bugun() -> date:
    """Bugünün tarihi. Testlerde sabit bir tarihle değiştirilebilsin diye ayrı fonksiyon."""
    return date.today()
