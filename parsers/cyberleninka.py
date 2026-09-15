"""
Parser for CyberLeninka.ru — scraping HTML
"""

import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from parsers.utils import extract_year

CYBERLENINKA_BASE = "https://cyberleninka.ru"


class CyberLeninkaParser:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

        try:
            url = f"{CYBERLENINKA_BASE}/search?q={query}&page=1"
            resp = requests.get(url, headers=headers, timeout=30)
            resp.raise_for_status()
        except Exception as e:
            return self._fallback_empty(query, str(e))

        soup = BeautifulSoup(resp.text, "lxml")
        papers = []

        articles = soup.select("article, .search-item, .article-item, .b-serp-item")
        if not articles:
            articles = soup.select("li.result-item, div.result, .b-article")

        for article in articles[:max_results]:
            title_el = article.select_one("a[href*='/article/'], a[href*='article']")
            if not title_el:
                title_el = article.select_one("h2 a, h3 a, .title a")

            href = title_el.get("href", "") if title_el else ""
            if href and not href.startswith("http"):
                href = CYBERLENINKA_BASE + href

            title = title_el.get_text(strip=True) if title_el else "N/A"

            authors_el = article.select_one(".author, .authors, .b-serp-item__author")
            authors = authors_el.get_text(strip=True) if authors_el else ""

            year_el = article.select_one(".year, .date, .b-serp-item__date")
            year = year_el.get_text(strip=True) if year_el else ""

            abstract_el = article.select_one(".abstract, .annotation, .description, p")
            abstract = abstract_el.get_text(strip=True)[:300] if abstract_el else ""

            papers.append({
                "id": href.split("/")[-1] if href else "",
                "title": title,
                "authors": authors,
                "year": extract_year(year),
                "abstract": abstract,
                "url": href,
                "venue": "CyberLeninka",
            })

        if not papers:
            return self._fallback_empty(query, "Empty results from CyberLeninka")

        return papers

    def _fallback_empty(self, query: str, reason: str = ""):
        return [{
            "id": f"cyberleninka_{hash(query) % 100000}",
            "title": f"[CyberLeninka] Поиск: {query}",
            "authors": "N/A",
            "year": "",
            "abstract": f"Не удалось получить данные с CyberLeninka. Причина: {reason}. Попробуйте https://cyberleninka.ru/search?q={query}",
            "url": f"{CYBERLENINKA_BASE}/search?q={query}",
            "venue": "CyberLeninka (scraped)",
        }]