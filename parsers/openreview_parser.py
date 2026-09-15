"""
Parser for OpenReview.net — публичный REST API
"""

import requests
from typing import List, Dict
from parsers.utils import extract_year

OPENREVIEW_API = "https://api.openreview.net/notes/search"


class OpenReviewParser:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {"term": query, "limit": max_results, "source": "forum"}
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0"}

        try:
            resp = requests.get(OPENREVIEW_API, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception:
            # fallback — поиск через другой эндпоинт
            alt_url = f"https://api.openreview.net/notes?term={query}&limit={max_results}"
            resp = requests.get(alt_url, headers=headers, timeout=30)
            resp.raise_for_status()

        data = resp.json()
        papers = []

        notes = data.get("notes", [])
        if not notes:
            # OpenReview может возвращать в другом формате
            notes = data.get("rows", [])

        for note in notes[:max_results]:
            content = note.get("content", {})
            title = content.get("title", note.get("title", "N/A"))
            if isinstance(title, dict):
                title = title.get("value", "N/A")

            authors = content.get("authors", note.get("authors", []))
            if authors and isinstance(authors, dict):
                authors = authors.get("value", [])

            abstract = content.get("abstract", "")
            if isinstance(abstract, dict):
                abstract = abstract.get("value", "")

            forum = note.get("forum", "")
            cdate = note.get("cdate", note.get("tcdate", 0))
            year = extract_year(cdate)

            papers.append({
                "id": note.get("id", ""),
                "title": title if isinstance(title, str) else str(title),
                "authors": ", ".join(authors[:5]) if isinstance(authors, list) else str(authors),
                "year": year,
                "abstract": abstract,
                "url": f"https://openreview.net/forum?id={forum}" if forum else "",
                "venue": "OpenReview",
            })

        return papers