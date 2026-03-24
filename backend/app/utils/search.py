import logging
from duckduckgo_search import DDGS  # pip install duckduckgo-search

logger = logging.getLogger(__name__)


class FreeSearchService:
    def search(self, query: str, max_results: int = 3) -> list:
        """
        Perform a free search using DuckDuckGo.
        Returns a list of dicts with title, snippet, link.
        """
        try:
            with DDGS() as ddgs:
                results = []
                for r in ddgs.text(query, max_results=max_results):
                    results.append({
                        "title": r.get("title", ""),
                        "snippet": r.get("body", ""),
                        "link": r.get("href", ""),
                    })
                return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []
