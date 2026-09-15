"""
Parser for JMLR.org — scraping HTML
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict

JMLR_URL = "https://jmlr.org/papers/"


class JMLRParser:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        """Ищет статьи через страницу JMLR и фильтрует по ключевым словам."""
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0"}

        try:
            resp = requests.get(JMLR_URL, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception:
            return self._fallback_search(query, max_results)

        soup = BeautifulSoup(resp.text, "lxml")
        papers = []
        q_lower = query.lower()

        # JMLR организует статьи по годам/томам
        links = soup.select("a[href*='papers/v']")
        paper_links = [l for l in links if not l.find("img")]

        for link in paper_links:
            href = link.get("href", "")
            title = link.get_text(strip=True)

            if not title or (q_lower not in title.lower() and q_lower.split()[0] not in title.lower()):
                continue

            if not href.startswith("http"):
                href = "https://jmlr.org" + href

            papers.append({
                "id": href.split("/")[-1].replace(".html", ""),
                "title": title,
                "authors": "",
                "year": href.split("/v")[-1][:4] if "/v" in href else "",
                "abstract": "",
                "url": href,
                "venue": "JMLR",
            })

            if len(papers) >= max_results:
                break

        # Если не нашли по заголовку — возвращаем последние статьи
        if not papers:
            for link in paper_links[:max_results]:
                href = link.get("href", "")
                title = link.get_text(strip=True)
                if not href.startswith("http"):
                    href = "https://jmlr.org" + href

                papers.append({
                    "id": href.split("/")[-1].replace(".html", ""),
                    "title": title or "JMLR Paper",
                    "authors": "",
                    "year": href.split("/v")[-1][:4] if "/v" in href else "",
                    "abstract": "",
                    "url": href,
                    "venue": "JMLR",
                })

        return papers

    def _fallback_search(self, query: str, max_results: int) -> List[Dict]:
        """Fallback: возвращаем заглушку с ссылкой на JMLR."""
        return [{
            "id": f"jmlr_{query.replace(' ', '_')}",
            "title": f"JMLR papers related to: {query}",
            "authors": "See JMLR website",
            "year": "",
            "abstract": "Visit JMLR.org/papers for full list.",
            "url": "https://jmlr.org/papers/",
            "venue": "JMLR (scraped)",
        }]