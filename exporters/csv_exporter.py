"""
CSV Exporter — экспорт результатов в CSV
"""

import csv
import pandas as pd
from typing import List, Dict


class CSVExporter:
    def export(self, df: pd.DataFrame, filepath: str):
        """Экспорт в CSV файл."""
        # Отбираем только основные колонки для CSV
        export_cols = [
            "title", "authors", "year", "source", "url",
            "citation_score", "text_score", "journal_score",
            "overall_score", "verdict"
        ]
        export_cols = [c for c in export_cols if c in df.columns]

        df_export = df[export_cols].copy()
        df_export.to_csv(filepath, index=False, encoding="utf-8-sig")
        return filepath