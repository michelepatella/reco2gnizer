"""src/carbon_react_agent/state.py

This module defines the state structures for the agent.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from typing import Annotated, Any, Literal, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages


class ProductCarbonFootprint(TypedDict):
    """Structured representation of a Product Carbon Footprint (PCF) value.

    This class defines the expected structure for representing a PCF value.

    Attributes:
        co2e_kg (float):
            The carbon footprint value expressed in kilograms of CO2 equivalent.

        source (Literal["official", "estimated"]):
            The source from which the PCF value was obtained ("official", "estimated").

        explanation (str):
            Explanation to provide details about how the PCF value was obtained.
    """

    co2e_kg: float

    source: Literal["official", "estimated"]

    explanation: str


class RetrievedEvidence(TypedDict):
    """Structured representation of retrieved evidence for estimating carbon footprint.

    This class defines the expected structure for representing retrieved evidence.

    Attributes:
        content (str):
            The content of the retrieved evidence.

        source (str):
            The source from which the evidence was obtained.
    """

    content: str

    source: str


@dataclass
class InputState:
    """Input state for the agent.

    This class is used to define the initial state and structure of incoming data,
    representing a narrower interface to the outside world.

    Attributes:
        product_data (dict[str, Any]):
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

        retrieved_evidence (list[RetrievedEvidence]):
            Stores relevant information gathered for estimating carbon footprint.

        pcf (Optional[ProductCarbonFootprint]):
            The final carbon footprint result.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list,
    )

    search_web_count: int = field(default=0)

    retrieved_evidence: list[RetrievedEvidence] = field(default_factory=list)

    pcf: ProductCarbonFootprint | None = field(default=None)
