from __future__ import annotations

import os
from typing import Any

import requests

SERPAPI_URL = "https://serpapi.com/search.json"
BING_URL = "https://api.bing.microsoft.com/v7.0/search"
GOOGLE_CSE_URL = "https://www.googleapis.com/customsearch/v1"


class SearchToolError(RuntimeError):
    pass


def _serpapi_search(query: str, num_results: int = 5) -> list[dict[str, str]]:
    api_key = os.environ.get("SERPAPI_API_KEY")
    if not api_key:
        raise SearchToolError("SERPAPI_API_KEY is not set")

    params = {
        "q": query,
        "engine": os.environ.get("SERPAPI_ENGINE", "google"),
        "api_key": api_key,
        "num": num_results,
    }
    response = requests.get(SERPAPI_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    organic_results = data.get("organic_results") or []
    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", item.get("description", "")),
            "link": item.get("link", item.get("source", "")),
            "source": "serpapi",
        }
        for item in organic_results[:num_results]
    ]


def _bing_search(query: str, num_results: int = 5) -> list[dict[str, str]]:
    api_key = os.environ.get("BING_SEARCH_API_KEY")
    if not api_key:
        raise SearchToolError("BING_SEARCH_API_KEY is not set")

    headers = {"Ocp-Apim-Subscription-Key": api_key}
    params = {
        "q": query,
        "count": num_results,
        "mkt": os.environ.get("BING_SEARCH_MARKET", "en-US"),
        "textDecorations": True,
        "textFormat": "HTML",
    }
    response = requests.get(BING_URL, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    results = data.get("webPages", {}).get("value", [])
    return [
        {
            "title": item.get("name", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("url", ""),
            "source": "bing",
        }
        for item in results[:num_results]
    ]


def _google_cse_search(query: str, num_results: int = 5) -> list[dict[str, str]]:
    api_key = os.environ.get("GOOGLE_CSE_API_KEY")
    engine_id = os.environ.get("GOOGLE_CSE_ENGINE_ID")
    if not api_key or not engine_id:
        raise SearchToolError("GOOGLE_CSE_API_KEY or GOOGLE_CSE_ENGINE_ID is not set")

    params = {
        "key": api_key,
        "cx": engine_id,
        "q": query,
        "num": num_results,
    }
    response = requests.get(GOOGLE_CSE_URL, params=params, timeout=30)
    response.raise_for_status()
    data = response.json()

    items = data.get("items", [])
    return [
        {
            "title": item.get("title", ""),
            "snippet": item.get("snippet", ""),
            "link": item.get("link", ""),
            "source": "google_cse",
        }
        for item in items[:num_results]
    ]


def search(query: str, num_results: int = 5) -> list[dict[str, str]]:
    """Run a web search using an available configured engine."""
    if os.environ.get("GOOGLE_CSE_API_KEY") and os.environ.get("GOOGLE_CSE_ENGINE_ID"):
        return _google_cse_search(query, num_results=num_results)

    if os.environ.get("BING_SEARCH_API_KEY"):
        return _bing_search(query, num_results=num_results)

    if os.environ.get("SERPAPI_API_KEY"):
        return _serpapi_search(query, num_results=num_results)

    raise SearchToolError(
        "No supported web search API configured. Set one of GOOGLE_CSE_API_KEY and GOOGLE_CSE_ENGINE_ID, BING_SEARCH_API_KEY, or SERPAPI_API_KEY."
    )


def format_results(results: list[dict[str, str]]) -> str:
    lines = []
    for index, result in enumerate(results, start=1):
        lines.append(
            f"{index}. {result.get('title', '')}\n   {result.get('snippet', '')}\n   {result.get('link', '')}\n"
        )
    return "\n".join(lines)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Run a web search through a configured search provider.")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--num-results", type=int, default=5)
    args = parser.parse_args()

    try:
        matches = search(args.query, num_results=args.num_results)
        print(format_results(matches))
    except Exception as exc:
        raise SystemExit(str(exc))
