"""src/carbon_react_agent/__init__.py

This module implements a ReAct agent which leverages LLM reasoning and 
semantic web search to compute carbon footprints from product data.
"""

from carbon_react_agent.graph import graph

__all__ = ["graph"]
