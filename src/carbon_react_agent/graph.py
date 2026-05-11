"""src/carbon_react_agent/graph.py

This module defines a ReAct agent with LangGraph — LangChain.
"""

import json
from typing import Any, cast

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph
from langgraph.prebuilt import ToolNode
from langgraph.runtime import Runtime

from .const import (
    ANSWER_GRAPH_NODE,
    CALL_MODEL_GRAPH_NODE,
    END_GRAPH_NODE,
    GRAPH_NAME,
    SEARCH_WEB_TOOL,
    START_GRAPH_NODE,
    TOOLS_GRAPH_NODE,
)
from .context import Context
from .prompts import (
    AFTER_TOOL_MESSAGE_PROMPT,
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
    # Calculate remaining search web calls
    search_web_remaining_calls = (
        runtime.context.search_web_max_calls - state.search_web_count
    )

    # Format the system prompt
    system_prompt = SYSTEM_PROMPT.format(
        product_data=state.product_data,
        search_web_remaining_calls=search_web_remaining_calls,
        search_web_max_calls=runtime.context.search_web_max_calls,
    )

    # Initialize model with tools
    model = init_chat_model(
        model=runtime.context.model,
        temperature=runtime.context.model_temperature,
    ).bind_tools(TOOLS)

    # Prepare the messages list
    if not state.messages:
        # First execution: use system instructions directly as
        # the initial message
        initial_msg = HumanMessage(content=system_prompt)
        messages = [initial_msg]
    else:
        # Subsequent executions: always start with the initial message
        if state.messages[0]:
            messages = [state.messages[0], *list(state.messages[1:])]
        else:
            messages = list(state.messages)

        # If the last message is a ToolMessage, add a continuation
        # prompt for the model
        if messages and isinstance(messages[-1], ToolMessage):
            messages.append(
                HumanMessage(content=AFTER_TOOL_MESSAGE_PROMPT),
            )

    # Get the model's response
    response = cast(
        "AIMessage",
        await model.ainvoke(messages),
    )

    # Increment the search web counter if the model decided to call it
    new_search_web_count = state.search_web_count
    if response.tool_calls:
        for tool_call in response.tool_calls:
            if tool_call["name"] == SEARCH_WEB_TOOL:
                new_search_web_count += 1
                break

    # Return the model's response and updated counter to the state
    return_dict = {
        "messages": [response],
        "search_web_count": new_search_web_count,
    }

    return return_dict


async def answer(state: State, runtime: Runtime[Context]) -> dict[str, Any]:
    """Provide the agent's answer.

    This function is called at the end of the agent's execution to provide the
    agent's answer according to the specified format.

    Args:
        state (State):
            The current state of the execution.

        runtime (Runtime[Context]):
            The runtime environment.

    Returns:
        dict[str, Any]:
            A dictionary containing the agent's answer.
    """
    # Format the system prompt
    system_prompt = SYSTEM_PROMPT.format(
        product_data=state.product_data,
        search_web_remaining_calls=runtime.context.search_web_max_calls
        - runtime.context.search_web_max_calls,
        search_web_max_calls=runtime.context.search_web_max_calls,
    )

    # Initialize model without tools (it's the final answer,
    # no more tool calls allowed)
    model = init_chat_model(
        model=runtime.context.model,
        temperature=runtime.context.model_temperature,
    )

    # Prepare messages with the conversation history and
    # output format instructions
    if state.messages[0]:
        messages = [
            SystemMessage(content=system_prompt),
            state.messages[0],
            *state.messages[1:],
            HumanMessage(content=OUTPUT_FORMAT_INSTRUCTIONS),
        ]
    else:
        messages = [
            SystemMessage(content=system_prompt),
            *state.messages,
            HumanMessage(content=OUTPUT_FORMAT_INSTRUCTIONS),
        ]

    # Get the model's response
    response = await model.ainvoke(messages)

    try:
        # Clean the response content and parse it as JSON
        co2e_kg = json.loads(
            str(response.content)
            .replace("```json", "")
            .replace("```", "")
            .strip(),
        )
    except Exception:
        # Fallback in case of JSON parsing errors
        co2e_kg = {"co2e_kg": str(response.content)}

    return {"co2e_kg": co2e_kg}


def route_model_output(state: State, runtime: Runtime[Context]) -> str:
    """Determine the next node based on the model's output and agent state.

    This function checks if the model's last message contains tool calls and applies
    agent-specific logic:
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

    # If max search web calls reached, provide the answer
    if state.search_web_count >= runtime.context.search_web_max_calls:
        return ANSWER_GRAPH_NODE

    # If there is no tool call, provide the answer
    if not last_message.tool_calls:
        return ANSWER_GRAPH_NODE

    # Otherwise, execute the requested actions
    return TOOLS_GRAPH_NODE


async def tool_wrapper(state: State) -> dict[str, Any]:
    """Wrapper around ToolNode to handle tool execution.

    Args:
        state (State):
            The current state.

    Returns:
        dict[str, Any]:
            Updated state with tool results.
    """
    # Create and execute ToolNode
    tool_node = ToolNode(TOOLS)
    return await tool_node.ainvoke(state)


# ========================================================================= #
#            ReAct Agent Construction with LangGraph - LangChain            #
# ========================================================================= #
#                                                                           #
#                          +--------------+                                 #
#                          |  __start__   |                                 #
#                          +--------------+                                 #
#                                 |                                         #
#                                 v                                         #
#                          +--------------+                                 #
#                          |  call_model  | <----------+                    #
#                          +--------------+            |                    #
#                                 |                    |                    #
#                                 |          (route_model_output)           #
#                                 |                    |                    #
#                        _________|_________           |                    #
#                       |                   |          |                    #
#                       v                   v          |                    #
#                +--------------+    +--------------+  |                    #
#                |    answer    |    |    tools     |  |                    #
#                +--------------+    +--------------+  |                    #
#                       |                   |          |                    #
#                       v                   +----------+                    #
#                +--------------+                                           #
#                |   __end__    |                                           #
#                +--------------+                                           #
#                                                                           #
# ========================================================================== #
# Graph
builder = StateGraph(State, input_schema=InputState, context_schema=Context)

# Nodes
builder.add_node(CALL_MODEL_GRAPH_NODE, call_model)
builder.add_node(TOOLS_GRAPH_NODE, tool_wrapper)
builder.add_node(ANSWER_GRAPH_NODE, answer)

# Entry point
builder.add_edge(START_GRAPH_NODE, CALL_MODEL_GRAPH_NODE)

# Conditional edges
builder.add_conditional_edges(
    CALL_MODEL_GRAPH_NODE,
    route_model_output,
)

# Edges
builder.add_edge(TOOLS_GRAPH_NODE, CALL_MODEL_GRAPH_NODE)
builder.add_edge(ANSWER_GRAPH_NODE, END_GRAPH_NODE)

# Compile the graph
graph = builder.compile(name=GRAPH_NAME)
