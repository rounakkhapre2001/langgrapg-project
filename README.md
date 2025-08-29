
# LangGraph Customer Support Agent

This project is an implementation of a multi-stage AI agent using the LangGraph library. The agent, named "Langie," models an 11-stage customer support workflow, demonstrating advanced concepts like state persistence, deterministic and non-deterministic routing, and mock client orchestration.

This project was completed as part of a coding task.

## Features

Graph-Based Workflow: The entire customer support flow is modeled as a directed acyclic graph (DAG) using LangGraph.

State Persistence: The agent maintains a consistent state (AgentState) that is passed and enriched through each node in the graph.

Deterministic & Non-Deterministic Routing: The agent executes most stages sequentially but uses conditional logic at the DECIDE stage to dynamically choose the next path (resolve or escalate) based on runtime data.

Mock Client Orchestration: The agent delegates tasks to mock AtlasClient (for external interactions) and CommonClient (for internal logic), simulating a microservice architecture.

Clear Logging: Every major action, including stage execution and client calls, is logged to the console for transparency.
## Project Structure

langgraph-project/

    ├── agent.py     # Main script with the LangGraph implementation
    ├── config.yaml  # Configuration file defining stages &abilities
    ├── requirements.txt  # Project dependencies        
    └── README.md         # This file
## ⚙️ Setup and Installation

Follow these steps to set up and run the project locally.

1. Clone the Repository
  git clone [Paste Your GitHub Repository URL Here]
cd langgraph-project

2. Create and Activate a Virtual Environment
It is highly recommended to use a virtual environment to manage project dependencies.

# Create the virtual environment
    python -m venv venv


# Activate on Windows
    venv\Scripts\activate


# Activate on macOS/Linux
     source venv/bin/activate

3. Install Dependencies
With the virtual environment active, install the required packages from the 
    requirements.txt file.

## ▶️ How to Run
Once the setup is complete, you can run the agent with a single command:

      python agent.py

Example Output:-

A successful run will display the step-by-step logs of the agent's execution, followed by the final structured JSON payload.

Stage: INTAKE | Server: None | Ability: accept_payload
Stage: UNDERSTAND | Server: COMMON | Ability: parse_request_text
Stage: UNDERSTAND | Server: ATLAS | Ability: extract_entities
Stage: PREPARE | Server: COMMON | Ability: normalize_fields
Stage: PREPARE | Server: ATLAS | Ability: enrich_records
Stage: PREPARE | Server: COMMON | Ability: add_flags_calculations
Stage: RETRIEVE | Server: ATLAS | Ability: knowledge_base_search
Stage: DECIDE | Server: COMMON | Ability: solution_evaluation
Stage: DECIDE | Server: ATLAS | Ability: escalation_decision
Stage: CREATE | Server: COMMON | Ability: response_generation
Stage: DO | Server: ATLAS | Ability: execute_api_calls
Stage: DO | Server: ATLAS | Ability: trigger_notifications
Stage: COMPLETE | Server: None | Ability: output_payload

  --- FINAL PAYLOAD ---                 
{
  "customer_name": "Alice Wonderland",
  "email": "alice.w@example.com",
  "query": "Hi, I forgot my password and I need to reset it.",
  ...
}
