import operator
import json
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END

# --- 1. State Management: Define the agent's memory ---
class AgentState(TypedDict):
    # Input fields
    customer_name: str
    email: str
    query: str
    priority: int
    ticket_id: str
    
    # Intermediate data
    structured_data: dict
    entities: dict
    normalized_fields: dict
    enriched_records: dict
    flags: dict
    kb_results: list
    solution_score: int
    decision: str
    generated_response: str
    api_call_results: dict
    notification_status: str
    logs: List[str]
    current_stage: str

# --- 2. MCP Integration: Mock clients ---
class MCPClient:
    def _log_call(self, ability: str, server: str, state: AgentState) -> str:
        log_entry = f"Stage: {state['current_stage']} | Server: {server} | Ability: {ability}"
        print(log_entry)
        return log_entry

class AtlasClient(MCPClient):
    def extract_entities(self, state: AgentState) -> dict:
        state['current_stage'] = 'UNDERSTAND'
        state['logs'].append(self._log_call("extract_entities", "ATLAS", state))
        if "password" in state['query'].lower():
            return {"entities": {"product": "Account", "issue_type": "Password Reset"}}
        return {"entities": {"product": "General", "issue_type": "Inquiry"}}

    def enrich_records(self, state: AgentState) -> dict:
        state['current_stage'] = 'PREPARE'
        state['logs'].append(self._log_call("enrich_records", "ATLAS", state))
        return {"enriched_records": {"sla": "24 hours", "historical_tickets": 5, "customer_tier": "Gold"}}

    def knowledge_base_search(self, state: AgentState) -> dict:
        state['current_stage'] = 'RETRIEVE'
        state['logs'].append(self._log_call("knowledge_base_search", "ATLAS", state))
        return {"kb_results": [{"id": "KB123", "title": "How to Reset Your Password", "score": 95}]}

    def escalation_decision(self, state: AgentState) -> dict:
        state['current_stage'] = 'DECIDE'
        state['logs'].append(self._log_call("escalation_decision", "ATLAS", state))
        if state['solution_score'] < 90:
            return {"decision": "escalate"}
        return {"decision": "resolve"}

    def update_ticket(self, state: AgentState) -> dict:
        state['current_stage'] = 'UPDATE'
        state['logs'].append(self._log_call("update_ticket", "ATLAS", state))
        return {"ticket_id": state['ticket_id'], "status": "Escalated to Human Agent"}

    def execute_api_calls(self, state: AgentState) -> dict:
        state['current_stage'] = 'DO'
        state['logs'].append(self._log_call("execute_api_calls", "ATLAS", state))
        return {"api_call_results": {"password_reset_link_generated": "N/A"}}

    def trigger_notifications(self, state: AgentState) -> dict:
        state['current_stage'] = 'DO'
        state['logs'].append(self._log_call("trigger_notifications", "ATLAS", state))
        return {"notification_status": f"Email sent to {state['email']}"}

class CommonClient(MCPClient):
    def parse_request_text(self, state: AgentState) -> dict:
        state['current_stage'] = 'UNDERSTAND'
        state['logs'].append(self._log_call("parse_request_text", "COMMON", state))
        return {"structured_data": {"intent": "request_help", "text": state['query']}}

    def normalize_fields(self, state: AgentState) -> dict:
        state['current_stage'] = 'PREPARE'
        state['logs'].append(self._log_call("normalize_fields", "COMMON", state))
        return {"normalized_fields": {"ticket_id_std": state['ticket_id'].upper()}}

    def add_flags_calculations(self, state: AgentState) -> dict:
        state['current_stage'] = 'PREPARE'
        state['logs'].append(self._log_call("add_flags_calculations", "COMMON", state))
        if state['priority'] > 3:
            return {"flags": {"sla_risk": "High"}}
        return {"flags": {"sla_risk": "Low"}}

    def solution_evaluation(self, state: AgentState) -> dict:
        state['current_stage'] = 'DECIDE'
        state['logs'].append(self._log_call("solution_evaluation", "COMMON", state))
        if state.get("kb_results") and state["kb_results"][0]["score"] > 90:
            return {"solution_score": 95}
        return {"solution_score": 85}
        
    def response_generation(self, state: AgentState) -> dict:
        state['current_stage'] = 'CREATE'
        state['logs'].append(self._log_call("response_generation", "COMMON", state))
        kb_title = state['kb_results'][0]['title']
        response = f"Hello {state['customer_name']},\n\nBased on your query, here is an article that might help: '{kb_title}'.\n\nIf you still need help, please let us know.\n\nThanks,\nSupport Team"
        return {"generated_response": response}

