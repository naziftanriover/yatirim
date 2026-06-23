"""Risk kurallarının SAYILARI burada durur (tek doğru kaynak).

Bu değerleri değiştirmek istersen sadece burayı düzenlersin; kod değişmez.
Para/oran değerleri Decimal tutulur (yuvarlama hatasını önlemek için).
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class RiskAyarlari:
    """Kullanıcının risk sınırları. frozen=True => yanlışlıkla değiştirilemez."""

    # Tek işleme koyabileceğin kendi parana (teminat) sınır: ana paranın yüzdesi.
    max_teminat_yuzde: Decimal = Decimal("20")

    # İzin verilen en yüksek kaldıraç oranı (5 => 5x). 1 => kaldıraç yok.
    max_kaldirac: Decimal = Decimal("5")

    # Tek bir normal (kaldıraçsız) işleme ayrılabilecek azami pay: ana paranın yüzdesi.
    max_pozisyon_yuzde: Decimal = Decimal("2")

    # Aynı anda AÇIK tüm işlemlerin toplam riski, ana paranın bu yüzdesini geçemez.
    # Örn. 6 => açık işlemlerin toplam zarar potansiyeli ana paranın %6'sını aşamaz.
    max_toplam_risk_yuzde: Decimal = Decimal("6")


# Programın her yerinden kullanılacak varsayılan ayar nesnesi.
VARSAYILAN = RiskAyarlari()
