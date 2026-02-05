# LangChain-Powered Grocery Inventory Management Agent

A **production-grade** grocery store inventory management system built with **LangChain**, **LangGraph**, and **Ollama** for local AI processing. This intelligent agent leverages official LangChain core components including agents, tools, memory, streaming, and structured output for robust inventory management.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-1.1+-green.svg)](https://python.langchain.com/)
[![Ollama](https://img.shields.io/badge/Ollama-Local-orange.svg)](https://ollama.ai/)

---

## 🎯 Features

### 🤖 **LangChain Agent Architecture**
- ✅ **ReAct Pattern**: Automatic multi-step reasoning with iterative tool calling
- ✅ **Dynamic Model Selection**: Switches between fast and powerful models based on query complexity
- ✅ **Tool Routing**: Automatic tool selection without manual parsing
- ✅ **Error Recovery**: Middleware-based error handling with user-friendly messages
- ✅ **Streaming**: Real-time token streaming and tool call visibility

### 📦 **Inventory Management**
- Track 1000+ products across multiple categories (Dairy, Meat, Produce, Bakery, etc.)
- Real-time stock level monitoring with context injection
- Automatic low-stock detection (configurable threshold)
- Smart product search with category filtering
- Comprehensive inventory reports with recommendations

### 🛒 **Order Processing**
- Place orders with automatic validation (Pydantic schemas)
- Automatic supplier routing and contact information
- Order tracking with unique IDs and status updates
- Real-time inventory updates after order placement
- Cost calculation and delivery estimation

### 👥 **Supplier Management**
- Complete supplier database with contact information
- 7 suppliers: Metro Wholesale, Prime Vendors LLC, Local Farms Co-op, Fresh Foods Inc, Daily Suppliers Co, National Distributors, Quality Foods Ltd
- Delivery time tracking and express options
- Payment terms and rating information

### 📊 **Analytics & Reporting**
- Generate comprehensive low-stock reports
- Inventory value calculations
- Reorder recommendations based on data
- Recent order history with filtering
- Real-time metrics in system prompts

---

## 🏗️ Architecture

### **Modular Structure**
```
Sales_Agent/
├── 📱 Entry Points
│   ├── main.py              # Interactive CLI with Rich UI
│   ├── test_agent.py        # Testing & validation
│   └── agent_core.py        # Agent factory & configuration
│
├── 🔧 Tools (Business Logic)
│   ├── inventory_tools.py   # search_inventory, generate_low_stock_report
│   ├── order_tools.py       # place_order, get_recent_orders
│   └── supplier_tools.py    # get_supplier_details
│
├── 📊 Models (Data Structures)
│   ├── state.py             # GroceryAgentState (conversation + context)
│   └── schemas.py           # Pydantic models (OrderConfirmation, etc.)
│
├── ⚙️ Middleware (Cross-cutting Concerns)
│   ├── error_handling.py    # Graceful error recovery
│   ├── context_injection.py # Real-time inventory context
│   └── model_routing.py     # Dynamic model selection
│
├── 🛠️ Utils (Helpers)
│   ├── data_loader.py       # CSV operations
│   └── formatters.py        # Output formatting
│
└── 📁 Data Files
    ├── grocery_inventory.csv     # 1000+ products
    ├── suppliers.csv             # Supplier database
    ├── stock_order.csv           # Order history
    └── critical_low_stock.csv    # Auto-generated alerts
```

### **LangChain Components Used**

| Component | Implementation | Purpose |
|-----------|---------------|---------|
| **Agents** | `create_agent()` with ReAct | Automatic tool routing & reasoning |
| **Models** | `ChatOllama` + dynamic routing | Fast & powerful model selection |
| **Messages** | `SystemMessage`, `HumanMessage`, etc. | Standardized conversation flow |
| **Tools** | `@tool` decorator (5 tools) | Automatic schema generation |
| **Memory** | `GroceryAgentState` + context | Conversation + inventory state |
| **Streaming** | Token & tool call streaming | Real-time user feedback |
| **Structured Output** | Pydantic schemas | Type-safe validation |

---

## 🚀 Quick Start

### **Prerequisites**

- **Python 3.10+**
- **Ollama** installed and running
- **Models downloaded**:
  ```bash
  ollama pull gpt-oss:20b-cloud   # Fast base model with tool support
  ollama pull glm-4.6:cloud       # Powerful model for complex queries
  ```

### **Installation**

1. **Navigate to project**:
   ```bash
   cd Sales_Agent
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Ollama is running**:
   ```bash
   curl http://localhost:11434/api/version
   ```

### **Running the Agent**

```bash
# Test the agent
python test_agent.py

# Run interactive mode
python main.py
```

---

## 💬 Usage Examples

### **Simple Queries** (Uses fast model: gpt-oss:20b-cloud)
```
You: How many products do we have?
Agent: We currently have 1000 products in inventory...

You: What's the stock of milk?
Agent: 🔧 Using tool: search_inventory
       Found Whole Milk - Family Size with 318 units in stock...

You: Show recent orders
Agent: 🔧 Using tool: get_recent_orders
       Retrieved 10 recent orders...
```

### **Complex Analysis** (Uses powerful model: glm-4.6:cloud)
```
You: Analyze the inventory and provide comprehensive recommendations
Agent: 🔧 Using tool: generate_low_stock_report
       📊 Based on analysis of 1000+ products:
       - 23 items require immediate attention
       - Estimated reorder cost: $12,450
       - Most urgent: Granola Bars (only 7 units)
       ...
```

### **Order Placement**
```
You: Order 100 units of product P00001
Agent: 🔧 Using tool: place_order
       ✅ Order confirmed!
       
       ══════════════════════════════════════════════════
       ORDER CONFIRMED
       ══════════════════════════════════════════════════
       Product:          Pickles - Premium
       Quantity:         100 units
       Supplier:         Metro Wholesale
       Total Cost:       $2,308.00
       Expected:         3 days
       ══════════════════════════════════════════════════
```

### **Supplier Information**
```
You: Tell me about Metro Wholesale
Agent: 🔧 Using tool: get_supplier_details
       Metro Wholesale
       Contact: +1-555-0123
       Email: contact@metrowholesale.com
       Delivery: 3 days (express available)
       Rating: 4.5/5
```

---

## 🔧 Configuration

### **Environment Variables**

Create a `.env` file (optional):
```env
OLLAMA_URL=http://localhost:11434
BASE_MODEL=gpt-oss:20b-cloud
ADVANCED_MODEL=glm-4.6:cloud
OLLAMA_TEMPERATURE=0.3

INVENTORY_CSV=grocery_inventory.csv
SUPPLIERS_CSV=suppliers.csv
ORDER_CSV=stock_order.csv
CRITICAL_LOW_STOCK_CSV=critical_low_stock.csv
```

### **Agent Configuration**

In `agent_core.py`:
```python
agent = create_grocery_agent(
    use_dynamic_routing=True,  # Enable smart model selection
    enable_memory=True,        # Conversation persistence
    verbose=False              # Show detailed logs
)
```

### **Dynamic Model Routing**

The agent automatically selects models based on query complexity:

**Fast Model (gpt-oss:20b-cloud)** - Used for:
- Simple lookups ("What's stock of X?")
- Direct queries
- Recent order checks
- Single tool calls

**Advanced Model (glm-4.6:cloud)** - Used for:
- Analysis queries ("analyze inventory")
- Multi-step reasoning
- Complex recommendations
- Long conversations (>10 messages)

---

## 🎓 Key Technologies

### **Core Stack**
- **[LangChain 1.1+](https://python.langchain.com/)**: Agent framework
- **[LangGraph 0.2+](https://langchain-ai.github.io/langgraph/)**: State management & workflows
- **[Ollama](https://ollama.ai/)**: Local LLM inference
- **[Pydantic 2.0+](https://docs.pydantic.dev/)**: Data validation
- **[Rich](https://rich.readthedocs.io/)**: Terminal UI

### **Models**
- **gpt-oss:20b-cloud**: Fast base model with tool calling support
- **glm-4.6:cloud**: Powerful model for complex analysis

### **Data Processing**
- **Pandas**: CSV operations and data manipulation
- **Python dotenv**: Environment configuration

---

## 📊 How It Works

### **1. Agent Execution Flow**

```
User Query
    │
    ▼
┌─────────────────────────┐
│  Model Routing          │ ← Selects appropriate model
│  (Middleware)           │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Context Injection      │ ← Adds inventory stats
│  (Middleware)           │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Agent (ReAct Loop)     │ ← Iterative reasoning
│  • Think                │
│  • Act (call tools)     │
│  • Observe              │
│  • Repeat if needed     │
└─────────────────────────┘
    │
    ▼
┌─────────────────────────┐
│  Tool Execution         │ ← With error handling
└─────────────────────────┘
    │
    ▼
Final Response
```

### **2. Tool Architecture**

All tools use the `@tool` decorator for automatic schema generation:

```python
@tool
def search_inventory(
    query: str,
    category: Optional[str] = None,
    low_stock_only: bool = False
) -> dict:
    """Search for products in inventory.
    
    Args:
        query: Product name or keyword
        category: Optional category filter
        low_stock_only: Filter items below threshold
        
    Returns:
        Dictionary with matching products
    """
    # Implementation
```

**Benefits:**
- Automatic schema generation for the model
- Type validation with annotations
- Self-documenting code
- Error handling via middleware

### **3. State Management**

The agent uses `GroceryAgentState` for tracking:

```python
class GroceryAgentState(TypedDict):
    messages: list           # Conversation history
    session_id: str         # User session ID
    user_preferences: dict  # User settings
    pending_orders: list    # Orders awaiting confirmation
    context: dict           # Real-time inventory metrics
```

Context is automatically updated before each model call with:
- Total products count
- Low stock items count
- Current stock levels
- Last update timestamp

---

## 📝 Available Tools

| Tool | Purpose | Example |
|------|---------|---------|
| `search_inventory` | Find products, check stock | "What's stock of milk?" |
| `generate_low_stock_report` | Analyze inventory | "Show low stock items" |
| `place_order` | Create purchase orders | "Order 100 units of P00001" |
| `get_recent_orders` | Check order history | "Show recent orders" |
| `get_supplier_details` | Supplier information | "Info about Metro Wholesale" |

---

## 🧪 Testing

```bash
# Run comprehensive tests
python test_agent.py

# Expected output:
# ✅ Agent initialized successfully!
# Test 1: How many products do we have in inventory?
# ✅ Test passed
# Test 2: Show me products with low stock
# ✅ Test passed
# Test 3: What's the stock level of milk?
# ✅ Test passed
```

---

## 🐛 Troubleshooting

### **Issue: "Model does not support tools"**
**Solution**: Use models with tool calling support:
```bash
ollama pull gpt-oss:20b-cloud
ollama pull qwen2.5:7b
ollama pull llama3.1:8b
```

### **Issue: "Connection refused"**
**Solution**: Start Ollama:
```bash
ollama serve
```

### **Issue: Import errors**
**Solution**: Reinstall dependencies:
```bash
pip install -r requirements.txt --force-reinstall
```

### **Issue: Slow responses**
**Solution**: 
- Dynamic routing automatically uses fast model for simple queries
- Check Ollama GPU acceleration is working
- Consider using smaller models for base_model

### **Issue: CSV file not found**
**Solution**: Ensure you're in the correct directory:
```bash
cd g:\Langchain\Sales_Agent
python main.py
```

---

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - 5-minute setup guide
- **[README_LANGCHAIN.md](README_LANGCHAIN.md)** - Detailed LangChain implementation guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture with diagrams
- **[IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md)** - Implementation summary
- **[LANGCHAIN_ENHANCEMENT_PLAN.md](LANGCHAIN_ENHANCEMENT_PLAN.md)** - Original design plan

---

## 🔄 Migration from Old Version

The old monolithic implementation (`grocery_agent.py`) has been replaced with a modular LangChain architecture:

| Old | New |
|-----|-----|
| Manual regex parsing | Automatic tool routing |
| Single model | Dynamic model selection |
| Manual JSON memory | LangGraph state management |
| Basic try-catch | Middleware error handling |
| One file (~600 lines) | Modular structure (~2000+ lines) |

All CSV data files remain compatible.

---

## 🚀 Future Enhancements

- [ ] SQLite persistence for long-term memory
- [ ] Web interface (Streamlit/Gradio)
- [ ] Batch order processing
- [ ] Real-time supplier API integration
- [ ] Multi-user authentication
- [ ] Email notifications for low stock
- [ ] Advanced analytics dashboard
- [ ] LangSmith integration for monitoring

---

## 🤝 Contributing

Contributions are welcome! This project demonstrates LangChain best practices.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

This project is open source and available for educational purposes.

---

## 💡 Tips

1. **Use verbose mode** during development:
   ```python
   agent = create_grocery_agent(verbose=True)
   ```

2. **Monitor tool calls** in real-time with streaming

3. **Customize system prompts** in `agent_core.py`

4. **Add new tools** easily:
   ```python
   @tool
   def my_new_tool(param: str) -> dict:
       """Tool description for the model."""
       return {"result": "data"}
   ```

5. **Adjust model routing** logic in `middleware/model_routing.py`

---

**Built with:** LangChain 1.1+ • LangGraph 0.2+ • Ollama • Pydantic 2.0+ • Rich  
**Last Updated:** February 5, 2026  
**Version:** 2.0.0 (LangChain Implementation)

---

🎉 **Enjoy your production-grade LangChain agent!**