# --- 3. Stage Modeling: Create node functions ---
atlas_client = AtlasClient()
common_client = CommonClient()

def execute_intake(state: AgentState) -> AgentState:
    state['current_stage'] = 'INTAKE'
    log_entry = "Stage: INTAKE | Server: None | Ability: accept_payload"
    print(log_entry)
    state['logs'] = [log_entry]
    return state

def execute_understand(state: AgentState) -> AgentState:
    structured_data = common_client.parse_request_text(state)
    entities = atlas_client.extract_entities(state)
    return {**structured_data, **entities}
    
def execute_prepare(state: AgentState) -> AgentState:
    normalized = common_client.normalize_fields(state)
    enriched = atlas_client.enrich_records(state)
    flags = common_client.add_flags_calculations(state)
    return {**normalized, **enriched, **flags}

def execute_retrieve(state: AgentState) -> AgentState:
    kb_data = atlas_client.knowledge_base_search(state)
    return kb_data

def execute_decide(state: AgentState) -> AgentState:
    score = common_client.solution_evaluation(state)
    state.update(score)
    decision = atlas_client.escalation_decision(state)
    return {**score, **decision}

def execute_update(state: AgentState) -> AgentState:
    updated_ticket_info = atlas_client.update_ticket(state)
    return {**updated_ticket_info, "generated_response": "Ticket has been escalated. A human agent will contact you shortly."}

def execute_create(state: AgentState) -> AgentState:
    response = common_client.response_generation(state)
    return response

def execute_do(state: AgentState) -> AgentState:
    api_calls = atlas_client.execute_api_calls(state)
    notifications = atlas_client.trigger_notifications(state)
    return {**api_calls, **notifications}

def execute_complete(state: AgentState) -> AgentState:
    state['current_stage'] = 'COMPLETE'
    log_entry = "Stage: COMPLETE | Server: None | Ability: output_payload"
    print(log_entry)
    state['logs'].append(log_entry)
    return state

def route_after_decide(state: AgentState):
    """Router function to choose the path after the DECIDE stage."""
    if state["decision"] == "escalate":
        return "escalate" # Also good practice to match the key exactly
    else:
        return "resolve" # This now matches the dictionary key

workflow = StateGraph(AgentState)
workflow.add_node("INTAKE", execute_intake)
workflow.add_node("UNDERSTAND", execute_understand)
workflow.add_node("PREPARE", execute_prepare)
workflow.add_node("RETRIEVE", execute_retrieve)
workflow.add_node("DECIDE", execute_decide)
workflow.add_node("UPDATE", execute_update)
workflow.add_node("CREATE", execute_create)
workflow.add_node("DO", execute_do)
workflow.add_node("COMPLETE", execute_complete)

workflow.set_entry_point("INTAKE")
workflow.add_edge("INTAKE", "UNDERSTAND")
workflow.add_edge("UNDERSTAND", "PREPARE")
workflow.add_edge("PREPARE", "RETRIEVE")
workflow.add_edge("RETRIEVE", "DECIDE")
workflow.add_conditional_edges("DECIDE", route_after_decide, {"escalate": "UPDATE", "resolve": "CREATE"})
workflow.add_edge("UPDATE", "DO")
workflow.add_edge("CREATE", "DO")
workflow.add_edge("DO", "COMPLETE")
workflow.add_edge("COMPLETE", END)

app = workflow.compile()

# --- 5. Demo Run ---
sample_input = {
    "customer_name": "Alice Wonderland",
    "email": "alice.w@example.com",
    "query": "Hi, I forgot my password and I need to reset it.",
    "priority": 4,
    "ticket_id": "TICKET-78901"
}

# Run the graph
final_state = app.invoke(sample_input)

# Print the final structured payload
print("\n--- FINAL PAYLOAD ---")
print(json.dumps(final_state, indent=2))