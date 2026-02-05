# LangChain-Powered Grocery Inventory Agent

A production-grade grocery inventory management system built with **LangChain**, **LangGraph**, and **Ollama** for local AI processing.

## 🎯 Features

### Core LangChain Components
- ✅ **Agents**: ReAct pattern with automatic tool routing
- ✅ **Models**: Dynamic model selection (gemma3:1b for simple queries, glm-4.6:cloud for complex analysis)
- ✅ **Messages**: Standardized message types with conversation history
- ✅ **Tools**: 5 specialized tools with automatic schema generation
- ✅ **Short-term Memory**: Conversation persistence with context injection
- ✅ **Streaming**: Real-time token and tool call streaming
- ✅ **Structured Output**: Pydantic validation for orders and reports

### Capabilities
🔍 **Inventory Management**
- Search products by name, category, or keyword
- Check stock levels in real-time
- Track 1000+ products across multiple categories
- Automatic low-stock alerts (<50 units)

📦 **Order Processing**
- Place orders with automatic supplier routing
- Order tracking and status updates
- Cost calculation and delivery estimation
- Inventory update after order placement

📊 **Analytics & Reporting**
- Generate low-stock reports with recommendations
- Inventory value and trend analysis
- Supplier performance tracking
- Actionable insights for restocking

## 🏗️ Architecture

```
Sales_Agent/
├── agent_core.py              # Main agent initialization with create_agent()
├── main.py                    # CLI entry point with streaming
├── tools/                     # LangChain tools (@tool decorator)
│   ├── inventory_tools.py     # search_inventory, generate_low_stock_report
│   ├── order_tools.py         # place_order, get_recent_orders
│   └── supplier_tools.py      # get_supplier_details
├── models/                    # Data models & schemas
│   ├── state.py               # GroceryAgentState (custom state)
│   └── schemas.py             # Pydantic models (OrderConfirmation, etc.)
├── middleware/                # Agent middleware
│   ├── error_handling.py      # Graceful error handling
│   ├── context_injection.py   # Real-time inventory context
│   └── model_routing.py       # Dynamic model selection
├── utils/                     # Utilities
│   ├── data_loader.py         # CSV data operations
│   └── formatters.py          # Output formatting
└── [CSV data files]           # Inventory, orders, suppliers
```

## 🚀 Quick Start

### Prerequisites

1. **Python 3.10+**
2. **Ollama** installed and running locally
3. **Models downloaded**:
   ```bash
   ollama pull gemma3:1b
   ollama pull glm-4.6:cloud
   ```

### Installation

1. **Create virtual environment**:
   ```bash
   cd Sales_Agent
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment** (optional):
   Create a `.env` file:
   ```env
   OLLAMA_URL=http://localhost:11434
   BASE_MODEL=gemma3:1b
   ADVANCED_MODEL=glm-4.6:cloud
   OLLAMA_TEMPERATURE=0.3
   ```

### Running the Agent

```bash
python main.py
```

## 💬 Usage Examples

### Inventory Queries
```
You: What's the current stock of milk?
Agent: [Uses search_inventory tool] We have Whole Milk with 318 units in stock...

You: Show me all low stock items
Agent: [Uses generate_low_stock_report] Found 23 items below 50 units...
```

### Order Placement
```
You: Order 100 units of product P00001
Agent: [Uses place_order tool] Order confirmed! 100 units of Pickles - Premium 
       from Metro Wholesale. Total cost: $2,308.00. Expected delivery: 3 days.
```

### Analysis Queries (Uses Advanced Model)
```
You: Analyze the inventory and give me recommendations
Agent: [Switches to glm-4.6:cloud] Based on the current inventory analysis...
       - 23 items require immediate attention
       - Estimated reorder cost: $12,450
       - Top priority: Granola Bars (only 7 units)
```

### Supplier Information
```
You: Tell me about Metro Wholesale
Agent: [Uses get_supplier_details] Metro Wholesale
       Contact: +1-555-0123
       Delivery: 3 days
       Express available: Yes
```

## 🔧 Technical Details

### Dynamic Model Routing

The agent automatically selects the appropriate model:

**gemma3:1b** (Fast Model) - Used for:
- Simple lookups and queries
- Direct tool calls
- Basic inventory checks

**glm-4.6:cloud** (Advanced Model) - Used for:
- Analysis and reporting
- Multi-step reasoning
- Long conversations (>10 messages)
- Complex queries with multiple conditions

### Tool Architecture

All tools use the `@tool` decorator for automatic schema generation:

```python
@tool
def search_inventory(query: str, category: Optional[str] = None) -> dict:
    """Search for products in inventory.
    
    Args:
        query: Product name or keyword
        category: Optional category filter
    
    Returns:
        Dictionary with matching products
    """
    # Implementation
