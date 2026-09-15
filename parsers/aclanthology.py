"""
Parser for ACL Anthology — публичный REST API
"""

import requests
from typing import List, Dict

ACL_API = "https://api.aclanthology.org/v1/search"


class ACLAnthologyParser:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {"q": query, "limit": max_results}
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0"}

        try:
            resp = requests.get(ACL_API, params=params, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception:
            # fallback: direct website search
            return self._scrape_search(query, max_results)

        data = resp.json()
        papers = []
        results = data.get("results", data.get("data", []))

        for paper in results[:max_results]:
            anth_id = paper.get("paper_id", paper.get("id", ""))
            title = paper.get("title", "N/A")
            authors_list = paper.get("authors", [])
            year = str(paper.get("year", ""))
            abstract = paper.get("abstract", paper.get("paper_abstract", ""))

            papers.append({
                "id": anth_id,
                "title": title,
                "authors": ", ".join(authors_list[:5]) if isinstance(authors_list, list) else str(authors_list),
                "year": year,
                "abstract": abstract,
                "url": f"https://aclanthology.org/{anth_id}/" if anth_id else "",
                "venue": "ACL Anthology",
            })

        return papers

    def _scrape_search(self, query: str, max_results: int) -> List[Dict]:
        """Fallback: поиск через веб-страницу"""
        import requests
        from bs4 import BeautifulSoup

        url = f"https://aclanthology.org/?q={query}"
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0"}
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")
        papers = []

        for item in soup.select(".paper-card, .list-item")[:max_results]:
            title_el = item.select_one("a, .title")
            title = title_el.get_text(strip=True) if title_el else "N/A"
            link = title_el.get("href", "") if title_el and hasattr(title_el, "get") else ""

            if not link.startswith("http"):
                link = "https://aclanthology.org" + link

            year_el = item.select_one(".year, .date")
            year = year_el.get_text(strip=True) if year_el else ""

            papers.append({
                "id": link.split("/")[-2] if link else "",
                "title": title,
                "authors": "",
                "year": year,
                "abstract": "",
                "url": link,
                "venue": "ACL Anthology",
            })

        return papers