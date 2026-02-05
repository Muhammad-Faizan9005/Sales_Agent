# LangChain Agent Architecture

## High-Level Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                          USER INTERACTION                            │
│                         (Rich Console UI)                            │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ User Query
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          MAIN.PY                                     │
│  • Session management                                                │
│  • Streaming handler                                                 │
│  • Progress indicators                                               │
└────────────────────────────┬────────────────────────────────────────┘
                             │
                             │ agent.stream()
                             ▼
┌─────────────────────────────────────────────────────────────────────┐
│                       AGENT_CORE.PY                                  │
│  ┌───────────────────────────────────────────────────────────────┐ │
│  │   create_agent(                                                │ │
│  │     model = dynamic_model_selector,                           │ │
│  │     tools = [5 specialized tools],                            │ │
│  │     state_schema = GroceryAgentState,                         │ │
│  │     middleware = [error_handler, context, routing]            │ │
│  │   )                                                            │ │
│  └───────────────────────────────────────────────────────────────┘ │
└───┬───────────┬───────────┬───────────┬───────────┬────────────────┘
    │           │           │           │           │
    ▼           ▼           ▼           ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌───────────┐
│MODELS  │ │TOOLS   │ │MEMORY  │ │STREAMING│ │MIDDLEWARE │
└────────┘ └────────┘ └────────┘ └────────┘ └───────────┘
```

## Model Selection Flow

```
User Query
    │
    ▼
┌───────────────────────────────┐
│  Model Routing Middleware     │
│  (middleware/model_routing.py)│
└───────────────────────────────┘
    │
    ├─[Simple Query]──────────────► gemma3:1b (Fast, 1-2s)
    │   • "What's stock of X?"
    │   • "Show recent orders"
    │   • Direct lookups
    │
    └─[Complex Query]─────────────► glm-4.6:cloud (Powerful, 5-10s)
        • "Analyze inventory..."
        • "Provide recommendations..."
        • Multi-step reasoning
```

## ReAct Loop (Agent Reasoning)

```
┌──────────────────┐
│  User Question   │
└────────┬─────────┘
         │
         ▼
    ┌────────────────────┐
    │   THINK (Model)    │◄──────────────┐
    │  What tools needed?│               │
    └────────┬───────────┘               │
             │                            │
             ▼                            │
    ┌────────────────────┐               │
    │    ACT (Tools)     │               │
    │  Execute tool(s)   │               │
    └────────┬───────────┘               │
             │                            │
             ▼                            │
    ┌────────────────────┐               │
    │  OBSERVE (Results) │               │
    │  Review outputs    │               │
    └────────┬───────────┘               │
             │                            │
             ├─[Need more info?]─────────┘
             │     YES
             │
             └─[Have answer?]
                   YES
                    │
                    ▼
            ┌──────────────┐
            │Final Response│
            └──────────────┘
```

## Tool Execution Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│                      Tool Call Request                            │
│  {name: "search_inventory", args: {query: "milk"}}               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Error Handling Middleware                       │
│  (middleware/error_handling.py)                                   │
│  • Wraps tool execution                                           │
│  • Catches exceptions                                             │
│  • Returns user-friendly errors                                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                      Tool Execution                               │
│  (tools/inventory_tools.py, order_tools.py, etc.)                │
│                                                                    │
│  @tool decorator provides:                                        │
│  • Automatic schema generation                                    │
│  • Type validation                                                │
│  • Documentation                                                  │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                     Data Layer                                    │
│  (utils/data_loader.py)                                           │
│  • Load CSV files                                                 │
│  • Update inventory                                               │
│  • Save orders                                                    │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
┌──────────────────────────────────────────────────────────────────┐
│                   Tool Result                                     │
│  {found: 1, products: [...], message: "..."}                      │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                             ▼
                       Back to Model
```

## State Management

