"""src/carbon_react_agent/const.py

This module defines constants for the agent.
"""

# Model
DEFAULT_MODEL = "google_genai:gemini-2.5-flash"
DEFAULT_MODEL_TEMPERATURE = None

# Search web
DEFAULT_SEARCH_WEB_MAX_RESULTS = 10
DEFAULT_SEARCH_WEB_TYPE = "auto"
DEFAULT_SEARCH_WEB_MAX_CALLS = 3

# Logging
DEFAULT_ENABLE_LOGGING = True
DEFAULT_LOGS_PATH = "carbon_react_agent.log"
DEFAULT_LOGS_DIR = "logs"

# Graph
GRAPH_NAME = "carbon-react-agent"

# Graph nodes
CALL_MODEL_GRAPH_NODE = "call_model"
TOOLS_GRAPH_NODE = "tools"
ANSWER_GRAPH_NODE = "answer"
START_GRAPH_NODE = "__start__"
END_GRAPH_NODE = "__end__"

# Tools
SEARCH_WEB_TOOL = "search_web"
