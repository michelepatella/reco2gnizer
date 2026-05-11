"""src/carbon_react_agent/tools.py

This module provides tools which can be used by the agent.
"""

from collections.abc import Callable
from typing import Any, cast

from langchain_exa import ExaSearchRetriever
from langgraph.runtime import get_runtime

from carbon_react_agent.context import Context


async def search_web(query: str) -> dict[str, Any] | None:
    """Search for web results.

    This function performs a web search using the Exa search engine.

    Args:
        query (str):
            The search query.

    Returns:
        Optional[Dict[str, Any]]:
            The search results or None if no results were found.
    """
    runtime = get_runtime(Context)
    wrapped = ExaSearchRetriever(
        k=runtime.context.search_web_max_results,
        type=runtime.context.search_web_type,
    )
    return cast("dict[str, Any]", await wrapped.ainvoke({"query": query}))


TOOLS: list[Callable[..., Any]] = [search_web]
