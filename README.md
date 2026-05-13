# Multi-Agent System: LangGraph Technical Specifications

## 1. System Vision (The "State" Approach)

The core of this system is the **AgentState**. In LangGraph, the conversation is treated as a shared state that evolves as different agents (nodes) process it. This replaces traditional "pass-the-message" architectures with a more robust "shared-context" model.

## 2. Multi-Agent Graph Design

The system will be structured as a **StateGraph** with specialized nodes.

### 2.1. The Supervisor (The Orchestrator)

* **Logic:** Uses a `Router` pattern to decide which node to visit next based on the user's message and the current `AgentState`.
* **Responsibility:** Evaluates if the current information in the state is sufficient to "Finish" or if another agent is needed.

### 2.2. The Profiler Agent (Node: `qualifier`)

* **Tech:** Uses **LangChain Structured Output** to extract entity fields (budget, location, timeline).
* **Behavior:** If fields are missing in the state, this node generates the next conversational question. If all fields are filled, it updates the state with a `ready_to_sync` flag.

### 2.3. The Market Research Agent (Node: `researcher`)

* **Tools:** Integrated with **TavilySearchResults** or **SerpAPI**.
* **Behavior:** Triggered when a lead asks about trends or when the Supervisor needs to verify if a lead's budget matches current market reality. It writes "Market Insights" into the state for the Concierge to use.

### 2.4. The CRM Connector (Node: `crm_sync`)

* **Tools:** Custom Python tools that wrap your CRM’s REST API.
* **Behavior:** A "leaf node" that executes once the state is validated. It pushes the structured JSON to the CRM and returns the CRM's unique `lead_id` to the state.

---

## 3. LangGraph-Specific Functional Requirements

### 3.1. Persistence & Checkpointing

* **Requirement:** Use a `SqliteSaver` or `PostgresSaver` checkpointer within the LangGraph Server.
* **Purpose:** Messaging apps like WhatsApp are asynchronous. The agent may wait hours for a user to reply. Checkpoints allow the graph to "freeze" and "thaw" exactly where it left off based on the user's unique `thread_id` (phone number).

### 3.2. Human-in-the-Loop (Breakpoints)

* **Requirement:** Implement **Interrupts** before the `crm_sync` or `send_offer` nodes.
* **Purpose:** For high-value leads, the LangGraph Server can pause the graph execution. A human can review the "State" via the LangGraph UI, edit the data if necessary, and then click "Continue" to let the agent resume.

### 3.3. Tool Calling & Side Effects

* **Requirement:** All external interactions (Search, CRM API, Messaging) must be defined as **LangChain Tools**.
* **Benefit:** This allows the LLM to choose *when* to search the internet or *when* to update the CRM based on the conversation flow.

---

## 4. Integration Specifications (LangGraph Server)

### 4.1. The API Gateway (FastAPI/LangGraph Server)

While LangGraph Server handles the logic, you will need a lightweight entry point (or a LangGraph Cloud deployment) to:

1. **Receive Webhooks:** Accept incoming `POST` requests from Telegram/WhatsApp.
2. **Thread Mapping:** Map the sender's phone number to a LangGraph `thread_id`.
3. **Invoke Graph:** Call `app.ainvoke()` or `app.astream()` to start the multi-agent logic.

### 4.2. Vector Store (RAG) Integration

* **Implementation:** Use a **Vector Store Retriever** tool (e.g., Pinecone or Chroma) within the Concierge node.
* **Logic:** The node takes the "Qualified Preferences" from the state, queries the vector store for property matches, and appends the "Top 3 Properties" to the conversation context.

---

## 5. Technical Stack Requirements

* **Orchestration:** LangGraph (StateGraph, nodes, edges).
* **LLM Framework:** LangChain (ChatOpenAI, ChatAnthropic, or ChatGemini).
* **Data Extraction:** Pydantic (for defining the CRM-ready JSON schema).
* **Server Environment:** LangGraph Server (using `langgraph.json` configuration).
* **Persistence:** ChromaDB.