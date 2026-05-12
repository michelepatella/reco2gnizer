<a id="readme-top"></a>

<br/>

<div align="center">
  <h1 align="center">ReCO₂gnizer</h1>
  <p align="center">
    ReAct agent built with LangGraph, leveraging LLM reasoning <br>
    and semantic web search to compute carbon footprints from product data.
  </p>
</div>

<br/>
<br/>
  
<details>
  <summary><strong>Table of Contents</strong></summary>
  ────────────
  <ul>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#license">License</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<br/>

## About The Project

<div align="center">
<img  width="40%" src="https://github.com/user-attachments/assets/ab26a136-7c2e-464c-b880-b07bfc0d26d7" />
</div>

<br>

**ReCO₂gnizer** is a ReAct-based AI agent that automatically computes the carbon footprint of any product by combining LLM reasoning with semantic web search.

- **LangGraph Architecture** — Implements a production-grade agentic framework with deterministic node-based control flow, execution state tracking, and configurable context
- **LLM Reasoning** — Leverages an LLM (OpenAI/Google Gemini) to retrieve, analyze, and compute the most accurate carbon footprint
- **Semantic Web Search** — Searches the web via Exa API to retrieve reliable environmental data related to the input product and supporting evidence for estimation
- **ReAct Loop** — Uses a ReAct loop to prioritize official carbon footprint data and fallback to supporting evidence to inform estimation
- **Carbon Footprint Quantification** — Computes the carbon footprint value in kg CO₂e (Cradle-to-Grave) based on retrieved information
- **Logging**: Records full execution traces for debugging, validation, and auditability, making the system transparent and explainable

> [!NOTE]
> LLM-based carbon footprint estimation follows established protocols:
> - GHG Protocol Product Standard — System boundaries and calculation methodology
> - ISO 14040/14044 — Life Cycle Assessment principles
> - PAS 2050 and ISO/TS 14067 — Carbon footprint calculation guidelines

<p align="right"><a href="#readme-top">Top ↑</a></p>

### Built With

[![Python](https://img.shields.io/badge/python-3776AB?style=for-the-badge&logo=python&logoColor=ffdd54)](https://www.python.org/)  
[![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langgraph&logoColor=white)](https://www.langchain.com/langgraph)  
[![LangChain](https://img.shields.io/badge/LangChain-7FC8FF?style=for-the-badge&logo=langchain&logoColor=black)](https://www.langchain.com/langchain)

<p align="right"><a href="#readme-top">Top ↑</a></p>

## Getting Started

### Prerequisites

**Python**  
Required version: 3.14.4  
Link: https://www.python.org/downloads/release/python-3144/

> [!WARNING]
> Compatibility with earlier or later Python versions has not been tested.  

**API Keys**  
The agent requires API keys for the following services:  
- [OpenAI](https://platform.openai.com/api-keys) / [Google Gemini](https://aistudio.google.com/app/apikey) — LLM provider
- [Exa](https://dashboard.exa.ai/api-keys) — Web search API

Set the required keys as environment variables in a `.env` file:
```env
GEMINI_API_KEY=your_gemini_key
OPENAI_API_KEY=your_openai_key
EXA_API_KEY=your_exa_key
```

> [!IMPORTANT]
> At least one LLM provider (+ Exa) is required.

### Installation

Install the package directly from GitHub:
```sh
pip install git+https://github.com/michelepatella/reco2gnizer.git
```

Alternatively, for development setup:
```sh
git clone https://github.com/michelepatella/reco2gnizer.git
cd reco2gnizer
pip install -e .
```

<p align="right"><a href="#readme-top">Top ↑</a></p>

## Usage

Example of how to run the agent:

```python
import asyncio
from reco2gnizer import graph
from reco2gnizer.state import InputState
from reco2gnizer.context import Context


async def main() -> None:
    """Example of how to run the agent.
      
    Returns:
        None
    """
  
    # Define data for the product you want to estimate its carbon
    # footprint as a dictionary
    product_data = {
        "name": "Mac Studio (M4 Max, 512GB SSD)"
    }

    # Create InputState for the agent
    input_state = InputState(
        product_data=product_data
    )
  
    # Define Context for the agent
    context = Context(
        model="google_genai:gemini-2.5-flash",
        # The name of the language model to use for the agent's main interactions
        # ('provider-name/model-name'). At the moment, the agent only supports all
        # the models provided by 'google_genai' and 'openai' providers.
        # Default: 'google_genai:gemini-2.5-flash'
        
        model_temperature=0.0,
        # The temperature to use for the language model (0.0-1.0).
        # Default: None
         
        search_web_max_results=10,
        # The maximum number of web search results to return for each query (1-100).
        # Default: 10
        
        search_web_type="auto",
        # The type of web search to perform ('fast', 'auto', 'deep').
        # Default: 'auto'
      
        search_web_max_calls=3,
        # The maximum number of web search calls the agent can make per run (> 0).
        # Default: 3
        
        enable_logging=True,
        # Whether to enable logging of agent execution to files (True/False).
        # Default: True
        
        logs_dir='logs',
        # The directory path for execution logs if logging is enabled.
        # Default: 'logs'

        logs_path='reco2gnizer.log'
        # The file path for the execution log if logging is enabled.
        # Default: 'reco2gnizer.log'
    )
  
    # Run agent
    result = await graph.ainvoke(
        input=input_state,
        context=context
    )

    # Display results
    print(result)

# Try out the example
asyncio.run(main())
```

The agent outputs a JSON having the following schema:

```text
{
  "co2e_kg": {
    "value": <float value of the carbon footprint in kg CO₂e>,
    "source": <either "official" if an official value was found, or "estimated" if it was computed>,
    "explanation": <explanation of how the value was obtained (max 300 characters)>
  }
}
```

<p align="right"><a href="#readme-top">Top ↑</a></p>

## License

Distributed under the [MIT License](https://github.com/michelepatella/reco2gnizer/blob/main/LICENSE).

<p align="right"><a href="#readme-top">Top ↑</a></p>

## Acknowledgments

Thanks to [LangChain](https://www.langchain.com/) for their [ReAct agent template](https://github.com/langchain-ai/react-agent), which served as the foundation for this implementation.

<p align="right"><a href="#readme-top">Top ↑</a></p>
