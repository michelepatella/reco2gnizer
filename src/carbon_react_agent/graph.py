"""src/carbon_react_agent/graph.py

Define a ReAct agent with LangGraph (LangChain).
"""

import json
from typing import Any, cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from .const import (
    ANSWER_NODE,
    CALL_MODEL_NODE,
    END_NODE,
    START_NODE,
    TOOLS_NODE,
)
from .context import Context
from .prompts import (
    OUTPUT_FORMAT_INSTRUCTIONS,
    SYSTEM_PROMPT,
)
from .state import InputState, State
from .tools import TOOLS


async def call_model(
    state: State,
    runtime: Runtime[Context],
) -> dict[str, Any]:
    """Call the LLM powering the agent.

    This function prepares the prompt, initializes the model,
    and processes the response.

    Args:
        state (State):
            The current state of the execution.

        runtime (Runtime[Context]):
            The runtime environment.

    Returns:
        dict[str, Any]:
            A dictionary containing the model's response message and
            the updated search count.
    """
    # Initialize the model with tool binding
    model = init_chat_model(
        model=runtime.context.model,
        temperature=runtime.context.model_temperature,
    ).bind_tools(TOOLS)

    # Calculate remaining search web calls
    search_web_remaining_calls = (
        runtime.context.search_web_max_calls - state.search_web_count
    )

    # Format the system prompt instructions
    system_instructions = SYSTEM_PROMPT.format(
        product_data=state.product_data,
        search_web_remaining_calls=search_web_remaining_calls,
        search_web_max_calls=runtime.context.search_web_max_calls,
    )

    if not state.messages:
        # First execution: Create the initial sequence
        messages = [
            SystemMessage(content=system_instructions),
            HumanMessage(
                content=f"Analyze the Product Carbon Footprint (PCF) for this product: {state.product_data}",
            ),
        ]
    else:
        # Subsequent executions: pass the conversation history
        messages = list(state.messages)

    # Get the model's response
    response = cast(
        "AIMessage",
        await model.ainvoke(messages),
    )

    # Increment the search counter if the model decided to call a tool
    new_search_web_count = state.search_web_count
    if response.tool_calls:
        new_search_web_count += 1

    # Return the model's response and updated counter to the state
    return {
        "messages": [response],
        "search_web_count": new_search_web_count,
    }


async def answer(state: State, runtime: Runtime[Context]) -> dict[str, Any]:
    """Provide the final answer.

    This function is called at the end of the agent's execution to provide the
    final answer according to the specified format.

    Args:
        state (State):
            The current state of the execution.

        runtime (Runtime[Context]):
            The runtime environment.

    Returns:
        dict[str, Any]:
            A dictionary containing the final PCF result.
    """
    # Initialize the model
    model = init_chat_model(
        model=runtime.context.model,
        temperature=runtime.context.model_temperature,
    )

    # Prepare messages with the output format instructions
    messages = [
        SystemMessage(
            content=SYSTEM_PROMPT.format(
                product_data=state.product_data,
                search_web_remaining_calls=0,
                search_web_max_calls=runtime.context.search_web_max_calls,
            ),
        ),
        *state.messages,
        HumanMessage(content=OUTPUT_FORMAT_INSTRUCTIONS),
    ]

    # Get the model's response
    response = await model.ainvoke(messages)

    try:
        # Ensure content is a string and clean potential
        # markdown wrappers
        content_str = str(response.content)
        cleaned_content = (
            content_str.replace("```json", "").replace("```", "").strip()
        )
        pcf_data = json.loads(cleaned_content)
    except Exception:
        # Fallback in case of parsing errors
        pcf_data = {"co2e_kg": str(response.content)}

    # Return the parsed data to be stored in co2e_kg
    return {"co2e_kg": pcf_data}


def route_model_output(state: State, runtime: Runtime[Context]) -> str:
    """Determine the next node based on the model's output and agent state.

    This function checks if the model's last message contains tool calls and applies
    agent-specific logic:
    - If carbon footprint has been found, end the agent
    - If max search web limit has been reached, provide the answer
    - If the model has no tool calls, provide the answer
    - Otherwise, execute requested actions

    Args:
        state (State):
            The current state of the agent's execution.

        runtime (Runtime[Context]):
            The runtime environment.

    Returns:
        str:
            The name of the next node to call.
    """
    # Get the last message from the state
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}",
        )

    # If carbon footprint has been found, end immediately
    if state.co2e_kg:
        return END_NODE

    # If max search web calls reached, provide the answer
    if state.search_web_count >= runtime.context.search_web_max_calls:
        return ANSWER_NODE

    # If there is no tool call, provide the answer
    if not last_message.tool_calls:
        return ANSWER_NODE

    # Otherwise, execute the requested actions
    return TOOLS_NODE


# Build the graph
builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# Define the nodes
builder.add_node(CALL_MODEL_NODE, call_model)
builder.add_node(TOOLS_NODE, ToolNode(TOOLS))
builder.add_node(ANSWER_NODE, answer)

# Set the entrypoint
builder.add_edge(START_NODE, CALL_MODEL_NODE)

# Add a conditional edge to determine the next
# step after the entry node
builder.add_conditional_edges(
    CALL_MODEL_NODE,
    route_model_output,
)

# Add classical edges
builder.add_edge(TOOLS_NODE, CALL_MODEL_NODE)
builder.add_edge(ANSWER_NODE, END_NODE)

# Compile the builder into an executable graph
graph = builder.compile(name="Carbon ReAct Agent")
