"""
Excel Exporter — экспорт результатов в XLSX с форматированием
"""

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils.dataframe import dataframe_to_rows


class ExcelExporter:
    def export(self, df: pd.DataFrame, filepath: str):
        """Экспорт в Excel с условным форматированием."""
        wb = Workbook()
        ws = wb.active
        ws.title = "Results"

        # Отбираем колонки
        export_cols = [
            "title", "authors", "year", "source", "url",
            "citation_score", "text_score", "journal_score",
            "overall_score", "verdict",
            "citation_detail", "text_detail", "journal_detail",
        ]
        export_cols = [c for c in export_cols if c in df.columns]
        df_export = df[export_cols].copy()

        # Записываем данные
        for r_idx, row in enumerate(dataframe_to_rows(df_export, index=False, header=True)):
            ws.append(list(row))

        # Стили
        header_fill = PatternFill(start_color="1F4E79", end_color="1F4E79", fill_type="solid")
        header_font = Font(color="FFFFFF", bold=True, size=11)
        thin_border = Border(
            left=Side(style="thin"),
            right=Side(style="thin"),
            top=Side(style="thin"),
            bottom=Side(style="thin"),
        )

        green_fill = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")
        yellow_fill = PatternFill(start_color="FFEB9C", end_color="FFEB9C", fill_type="solid")
        red_fill = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")

        # Форматирование заголовков
        for cell in ws[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            cell.border = thin_border

        # Условное форматирование для колонки "verdict" (предполагаем индекс 8)
        verdict_col = None
        for idx, col_name in enumerate(export_cols):
            if col_name == "verdict":
                verdict_col = idx + 1  # 1-based for openpyxl
                break

        if verdict_col:
            for row in ws.iter_rows(min_row=2, min_col=verdict_col, max_col=verdict_col):
                for cell in row:
                    if cell.value and "Real" in str(cell.value):
                        cell.fill = green_fill
                    elif cell.value and "Suspicious" in str(cell.value):
                        cell.fill = yellow_fill
                    elif cell.value and "Fake" in str(cell.value):
                        cell.fill = red_fill
                    cell.border = thin_border
                    cell.alignment = Alignment(horizontal="center")

        # Ширина колонок
        ws.column_dimensions["A"].width = 60  # title
        ws.column_dimensions["B"].width = 40  # authors
        ws.column_dimensions["C"].width = 10  # year
        ws.column_dimensions["D"].width = 20  # source
        ws.column_dimensions["E"].width = 40  # url

        wb.save(filepath)
        return filepath