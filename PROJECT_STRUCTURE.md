```text
.
├── LICENSE                    <- License defining project usage rights
├── README.md                  <- Project overview, setup instructions, and usage examples
├── PROJECT_STRUCTURE.md       <- Project structure overview (this file)
├── pyproject.toml             <- Project configuration, dependencies, and build settings
├── .gitignore                 <- Files/folders ignored by Git
├── .pre-commit-config.yaml    <- Pre-commit hooks configuration
└── src
    └── reco2gnizer
        ├── __init__.py        <- Main `graph` agent exposed for external consumption
        ├── const.py           <- Global constants used throughout the project
        ├── context.py         <- Runtime configuration for the agent
        ├── graph.py           <- ReAct agent graph structure and execution logic
        ├── prompts.py         <- LLM prompts
        ├── state.py           <- Agent execution state
        └── tools.py           <- Available tools for the agent
