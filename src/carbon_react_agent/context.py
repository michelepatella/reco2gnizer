"""src/carbon_react_agent/context.py

This module defines configurable parameters for the agent.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field, fields
from typing import Annotated

from carbon_react_agent.const import (
    DEFAULT_MODEL,
    DEFAULT_MODEL_TEMPERATURE,
    DEFAULT_SEARCH_WEB_MAX_RESULTS,
    DEFAULT_SEARCH_WEB_TYPE,
)

from . import prompts


@dataclass(kw_only=True)
class Context:
    """The context for the agent.

    This class defines the configurable parameters for the agent.

    Attributes:
        system_prompt (str):
            The system prompt to use for the agent's interactions.

        model (Annotated[str, {"__template_metadata__": {"kind": "llm"}}]):
            The name of the language model to use for the agent's main interactions.
            ('provider-name/model-name').

        search_web_max_results (int):
            The maximum number of web search results to return for each query (1-100).

        search_web_type (str):
            The type of web search to perform ("fast", "auto", "deep").
    """

    system_prompt: str = field(
        default=prompts.SYSTEM_PROMPT,
        metadata={
            "description": "The system prompt to use for the agent's interactions.",
        },
    )

    model: Annotated[str, {"__template_metadata__": {"kind": "llm"}}] = field(
        default=DEFAULT_MODEL,
        metadata={
            "description": "The name of the language model to use for the agent's main interactions. "
            "('provider-name/model-name')",
        },
    )

    model_temperature: float = field(
        default=DEFAULT_MODEL_TEMPERATURE,
        metadata={
            "description": "The temperature to use for the language model (0.0-1.0).",
        },
    )

    search_web_max_results: int = field(
        default=DEFAULT_SEARCH_WEB_MAX_RESULTS,
        metadata={
            "description": "The maximum number of web search results to return for each query (1-100).",
        },
    )

    search_web_type: str = field(
        default=DEFAULT_SEARCH_WEB_TYPE,
        metadata={
            "description": 'The type of web search to perform ("fast", "auto", "deep").',
        },
    )

    def __post_init__(self) -> None:
        """Fetch env vars for attributes that were not passed as args.

        This function iterates over the fields of the dataclass and checks if
        any of them were not initialized. If a field was not initialized, it
        attempts to fetch its value from an environment variable with the
        same name (converted to uppercase). If the environment variable is not
        set, it retains the default value defined in the dataclass.

        Returns:
            None
        """
        for f in fields(self):
            if not f.init:
                continue

            if getattr(self, f.name) == f.default:
                setattr(
                    self,
                    f.name,
                    os.environ.get(f.name.upper(), f.default),
                )
