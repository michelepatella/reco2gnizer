"""src/carbon_react_agent/tools.py

This module provides tools which can be used by the agent.
"""

from typing import Any, Callable, List, Optional, cast

from langchain_exa import ExaSearchRetriever
from langgraph.runtime import get_runtime

from carbon_react_agent.context import Context


async def search_web(query: str) -> Optional[dict[str, Any]]:
    """Search for web results.

    This function performs a web search using the Exa search engine.

    Args:
        query (str): 
            The search query.

    Returns:
        Optional[dict[str, Any]]: 
            The search results or None if no results were found.
    """
    runtime = get_runtime(Context)
    wrapped = ExaSearchRetriever(
        k=runtime.context.search_web_max_results,
        type=runtime.context.search_web_type
    )
    return cast(dict[str, Any], await wrapped.ainvoke({"query": query}))


TOOLS: List[Callable[..., Any]] = [search_web]
