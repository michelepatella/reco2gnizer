"""src/carbon_react_agent/graph.py

Define a ReAct agent with LangGraph (LangChain).
"""

from typing import Any, cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from carbon_react_agent.const import (
    ANSWER_NODE,
    CALL_MODEL_NODE,
    END_NODE,
    START_NODE,
    TOOLS_NODE,
)
from carbon_react_agent.context import Context
from carbon_react_agent.prompts import (
    OUTPUT_FORMAT_INSTRUCTIONS,
    SYSTEM_PROMPT,
)
from carbon_react_agent.state import InputState, State
from carbon_react_agent.tools import TOOLS


async def call_model(
    state: State,
    runtime: Runtime[Context],
) -> dict[str, list[AIMessage]]:
    """Call the LLM powering the agent.

    This function prepares the prompt, initializes the model,
    and processes the response.

    Args:
        state (State):
            The current state of the execution.

        runtime (Runtime[Context]):
            The runtime environment.

    Returns:
        dict[str, list[AIMessage]]:
            A dictionary containing the model's response message.
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

    # Format the system prompt with dynamic information
    system_message = SYSTEM_PROMPT.format(
        product_data=state.product_data,
        search_web_remaining_calls=search_web_remaining_calls,
        search_web_max_calls=runtime.context.search_web_max_calls,
    )

    # Get the model's response
    response = cast(
        "AIMessage",
        await model.ainvoke(
            [{"role": "system", "content": system_message}, *state.messages],
        ),
    )

    # Return the model's response as a list to
    # be added to existing messages
    return {"messages": [response]}


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
        {
            "role": "system",
            "content": SYSTEM_PROMPT.format(
                product_data=state.product_data,
                search_web_remaining_calls=0,
                search_web_max_calls=runtime.context.search_web_max_calls,
            ),
        },
        *state.messages,
        {"role": "user", "content": OUTPUT_FORMAT_INSTRUCTIONS},
    ]

    # Get the structured response
    response = cast(
        "dict[str, Any]",
        await model.ainvoke(messages),
    )

    return {"co2e_kg": response}


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
