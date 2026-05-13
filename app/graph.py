from langgraph.graph import StateGraph, END
from app.state import AgentState, QualifierSchema
from app.tools import create_crm_lead
from app.vector_store import search_properties
from langchain_openrouter import ChatOpenRouter
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
import os

# --- Node Definitions ---

async def qualifier_node(state: AgentState):
    """
    The Profiler Agent.
    Uses Structured Output to extract budget, location, and timeline.
    If fields are missing, it formulates the next question.
    """
    llm = ChatOpenRouter(model="meta-llama/llama-3.1-8b-instruct", api_key=os.getenv("OPENROUTER_API_KEY"))
    
    # 1. Try to extract fields from the conversation history
    extractor = llm.with_structured_output(QualifierSchema)
    
    # We pass the conversation history to the extractor
    extracted: QualifierSchema = await extractor.ainvoke(state["messages"])
    
    # Update state with extracted fields (only if they are not None and not already present)
    updates = {}
    if extracted.budget_min and not state.get("budget_min"):
        updates["budget_min"] = extracted.budget_min
    if extracted.budget_max and not state.get("budget_max"):
        updates["budget_max"] = extracted.budget_max
    if extracted.desired_location and not state.get("desired_location"):
        updates["desired_location"] = extracted.desired_location
    if extracted.timeline and not state.get("timeline"):
        updates["timeline"] = extracted.timeline
    if extracted.property_type_preference and not state.get("property_type_preference"):
        updates["property_type_preference"] = extracted.property_type_preference
    
    # Apply updates to current state view to check what is still missing
    current_state = {**state, **updates}
    
    # 2. Check for required fields
    missing_fields = []
    if not current_state.get("budget_max"): missing_fields.append("budget")
    if not current_state.get("desired_location"): missing_fields.append("desired location")
    if not current_state.get("property_type_preference"): missing_fields.append("property type preference")
    
    if not missing_fields:
        updates["ready_to_sync"] = True
        return updates
    
    # 3. Generate the next question
    system_prompt = f"""You are a helpful real estate assistant.
    Your goal is to qualify the lead by gathering their requirements.
    Currently, we are missing the following information: {', '.join(missing_fields)}.
    Please ask a polite, conversational question to gather this missing information.
    Do not ask for all of them at once, ask for one or two naturally.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = await llm.ainvoke(messages)
    
    updates["messages"] = [response]
    return updates

async def researcher_node(state: AgentState):
    """
    The Market Research Agent.
    Uses search tools to find market insights.
    """
    # Assuming TAVILY_API_KEY is set in the environment
    tool = TavilySearchResults(max_results=2)
    
    location = state.get("desired_location", "the city")
    query = f"Current real estate market trends and property prices in {location}"
    
    updates = {}
    try:
        results = tool.invoke({"query": query})
        updates["market_insights"] = str(results)
    except Exception as e:
        updates["market_insights"] = f"Could not fetch market insights: {str(e)}"
        
    return updates

async def concierge_node(state: AgentState):
    """
    The Concierge Agent.
    Uses RAG (Vector Store) to find matching properties based on the extracted fields.
    """
    budget = state.get("budget_max", "")
    location = state.get("desired_location", "")
    prop_type = state.get("property_type_preference", "")
    
    # Formulate a semantic search query
    query = f"{prop_type} in {location} under {budget} BDT"
    
    updates = {}
    try:
        top_props = search_properties(query, n_results=3)
        updates["top_properties"] = top_props
        
        # If properties found, format them into a message
        if top_props:
            prop_descriptions = "\n".join([p["description"] for p in top_props])
            system_msg = SystemMessage(content=f"Found these matching properties from our inventory:\n{prop_descriptions}")
            updates["messages"] = [system_msg]
        else:
            system_msg = SystemMessage(content="No exact matching properties found in inventory at this moment.")
            updates["messages"] = [system_msg]
    except Exception as e:
        system_msg = SystemMessage(content=f"Error searching inventory: {str(e)}")
        updates["messages"] = [system_msg]
        
    return updates

async def crm_sync_node(state: AgentState):
    """
    The CRM Connector.
    Pushes the structured JSON to the CRM via REST API.
    """
    # 1. Execute the tool to create the lead
    result = create_crm_lead.invoke({
        "budget_min": state.get("budget_min") or 0,
        "budget_max": state.get("budget_max") or 0,
        "desired_location": state.get("desired_location") or "Unknown",
        "property_type": state.get("property_type_preference") or "apartment"
    })
    
    updates = {}
    
    # 2. Handle the response and store lead_id
    if "error" not in result:
        # Assuming result contains an 'id' based on API_DOCUMENTATION.md
        lead_id = result.get("id")
        updates["lead_id"] = lead_id
        
        # Add a success message to the state so the Concierge or final output knows it worked
        system_msg = SystemMessage(content=f"Successfully synced lead to CRM. Lead ID: {lead_id}")
        updates["messages"] = [system_msg]
    else:
        system_msg = SystemMessage(content=f"Failed to sync to CRM. Error: {result['error']}")
        updates["messages"] = [system_msg]
        
    return updates

# --- Routing Logic (Supervisor) ---

def after_qualifier_router(state: AgentState):
    """
    Decides where to go after the qualifier node.
    """
    if state.get("ready_to_sync"):
        return "crm_sync"
    return END

# --- Graph Construction ---

builder = StateGraph(AgentState)

# Add Nodes
builder.add_node("qualifier", qualifier_node)
builder.add_node("researcher", researcher_node)
builder.add_node("concierge", concierge_node)
builder.add_node("crm_sync", crm_sync_node)

# Add Edges
# Start with the qualifier node to process the incoming message
builder.set_entry_point("qualifier")

# After qualifier, we either go to crm_sync or END (wait for user)
builder.add_conditional_edges(
    "qualifier",
    after_qualifier_router,
    {
        "crm_sync": "crm_sync",
        END: END
    }
)

# Other nodes also go to END for now
builder.add_edge("researcher", END)
builder.add_edge("concierge", END)
builder.add_edge("crm_sync", END)

# Compile the graph
# LangGraph Server will automatically hook up the checkpointer specified in langgraph.json
# We add an interrupt before the CRM sync to allow a human to review the qualified lead.
graph = builder.compile(interrupt_before=["crm_sync"])
