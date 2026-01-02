# Grocery Store Inventory Management Agent

An intelligent AI-powered grocery store inventory management system built with Python and LangChain. This conversational agent helps manage inventory, track orders, monitor stock levels, and interact with suppliers using natural language.

## Features

### 🤖 AI-Powered Conversational Interface
- Natural language interaction using Ollama's Gemma 3:1b model
- Persistent chat history across sessions
- Context-aware responses with inventory insights

### 📦 Inventory Management
- Track 1000+ products across multiple categories
- Real-time stock level monitoring
- Automatic low-stock detection (items with <50 units)
- Universal product matching algorithm with 80% confidence threshold

### 🛒 Order Management
- Natural language ordering: "order 200 units of milk"
- Automatic supplier assignment
- Order tracking with unique Order IDs
- Automatic inventory quantity updates after orders
- Order history with status tracking

### 👥 Supplier Management
- Complete supplier database with contact information
- 7 suppliers: Metro Wholesale, Prime Vendors LLC, Local Farms Co-op, Fresh Foods Inc, Daily Suppliers Co, National Distributors, Quality Foods Ltd
- Automatic supplier assignment based on product availability

### 📊 Analytics & Reporting
- Inventory summary statistics
- Recent order history
- Critical low-stock alerts
- Product search and filtering

## Prerequisites

- Python 3.13 or higher
- Ollama installed and running locally
- Gemma 3:1b model downloaded in Ollama

## Installation

1. **Clone or download the project**
   ```bash
   cd Sales_agent
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ensure Ollama is running**
   ```bash
   # Install Ollama from https://ollama.ai
   # Pull the Gemma model
   ollama pull gemma3:1b
   
   # Start Ollama server (if not already running)
   ollama serve
   ```

## Usage

1. **Start the agent**
   ```bash
   python grocery_agent.py
   ```

2. **Interact with the agent**
   
   **Query inventory:**
   - "What's the current stock of Apple Juice?"
   - "Show me all products with low stock"
   - "How many units of Tomatoes do we have?"
   
   **Place orders:**
   - "Order 200 units of Milk - Whole"
   - "I need 150 Apple Juice - Regular"
   - "Order 500 units of Chicken Breast"
   
   **Get information:**
   - "Show me recent orders"
   - "What items are critically low?"
   - "Give me inventory summary"
   
   **Exit:**
   - Type "exit", "quit", or "bye"

## Project Structure

```
Sales_agent/
├── grocery_agent.py           # Main application file
├── requirements.txt           # Python dependencies
├── .gitignore                # Git ignore rules
├── README.md                 # This file
├── grocery_inventory.csv     # Product inventory database
├── suppliers.csv             # Supplier contact information
├── stock_order.csv           # Order history and tracking
├── critical_low_stock.csv    # Auto-generated low stock alerts
├── agent_memory.json         # Persistent chat history
└── venv/                     # Virtual environment (not in git)
```

## How It Works

### Product Matching Algorithm
The system uses a two-strategy approach for accurate product matching:

1. **Exact Match**: Tries to match the exact product name first
2. **Word-Based Matching**: If no exact match, uses 80%+ word matching with confidence scoring
   - Cleans query text (removes special characters)
   - Calculates match percentage
   - Prefers longer matches to avoid confusion (e.g., "Apple Juice" vs "Apples")

### Order Processing Flow
1. User requests order in natural language
2. Agent parses intent and extracts product name and quantity
3. System finds product using universal matcher
4. Retrieves supplier information from database
5. Creates order record with unique Order ID
6. Updates inventory quantity automatically
7. Saves order to `stock_order.csv`

### Memory Persistence
- Chat history saved to `agent_memory.json`
- Loads previous conversations on startup
- Maintains context across sessions

## Key Technologies

- **LangChain**: Framework for LLM application development
- **Ollama**: Local LLM inference engine
- **Gemma 3:1b**: Lightweight language model
- **Pandas**: Data manipulation and CSV handling
- **Rich**: Terminal formatting and output styling

## Dependencies

```
langchain>=0.3.18
langchain-community>=0.3.17
langchain-ollama>=0.2.0
pandas>=2.0.0
python-dotenv
rich
numpy>=1.26.0
```

## Configuration

The agent uses the following default settings:
- **Ollama URL**: http://localhost:11434
- **Model**: gemma3:1b
- **Temperature**: 0 (deterministic responses)
- **Low Stock Threshold**: 50 units
- **Match Confidence Threshold**: 80%

## Data Files

### grocery_inventory.csv
Contains product information:
- Product_ID, Product_Name, Category, Quantity_In_Stock, Reorder_Level, Unit_Price, Supplier

### suppliers.csv
Contains supplier details:
- Supplier_Name, Contact_Phone, Contact_Email, Address, Payment_Terms, Delivery_Days

### stock_order.csv
Tracks all orders:
- Order_ID, Product_ID, Product_Name, Supplier, Supplier_Contact, Supplier_Email, Current_Stock, Ordered_Quantity, Total_Bill, Order_Status, Order_Date, Expected_Delivery

## Known Limitations

- Requires local Ollama installation
- Product matching works best with specific product names
- Currently supports single product orders (not batch orders)
- Limited to CSV-based storage (no database)

## Future Enhancements

- [ ] Web-based interface
- [ ] Multi-product batch ordering
- [ ] Advanced analytics dashboard
- [ ] Database integration (PostgreSQL/MySQL)
- [ ] Email notifications for low stock
- [ ] Barcode scanning support
- [ ] Invoice generation
- [ ] User authentication and roles

## Troubleshooting

**Issue**: Agent not responding
- **Solution**: Ensure Ollama is running (`ollama serve`)

**Issue**: "Model not found" error
- **Solution**: Pull the model (`ollama pull gemma3:1b`)

**Issue**: Product not found
- **Solution**: Check exact product name in `grocery_inventory.csv` or use partial name

**Issue**: Import errors
- **Solution**: Ensure all dependencies installed (`pip install -r requirements.txt`)

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available for educational purposes.

## Contact

For questions or support, please refer to the supplier contact information in `suppliers.csv`.

---

**Last Updated**: January 3, 2026
**Version**: 1.0.0
