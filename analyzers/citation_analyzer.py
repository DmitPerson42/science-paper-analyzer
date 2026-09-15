"""
Citation Analyzer — анализ цитируемости статьи
Использует данные из Semantic Scholar или CrossRef
"""

from typing import Tuple


class CitationAnalyzer:
    def analyze(self, paper: dict) -> Tuple[float, str]:
        """
        Оценка на основе цитируемости.
        Возвращает (score, detail):
            score 0.0–1.0 (выше = более реальная)
        """
        citation_count = paper.get("citation_count", None)

        # Пробуем получить citation_count из разных полей
        if citation_count is None:
            citation_count = paper.get("citations", None)
        if citation_count is None:
            citation_count = paper.get("cited_by_count", None)

        year_str = paper.get("year", "")
        try:
            year = int(year_str) if year_str and year_str.isdigit() else None
        except (ValueError, TypeError):
            year = None

        # Если нет данных о цитированиях
        if citation_count is None:
            # Пытаемся определить через Semantic Scholar повторно
            # (в реальном коде здесь был бы повторный запрос)
            return 0.5, "Нет данных о цитированиях — оценка нейтральная"

        citation_count = int(citation_count)

        # Логика:
        # old paper (>=3 года) с 0 цит. → подозрительно
        # new paper (<3 года) с 0 цит. → нормально
        # 1-5 цит. → нормально
        # >=5 цит. → доверенный

        import datetime
        current_year = datetime.datetime.now().year

        if year and (current_year - year) >= 3 and citation_count == 0:
            return 0.2, f"Статья {year} года, {citation_count} цитирований — подозрительно (возраст >3 лет, 0 цит.)"
        elif citation_count == 0:
            return 0.5, f"Статья {year if year else 'N/A'} года, {citation_count} цитирований — нейтрально (молодая статья)"
        elif citation_count <= 5:
            return 0.7, f"{citation_count} цитирований — приемлемый уровень"
        elif citation_count <= 15:
            return 0.85, f"{citation_count} цитирований — хороший уровень"
        else:
            return 0.95, f"{citation_count} цитирований — высокий уровень доверия"