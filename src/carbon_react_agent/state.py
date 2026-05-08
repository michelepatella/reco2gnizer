"""src/carbon_react_agent/state.py

This module defines the state structures for the agent.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Optional, Sequence, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from langgraph.managed import IsLastStep
from typing_extensions import Annotated


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

        is_last_step (IsLastStep):
            Indicates whether the current step is the last one before the graph
            raises an error.

        search_web_count (int):
            Tracks the number of times search web has been called per agent run.

        official_pcf (Optional[ProductCarbonFootprint]):
            Stores information about the official carbon footprint for the product.

        retrieved_evidence (list[RetrievedEvidence]):
            Stores relevant information gathered for estimating carbon footprint.

        estimated_pcf (Optional[ProductCarbonFootprint]):
            Stores information about the estimated carbon footprint for the product.
    """

    messages: Annotated[Sequence[AnyMessage], add_messages] = field(
        default_factory=list
    )

    is_last_step: IsLastStep = field(default=False)

    search_web_count: int = field(default=0)

    official_pcf: Optional[ProductCarbonFootprint] = field(default=None)

    retrieved_evidence: list[RetrievedEvidence] = field(default_factory=list)

    estimated_pcf: Optional[ProductCarbonFootprint] = field(default=None)
