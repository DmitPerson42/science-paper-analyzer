"""
Parser for arXiv.org — бесплатный REST API
"""

import requests
import time
import xml.etree.ElementTree as ET
from typing import List, Dict

ARXIV_API = "https://export.arxiv.org/api/query"


class ArxivParser:
    def search(self, query: str, max_results: int = 5) -> List[Dict]:
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results
        }
        headers = {"User-Agent": "SciencePaperAnalyzer/1.0 (mailto:analyzer@example.com)"}

        # Retry with backoff for rate limiting
        max_retries = 3
        for attempt in range(max_retries):
            try:
                resp = requests.get(ARXIV_API, params=params, headers=headers, timeout=30)
                if resp.status_code == 429:
                    wait = (attempt + 1) * 3
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                break
            except requests.exceptions.HTTPError as e:
                if attempt == max_retries - 1:
                    # Return friendly error instead of crashing
                    return []
                time.sleep(2)
        else:
            raise Exception(f"Failed after {max_retries} attempts")

        time.sleep(1)  # Polite delay for arXiv

        root = ET.fromstring(resp.text)
        ns = {"a": "http://www.w3.org/2005/Atom",
              "arxiv": "http://arxiv.org/schemas/atom"}

        papers = []
        for entry in root.findall("a:entry", ns):
            title = entry.findtext("a:title", "").strip().replace("\n", " ")
            summary = entry.findtext("a:summary", "").strip().replace("\n", " ")
            published = entry.findtext("a:published", "")
            link_el = entry.find("a:id", ns)
            link = link_el.text if link_el is not None else ""

            authors = []
            for author in entry.findall("a:author", ns):
                name = author.findtext("a:name", "")
                if name:
                    authors.append(name)

            year = published[:4] if published else ""

            doi = ""
            for link in entry.findall("a:link", ns):
                if link.get("title") == "doi":
                    doi = link.get("href", "")

            papers.append({
                "id": link.split("/")[-1] if link else "",
                "title": title,
                "authors": ", ".join(authors[:5]),
                "year": year,
                "abstract": summary,
                "url": link,
                "doi": doi,
                "venue": "arXiv",
            })

        return papers