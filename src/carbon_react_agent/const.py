"""src/carbon_react_agent/const.py

This module defines constants for the agent.
"""

# Model
DEFAULT_MODEL = (
    "google_genai:gemini-2.5-flash"  # Alternatively: "openai:o3-mini"
)
DEFAULT_MODEL_TEMPERATURE = 0.0

# Search web
DEFAULT_SEARCH_WEB_MAX_RESULTS = 10
DEFAULT_SEARCH_WEB_TYPE = "auto"
DEFAULT_SEARCH_WEB_MAX_CALLS = 3

# Graph nodes
CALL_MODEL_NODE = "call_model"
TOOLS_NODE = "tools"
ANSWER_NODE = "answer"
START_NODE = "__start__"
END_NODE = "__end__"
