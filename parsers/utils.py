"""
Вспомогательные функции для парсеров
"""

import re
from datetime import datetime, timezone


def extract_year(value) -> str:
    """
    Извлекает корректный год из любых данных.
    Поддерживает:
    - int/float год (2023.0 → "2023")
    - строки вида "2023", "2023-01-15", "2023 год"
    - timestamp в секундах (1672531200)
    - timestamp в миллисекундах (1672531200000)
    Возвращает "" если определить не удалось.
    """
    if value is None or value == "":
        return ""

    # Если число — проверяем границы
    if isinstance(value, (int, float)):
        if 1900 <= value <= 2050:
            return str(int(value))
        # Если большое число — это timestamp (мс или сек)
        if value > 10**9:  # секунды (10 цифр) или миллисекунды (13 цифр)
            if value > 10**12:
                value = value / 1000
            try:
                return str(datetime.fromtimestamp(value, tz=timezone.utc).year)
            except (ValueError, OSError, OverflowError):
                return ""
        return ""

    # Строка
    s = str(value).strip()

    # Ищем 4 цифры, образующие год (1900-2050)
    match = re.search(r'\b(19[0-9][0-9]|20[0-9][0-9])\b', s)
    if match:
        return match.group(1)

    return ""