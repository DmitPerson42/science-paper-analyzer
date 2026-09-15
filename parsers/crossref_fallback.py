"""
Fallback parser using CrossRef API
Используется для сайтов без открытого API: ResearchGate, eLibrary, Dissercat, FIPS
"""

import requests
from typing import List, Dict

CROSSREF_API = "https://api.crossref.org/works"


class CrossRefFallback:
    def __init__(self, source_name: str = "CrossRef"):
        self.source_name = source_name

    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {
            "query": query,
            "rows": max_results,
            "select": "title,author,DOI,URL,abstract,publication-date,publisher,container-title"
        }
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0 (mailto:example@example.com)"}

        try:
            resp = requests.get(CROSSREF_API, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            return self._empty_result(query, str(e))

        data = resp.json()
        items = data.get("message", {}).get("items", [])
        papers = []

        for item in items[:max_results]:
            title = item.get("title", ["N/A"])[0]
            authors_list = item.get("author", [])
            authors = ", ".join([
                f"{a.get('given', '')} {a.get('family', '')}".strip()
                for a in authors_list[:5]
            ])
            doi = item.get("DOI", "")
            url = item.get("URL", f"https://doi.org/{doi}") if doi else ""
            year = ""
            date_parts = item.get("published-online", {}).get("date-parts") or \
                        item.get("published-print", {}).get("date-parts") or \
                        item.get("issued", {}).get("date-parts") or []
            if date_parts and len(date_parts) > 0 and len(date_parts[0]) > 0:
                year = str(date_parts[0][0])

            abstract = item.get("abstract", "") or ""
            # Clean HTML tags from abstract
            if abstract:
                import re
                abstract = re.sub(r'<[^>]+>', '', abstract)

            venue = item.get("container-title", [""])[0] or item.get("publisher", "")
            if isinstance(venue, list):
                venue = venue[0] if venue else ""

            papers.append({
                "id": doi,
                "title": title,
                "authors": authors,
                "year": year,
                "abstract": abstract,
                "url": url,
                "doi": doi,
                "venue": venue,
                "source_context": self.source_name,
            })

        if not papers:
            return self._empty_result(query, "No results from CrossRef")

        return papers

    def _empty_result(self, query: str, reason: str = "") -> List[Dict]:
        return [{
            "id": f"crossref_{hash(query) % 100000}",
            "title": f"[{self.source_name}] {query}",
            "authors": "N/A",
            "year": "",
            "abstract": f"Sourced via CrossRef API. {reason}",
            "url": "https://search.crossref.org/?q=" + query.replace(" ", "+"),
            "doi": "",
            "venue": self.source_name,
            "source_context": self.source_name,
        }]