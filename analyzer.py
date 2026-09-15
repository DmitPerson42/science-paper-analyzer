"""
Science Paper Analyzer — центральный координатор
Осуществляет парсинг, анализ и экспорт результатов
"""

import pandas as pd
import time
import streamlit as st
from datetime import datetime

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

    def __init__(self):
        self.parsers = self._init_parsers()
        self.analyzers = self._init_analyzers()
        self.exporter_csv = CSVExporter()
        self.exporter_xlsx = ExcelExporter()

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

    def collect_papers(self, query: str, max_per_source: int = 5):
        """Сбор статей из всех источников по запросу."""
        all_papers = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        sources = list(self.parsers.items())
        for idx, (source_key, parser) in enumerate(sources):
            status_text.text(f"📡 Парсинг: {SOURCE_DISPLAY.get(source_key, source_key)}...")
            try:
                papers = parser.search(query, max_results=max_per_source)
                for p in papers:
                    p["source"] = source_key
                    p["source_display"] = SOURCE_DISPLAY.get(source_key, source_key)
                    if "id" not in p or not p["id"]:
                        p["id"] = f"{source_key}_{hash(p.get('title', '')) % 100000}"
                all_papers.extend(papers)
                time.sleep(0.5)  # вежливая задержка
            except Exception as e:
                st.warning(f"⚠️ {SOURCE_DISPLAY.get(source_key, source_key)}: {str(e)[:100]}")
            progress_bar.progress((idx + 1) / len(sources))

        progress_bar.empty()
        status_text.text(f"✅ Собрано {len(all_papers)} статей из всех источников")
        return all_papers

    def analyze_papers(self, papers: list) -> pd.DataFrame:
        """Анализ всех собранных статей."""
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, paper in enumerate(papers):
            status_text.text(f"🔬 Анализ статьи {idx+1}/{len(papers)}: {paper.get('title', 'N/A')[:50]}...")

            citation_score, citation_detail = self.analyzers["citation"].analyze(paper)
            text_score, text_detail = self.analyzers["text"].analyze(paper)
            journal_score, journal_detail = self.analyzers["journal"].analyze(paper)

            scores = [citation_score, text_score, journal_score]
            avg_score = sum(scores) / len(scores)

            if avg_score >= 0.7:
                verdict = "Real ✅"
            elif avg_score >= 0.4:
                verdict = "Suspicious ⚠️"
            else:
                verdict = "Fake ❌"

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

            progress_bar.progress((idx + 1) / len(papers))

        progress_bar.empty()
        status_text.text(f"✅ Проанализировано {len(results)} статей")
        return pd.DataFrame(results)

    def export_csv(self, df: pd.DataFrame, filepath: str):
        """Экспорт в CSV."""
        self.exporter_csv.export(df, filepath)

    def export_excel(self, df: pd.DataFrame, filepath: str):
        """Экспорт в Excel с форматированием."""
        self.exporter_xlsx.export(df, filepath)