```

### Middleware Pipeline

1. **Error Handling**: Catches and formats tool errors
2. **Context Injection**: Adds real-time inventory stats
3. **Model Routing**: Selects appropriate model based on complexity

### Memory & State

The agent uses `GroceryAgentState` with:
- `messages`: Conversation history (automatic)
- `session_id`: User session tracking
- `context`: Real-time inventory metrics
- `pending_orders`: Orders awaiting confirmation
- `user_preferences`: User-specific settings

## 📊 Monitoring & Debugging

### Verbose Mode

Enable detailed logging:
```python
agent = create_grocery_agent(verbose=True)
```

### Tool Call Visibility

Tool calls are shown in real-time:
```
🔧 Using tool: search_inventory
🔧 Using tool: place_order
```

### Model Selection

Model routing decisions logged in console (optional).

## 🔄 Comparison: Old vs New

| Feature | Old Implementation | New LangChain Implementation |
|---------|-------------------|------------------------------|
| Tool Routing | Manual regex parsing | Automatic via model tool calling |
| Reasoning | Single-pass LLM | Multi-step ReAct loop |
| Model Selection | Static | Dynamic based on complexity |
| Memory | Manual JSON files | LangGraph state management |
| Error Handling | Basic try-catch | Middleware with user-friendly messages |
| Streaming | Basic text only | Tokens + tool calls + steps |
| Validation | None | Pydantic schemas |
| Extensibility | Hardcoded logic | Modular tools & middleware |

## 🛠️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_URL` | `http://localhost:11434` | Ollama server URL |
| `BASE_MODEL` | `gemma3:1b` | Fast model for simple queries |
| `ADVANCED_MODEL` | `glm-4.6:cloud` | Powerful model for analysis |
| `OLLAMA_TEMPERATURE` | `0.3` | Model temperature (0-1) |
| `INVENTORY_CSV` | `grocery_inventory.csv` | Inventory data file |
| `SUPPLIERS_CSV` | `suppliers.csv` | Supplier data file |
| `ORDER_CSV` | `stock_order.csv` | Orders data file |

### Agent Configuration

```python
agent = create_grocery_agent(
    use_dynamic_routing=True,  # Enable model routing
    enable_memory=True,        # Enable conversation persistence
    verbose=False              # Show detailed logs
)
```

## 📝 Development

### Adding New Tools

1. Create tool function in appropriate file:
   ```python
   @tool
   def my_new_tool(param: str) -> dict:
       """Tool description."""
       # Implementation
       return {"result": "data"}
   ```

2. Import in `tools/__init__.py`

3. Add to tools list in `agent_core.py`

### Adding Middleware

1. Create middleware in `middleware/`:
   ```python
   @wrap_tool_call
   def my_middleware(request, handler):
       # Pre-processing
       result = handler(request)
       # Post-processing
       return result
   ```

2. Add to middleware list in `agent_core.py`

## 🐛 Troubleshooting

### Issue: "Model not found"
**Solution**: Ensure models are downloaded:
```bash
ollama list  # Check available models
ollama pull gemma3:1b
ollama pull glm-4.6:cloud
```

### Issue: "Connection refused"
**Solution**: Start Ollama server:
```bash
ollama serve
```

### Issue: "Tool execution error"
**Solution**: Check CSV files exist and have correct format

### Issue: "Slow responses"
**Solution**: 
- Use dynamic routing (automatically uses fast model for simple queries)
- Check Ollama is using GPU acceleration
- Reduce `num_predict` in agent_core.py

## 📈 Performance

- **Simple queries**: ~1-2 seconds (gemma3:1b)
- **Complex analysis**: ~5-10 seconds (glm-4.6:cloud)
- **Tool execution**: <1 second (local CSV)
- **Memory usage**: ~2-4 GB (depending on model)

## 🤝 Contributing

This is a demonstration project showcasing LangChain best practices. Feel free to extend and customize for your needs.

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with:** LangChain 1.1+ • LangGraph 0.2+ • Ollama • Pydantic 2.0+ • Rich

**Last Updated:** February 5, 2026
