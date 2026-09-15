"""
Parser for Semantic Scholar — бесплатный REST API
"""

import requests
from typing import List, Dict

SEMANTIC_API = "https://api.semanticscholar.org/graph/v1/paper/search"
FIELDS = "title,authors,year,citationCount,abstract,venue,externalIds,url"


class SemanticScholarParser:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {"query": query, "limit": max_results, "fields": FIELDS}
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0"}

        resp = requests.get(SEMANTIC_API, params=params, headers=headers, timeout=30)
        
        if resp.status_code == 429:
            raise Exception("Rate limited. Please wait and try again.")
        resp.raise_for_status()

        data = resp.json()
        papers = []

        for paper in data.get("data", []):
            authors = [a.get("name", "") for a in paper.get("authors", [])]
            ext_ids = paper.get("externalIds", {}) or {}

            papers.append({
                "id": paper.get("paperId", ""),
                "title": paper.get("title", "N/A"),
                "authors": ", ".join(authors[:5]),
                "year": str(paper.get("year", "")) if paper.get("year") else "",
                "abstract": paper.get("abstract", "") or "",
                "url": f"https://www.semanticscholar.org/paper/{paper.get('paperId', '')}",
                "citation_count": paper.get("citationCount", 0),
                "venue": paper.get("venue", ""),
                "doi": ext_ids.get("DOI", ""),
            })

        return papers