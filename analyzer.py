"""
Science Paper Analyzer — центральный координатор
Работает как с Streamlit (веб), так и без него (Colab/консоль)
"""

import pandas as pd
import time
import sys
from datetime import datetime

# Streamlit — опциональный импорт (нужен только для веб-режима)
_has_streamlit = False
try:
    import streamlit as st
    _has_streamlit = True
except ImportError:
    # Создаём заглушку для Colab/консоли
    class _Stub:
        def progress(self, *a, **kw):
            return self
        def empty(self, *a, **kw):
            return self
        def warning(self, msg):
            print(f"[WARNING] {msg}")
        def text(self, msg):
            print(msg)
        def __getattr__(self, name):
            return lambda *a, **kw: None
    st = _Stub()

from parsers.arxiv_parser import ArxivParser
from parsers.semantic_scholar import SemanticScholarParser
from parsers.openreview_parser import OpenReviewParser
from parsers.aclanthology import ACLAnthologyParser
from parsers.jmlr_parser import JMLRParser
from parsers.crossref_fallback import CrossRefFallback
from parsers.cyberleninka import CyberLeninkaParser

from analyzers.citation_analyzer import CitationAnalyzer
from analyzers.text_analyzer import TextAnalyzer
from analyzers.journal_analyzer import JournalAnalyzer

from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter


SOURCE_DISPLAY = {
    "arxiv": "arXiv.org",
    "semantic_scholar": "Semantic Scholar",
    "openreview": "OpenReview.net",
    "aclanthology": "ACL Anthology",
    "jmlr": "JMLR.org",
    "researchgate": "ResearchGate (via CrossRef)",
    "cyberleninka": "CyberLeninka.ru",
    "elibrary": "eLibrary.ru (via CrossRef)",
    "dissercat": "Dissercat.com (via CrossRef)",
    "fips": "FIPS.ru (patent DB)"
}


class PaperAnalyzer:
    """Главный класс системы."""

    def __init__(self, verbose: bool = True):
        self.parsers = self._init_parsers()
        self.analyzers = self._init_analyzers()
        self.exporter_csv = CSVExporter()
        self.exporter_xlsx = ExcelExporter()
        self.verbose = verbose

    def _init_parsers(self):
        return {
            "arxiv": ArxivParser(),
            "semantic_scholar": SemanticScholarParser(),
            "openreview": OpenReviewParser(),
            "aclanthology": ACLAnthologyParser(),
            "jmlr": JMLRParser(),
            "researchgate": CrossRefFallback(source_name="ResearchGate"),
            "cyberleninka": CyberLeninkaParser(),
            "elibrary": CrossRefFallback(source_name="eLibrary"),
            "dissercat": CrossRefFallback(source_name="Dissercat"),
            "fips": CrossRefFallback(source_name="FIPS"),
        }

    def _init_analyzers(self):
        return {
            "citation": CitationAnalyzer(),
            "text": TextAnalyzer(),
            "journal": JournalAnalyzer(),
        }

    def _log(self, msg):
        if self.verbose:
            print(msg)

    def collect_papers(self, query: str, max_per_source: int = 5):
        """Сбор статей из всех источников по запросу."""
        all_papers = []

        if _has_streamlit:
            progress_bar = st.progress(0)
            status_text = st.empty()
        else:
            progress_bar = None

        sources = list(self.parsers.items())
        for idx, (source_key, parser) in enumerate(sources):
            src_name = SOURCE_DISPLAY.get(source_key, source_key)
            self._log(f"[{idx+1}/{len(sources)}] Парсинг: {src_name}...")

            if progress_bar is not None:
                status_text.text(f"Парсинг: {src_name}...")

            try:
                papers = parser.search(query, max_results=max_per_source)
                for p in papers:
                    p["source"] = source_key
                    p["source_display"] = SOURCE_DISPLAY.get(source_key, source_key)
                    if "id" not in p or not p["id"]:
                        p["id"] = f"{source_key}_{hash(p.get('title', '')) % 100000}"
                all_papers.extend(papers)
                self._log(f"  -> Найдено: {len(papers)} статей")
                time.sleep(0.3)
            except Exception as e:
                msg = f"{src_name}: {str(e)[:100]}"
                if _has_streamlit:
                    st.warning(f"WARNING: {msg}")
                else:
                    self._log(f"  [WARNING] {msg}")

            if progress_bar is not None:
                progress_bar.progress((idx + 1) / len(sources))

        if progress_bar is not None:
            progress_bar.empty()

        # Дедупликация: удаляем статьи с одинаковым title (регистронезависимо)
        seen = set()
        unique_papers = []
        for p in all_papers:
            key = p.get("title", "").strip().lower()[:100]
            if key and key not in seen:
                seen.add(key)
                unique_papers.append(p)

        dupes = len(all_papers) - len(unique_papers)
        if dupes:
            self._log(f"Удалено дублей: {dupes}")

        self._log(f"\nСобрано {len(unique_papers)} уникальных статей из всех источников")
        return unique_papers

    def analyze_papers(self, papers: list) -> pd.DataFrame:
        """Анализ всех собранных статей."""
        results = []

        if _has_streamlit:
            progress_bar = st.progress(0)
            status_text = st.empty()
        else:
            progress_bar = None

        for idx, paper in enumerate(papers):
            title_short = paper.get("title", "N/A")[:50]
            self._log(f"[{idx+1}/{len(papers)}] Анализ: {title_short}...")

            if progress_bar is not None:
                status_text.text(f"Анализ статьи {idx+1}/{len(papers)}: {title_short}...")

            citation_score, citation_detail = self.analyzers["citation"].analyze(paper)
            text_score, text_detail = self.analyzers["text"].analyze(paper)
            journal_score, journal_detail = self.analyzers["journal"].analyze(paper)

            scores = [citation_score, text_score, journal_score]
            avg_score = sum(scores) / len(scores)

            if avg_score >= 0.7:
                verdict = "Real"
            elif avg_score >= 0.4:
                verdict = "Suspicious"
            else:
                verdict = "Fake"

            results.append({
                "id": paper.get("id", "N/A"),
                "title": paper.get("title", "N/A"),
                "authors": paper.get("authors", "N/A"),
                "year": paper.get("year", "N/A"),
                "source": paper.get("source_display", paper.get("source", "N/A")),
                "url": paper.get("url", "N/A"),
                "abstract": (paper.get("abstract", "") or "")[:200],
                "citation_score": round(citation_score, 2),
                "text_score": round(text_score, 2),
                "journal_score": round(journal_score, 2),
                "overall_score": round(avg_score, 2),
                "verdict": verdict,
                "citation_detail": citation_detail,
                "text_detail": text_detail,
                "journal_detail": journal_detail,
            })

            if progress_bar is not None:
                progress_bar.progress((idx + 1) / len(papers))

        if progress_bar is not None:
            progress_bar.empty()

        self._log(f"Проанализировано {len(results)} статей")
        return pd.DataFrame(results)

    def export_csv(self, df: pd.DataFrame, filepath: str):
        """Экспорт в CSV."""
        self.exporter_csv.export(df, filepath)
        self._log(f"CSV сохранён: {filepath}")

    def export_excel(self, df: pd.DataFrame, filepath: str):
        """Экспорт в Excel с форматированием."""
        self.exporter_xlsx.export(df, filepath)
        self._log(f"Excel сохранён: {filepath}")