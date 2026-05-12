"""src/reco2gnizer/tools.py

This module provides tools which can be used by the agent.
"""

from collections.abc import Callable
from typing import Any

from langchain_exa import ExaSearchRetriever
from langgraph.runtime import get_runtime

from .context import Context


async def search_web(query: str) -> Any:
    """Search for web results.

    This function performs a web search using the Exa search engine.

    Args:
        query (str):
            The search query.

    Returns:
        Any:
            The search results.
    """
    runtime = get_runtime(Context)
    wrapped = ExaSearchRetriever(
        k=runtime.context.search_web_max_results,
        type=runtime.context.search_web_type,
    )
    return await wrapped.ainvoke(query)


TOOLS: list[Callable[..., Any]] = [search_web]
