"""
Web search for latest news/reports. Returns the latest 5 items with title, url,
snippet, and date for detailed analysis. Uses duckduckgo-search (real DDG search);
the legacy api.duckduckgo.com endpoint returns empty/test data.
"""
import requests

# Prefer duckduckgo-search for real results; fall back to requests if not installed
try:
    from duckduckgo_search import DDGS
    _HAS_DDGS = True
except ImportError:
    _HAS_DDGS = False


def web_search(query, max_results=5):
    """
    Fetch the latest reports/articles for the query. Returns up to max_results
    items (default 5) with title, url, snippet, and date for detailed analysis.
    """
    print(f"[tools] web_search called with query={query}")

    if _HAS_DDGS:
        return _search_ddgs(query, max_results)
    return _search_fallback(query, max_results)


def _search_ddgs(query, max_results):
    """Use duckduckgo-search package for real DDG news/text results."""
    results = []
    try:
        with DDGS() as ddgs:
            # Prefer news for "latest reports"; fall back to text search
            try:
                raw = list(ddgs.news(query, max_results=max_results))
            except Exception:
                raw = list(ddgs.text(query, max_results=max_results))

            for i, r in enumerate(raw[:max_results], 1):
                title = r.get("title") or ""
                url = r.get("url") or r.get("href") or ""
                body = (r.get("body") or "")[:500]
                date = r.get("date") or ""
                results.append({
                    "rank": i,
                    "title": title,
                    "url": url,
                    "snippet": body,
                    "date": date,
                })
    except Exception as e:
        print(f"[tools] web_search DDGS error: {e}")
        return {
            "error": str(e),
            "query": query,
            "results": [],
            "message": "Install duckduckgo-search: pip install duckduckgo-search",
        }

    out = {"query": query, "count": len(results), "results": results}
    print(f"[tools] web_search returning {len(results)} results for '{query}'")
    return out


def _search_fallback(query, max_results):
    """Fallback when duckduckgo-search is not installed: try DDG HTML and parse."""
    # Legacy API returns empty/test data; we only use it to avoid breaking
    url = f"https://api.duckduckgo.com/?q={requests.utils.quote(query)}&format=json"
    try:
        r = requests.get(url, timeout=10)
        data = r.json()
    except Exception as e:
        return {
            "error": str(e),
            "query": query,
            "results": [],
            "message": "For real search results, install: pip install duckduckgo-search",
        }

    results = []
    # Abstract/Answer from instant API are often empty; RelatedTopics may have something
    if data.get("Abstract"):
        results.append({
            "rank": 1,
            "title": data.get("Heading") or "Abstract",
            "url": data.get("AbstractURL") or "",
            "snippet": data.get("Abstract", "")[:500],
            "date": "",
        })
    for item in data.get("RelatedTopics", [])[: max_results - len(results)]:
        if isinstance(item, dict) and item.get("Text"):
            results.append({
                "rank": len(results) + 1,
                "title": item.get("Text", "")[:80],
                "url": item.get("FirstURL") or "",
                "snippet": item.get("Text", "")[:500],
                "date": "",
            })
        elif isinstance(item, dict) and "Topics" in item:
            for sub in item["Topics"][:1]:
                if sub.get("Text"):
                    results.append({
                        "rank": len(results) + 1,
                        "title": sub.get("Text", "")[:80],
                        "url": sub.get("FirstURL") or "",
                        "snippet": sub.get("Text", "")[:500],
                        "date": "",
                    })

    out = {"query": query, "count": len(results), "results": results}
    if not results:
        out["message"] = "No results. For latest reports, install: pip install duckduckgo-search"
    return out
