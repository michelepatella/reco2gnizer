"""src/carbon_react_agent/state.py

This module defines the state structures for the agent.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated, Any

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


@dataclass
class InputState:
    """Input state for the agent.

    This class is used to define the initial state and structure of incoming data,
    representing a narrower interface to the outside world.

    Attributes:
        product_data (Dict[str, Any]):
            The data of the product for which the carbon footprint is being computed.
    """

    product_data: dict[str, Any]


@dataclass
class State(InputState):
    """State of the agent.

    This class represents the state of the agent, storing any information needed
    throughout the agent's lifecycle.

    Attributes:
        messages (Annotated[Sequence[AnyMessage], add_messages]):
            Messages tracking the primary execution state of the agent.

        search_web_count (int):
            Tracks the number of times search web has been called per agent run.

        retrieved_evidence (List[Any]):
            Stores relevant information gathered for estimating carbon footprint.

        pcf (Dict[str, Any]):
            The final carbon footprint result.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list,
    )

    search_web_count: int = field(default=0)

    retrieved_evidence: list[Any] = field(default_factory=list)

    pcf: dict[str, Any] = field(default=dict)
