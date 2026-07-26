from typing import List, Dict, Any
from app.core.config import settings
from app.core.logging import logger
from app.core.cache import ttl_cache

def search_competitors(query: str, max_results: int = 4) -> List[Dict[str, Any]]:
    """
    Searches web for competitor content using Tavily Search API.
    Uses in-memory TTL caching for instant sub-second responses on cached queries.
    """
    cache_key = f"tavily:{query.lower().strip()}"
    cached_results = ttl_cache.get(cache_key)
    if cached_results:
        return cached_results

    if settings.TAVILY_API_KEY:
        try:
            from tavily import TavilyClient
            client = TavilyClient(api_key=settings.TAVILY_API_KEY)
            response = client.search(query=query, search_depth="basic", max_results=max_results)
            results = response.get("results", [])
            logger.info(f"Tavily search returned {len(results)} competitor pages for query: {query}")
            parsed = [
                {
                    "title": r.get("title", ""),
                    "url": r.get("url", ""),
                    "snippet": r.get("content", r.get("snippet", ""))
                }
                for r in results
            ]
            ttl_cache.set(cache_key, parsed)
            return parsed
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}. Falling back to mock search results.")

    # Fallback Mock Results
    mock_results = [
        {
            "title": f"Top Guide to {query}",
            "url": "https://example-competitor1.com/guide",
            "snippet": f"A complete analysis covering features, advantages, setup steps, and real-world results for {query}."
        },
        {
            "title": f"Best Practices and Strategies for {query}",
            "url": "https://example-competitor2.com/best-practices",
            "snippet": f"In-depth breakdown of how top industry leaders approach {query}, structural formats, and actionable recommendations."
        }
    ]
    ttl_cache.set(cache_key, mock_results)
    return mock_results
