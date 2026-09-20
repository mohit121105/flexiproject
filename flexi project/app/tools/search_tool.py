"""
app/tools/search_tool.py
Unit 1 — Web search FunctionTool for AI agents.

Wraps Tavily Search API as a callable tool that agents can invoke
to retrieve real-time information about known bugs, CVEs, or solutions.
Falls back to a mock response if TAVILY_API_KEY is not set.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")


def search_web(query: str, max_results: int = 5) -> str:
    """
    Search the web for information related to a software defect.

    Args:
        query: The search query string (e.g., 'React login form crash on submit fix')
        max_results: Maximum number of results to return (default: 5)

    Returns:
        A formatted string of search results with titles, URLs, and snippets.
    """
    if not TAVILY_API_KEY:
        # Mock response for demo without API key
        return _mock_search(query)

    try:
        response = requests.post(
            "https://api.tavily.com/search",
            json={
                "api_key": TAVILY_API_KEY,
                "query": query,
                "max_results": max_results,
                "search_depth": "basic",
                "include_answer": True,
            },
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()

        results = []
        if data.get("answer"):
            results.append(f"**Summary**: {data['answer']}\n")

        for i, result in enumerate(data.get("results", []), 1):
            results.append(
                f"{i}. **{result.get('title', 'No title')}**\n"
                f"   URL: {result.get('url', '')}\n"
                f"   {result.get('content', '')[:300]}...\n"
            )

        return "\n".join(results) if results else "No results found."

    except Exception as e:
        return f"Search failed: {str(e)}. Using offline mode."


def _mock_search(query: str) -> str:
    """Return a realistic mock response when no API key is available."""
    return f"""**Mock Search Results for:** "{query}"

1. **Stack Overflow — Common fixes for this issue**
   URL: https://stackoverflow.com/questions/example
   Several developers have reported similar issues. The most common fix involves
   checking null pointer exceptions and input validation before form submission.

2. **GitHub Issues — Related bug reports**
   URL: https://github.com/example/repo/issues/123
   This issue was reported in version 2.3.1 and fixed in 2.3.4. The root cause
   was an unhandled async state update during component unmount.

3. **Official Documentation — Best Practices**
   URL: https://docs.example.com/troubleshooting
   Always validate user input on both client and server side. Use try-catch
   blocks around async operations to prevent unhandled promise rejections.

> Note: Set TAVILY_API_KEY in .env for real-time search results.
"""


# ── FunctionTool wrapper for OpenAI Agents SDK / LangGraph ────────────────────

def get_search_tool_definition() -> dict:
    """
    Return the tool definition dict compatible with Gemini function calling
    and the OpenAI Agents SDK FunctionTool format.
    """
    return {
        "name": "search_web",
        "description": (
            "Search the internet for information about a software defect, error message, "
            "known bug, CVE, or fix. Use this when you need real-time information."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query, e.g. 'React useState crash fix github'",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of search results (default: 5)",
                },
            },
            "required": ["query"],
        },
        "function": search_web,
    }


if __name__ == "__main__":
    result = search_web("React login form crash on submit null pointer exception")
    print(result)