```
┌────────────────────────────────────────────────────────────┐
│              GroceryAgentState                              │
│  (models/state.py)                                          │
├────────────────────────────────────────────────────────────┤
│  messages: [...]           # Conversation history          │
│  session_id: "xxx"         # User session ID               │
│  user_preferences: {}      # User settings                 │
│  pending_orders: []        # Awaiting confirmation         │
│  context: {                # Real-time context             │
│    total_products: 1000,                                    │
│    low_stock_count: 23,                                     │
│    last_update: "..."                                       │
│  }                                                           │
└────────────────────────────────────────────────────────────┘
         ▲
         │ Updated by
         │
┌────────────────────────────────────────────────────────────┐
│        InventoryContextMiddleware                           │
│  (middleware/context_injection.py)                          │
│                                                              │
│  before_model():                                            │
│    • Loads current inventory                                │
│    • Calculates metrics                                     │
│    • Injects into state.context                            │
└────────────────────────────────────────────────────────────┘
```

## Streaming Architecture

```
Agent Execution
    │
    ├─► Token Stream ────────► "Analyzing" "inventory" "data" "..."
    │
    ├─► Tool Call Stream ────► "🔧 Using tool: search_inventory"
    │
    ├─► Step Stream ─────────► "Agent thinking..." "Executing tools..."
    │
    └─► Final Response ──────► Complete answer with all info
                                      │
                                      ▼
                               Rich Console Output
                               (colors, formatting)
```

## Middleware Chain

```
Request Flow:
    │
    ▼
┌─────────────────────────────────────┐
│  1. Error Handling Middleware       │
│     (Wraps everything)               │
│  ┌───────────────────────────────┐  │
│  │ 2. Context Injection Middleware│ │
│  │    (Updates state.context)     │ │
│  │ ┌──────────────────────────┐  │ │
│  │ │ 3. Model Routing         │  │ │
│  │ │    (Selects model)       │  │ │
│  │ │ ┌─────────────────────┐  │  │ │
│  │ │ │ 4. Model Execution  │  │  │ │
│  │ │ │   (LLM call)        │  │  │ │
│  │ │ └─────────────────────┘  │  │ │
│  │ └──────────────────────────┘  │ │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

## File Organization

```
Sales_Agent/
│
├── 📱 Entry Points
│   ├── main.py              # Interactive CLI
│   ├── test_agent.py        # Testing
│   └── agent_core.py        # Agent factory
│
├── 🔧 Tools (Business Logic)
│   ├── inventory_tools.py   # Search, reports
│   ├── order_tools.py       # Orders, tracking
│   └── supplier_tools.py    # Supplier info
│
├── 📊 Models (Data Structures)
│   ├── state.py             # Agent state schema
│   └── schemas.py           # Pydantic models
│
├── ⚙️ Middleware (Cross-cutting)
│   ├── error_handling.py    # Error recovery
│   ├── context_injection.py # Context management
│   └── model_routing.py     # Model selection
│
├── 🛠️ Utils (Helpers)
│   ├── data_loader.py       # CSV operations
│   └── formatters.py        # Output formatting
│
└── 📁 Data Files
    ├── grocery_inventory.csv
    ├── suppliers.csv
    └── stock_order.csv
```

## Key Design Patterns

### 1. Decorator Pattern (Tools)
```python
@tool
def my_tool(param: str) -> dict:
    """Automatic schema generation"""
    return {"result": data}
```

### 2. Middleware Pattern (Cross-cutting)
```python
@wrap_tool_call
def my_middleware(request, handler):
    # Pre-processing
    result = handler(request)
    # Post-processing
    return result
```

### 3. Strategy Pattern (Model Selection)
```python
if is_complex_query:
    use advanced_model
else:
    use base_model
```

### 4. State Pattern (Memory)
```python
class GroceryAgentState(TypedDict):
    messages: list  # Managed by LangGraph
    context: dict   # Custom state
```

---

**This architecture follows LangChain official best practices:**
- ✅ Modular design
- ✅ Separation of concerns
- ✅ Composable middleware
- ✅ Type-safe schemas
- ✅ Extensible tool system
