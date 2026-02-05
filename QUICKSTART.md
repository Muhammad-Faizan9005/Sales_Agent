# Quick Start Guide - LangChain Grocery Agent

## Step 1: Verify Prerequisites

### Check Ollama is running:
```powershell
# In PowerShell or cmd
curl http://localhost:11434/api/version
```

You should see a JSON response with version info.

### Check models are available:
```powershell
ollama list
```

You should see:
- `gemma3:1b`
- `glm-4.6:cloud` (or similar model)

If not, download them:
```powershell
ollama pull gemma3:1b
ollama pull glm-4.6:cloud
```

## Step 2: Set Up Virtual Environment

```powershell
# Navigate to project
cd g:\Langchain\Sales_Agent

# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\activate

# Your prompt should now show (venv)
```

## Step 3: Install Dependencies

```powershell
pip install -r requirements.txt
```

This will install:
- langchain (1.1+)
- langgraph
- langchain-ollama
- pydantic
- rich
- pandas

## Step 4: Test the Agent

```powershell
python test_agent.py
```

This will run basic tests to ensure everything is working.

## Step 5: Run the Agent

```powershell
python main.py
```

You should see a welcome screen and be able to interact with the agent.

## Example Interactions

### Simple Query (Uses gemma3:1b):
```
You: What's the stock of milk?
Agent: 🔧 Using tool: search_inventory
       We have Whole Milk - Family Size with 318 units in stock...
```

### Complex Query (Uses glm-4.6:cloud):
```
You: Analyze the inventory and give me a comprehensive report with recommendations
Agent: 🔧 Using tool: generate_low_stock_report
       📊 Based on the analysis of 1000+ products...
```

### Order Placement:
```
You: Order 100 units of product P00001
Agent: 🔧 Using tool: place_order
       ✅ Order confirmed! 100 units of Pickles - Premium...
```

## Troubleshooting

### Issue: Models not found
```powershell
ollama pull gemma3:1b
ollama pull glm-4.6:cloud
```

### Issue: Connection refused
Start Ollama:
```powershell
ollama serve
```

### Issue: Import errors
Reinstall dependencies:
```powershell
pip install -r requirements.txt --force-reinstall
```

### Issue: CSV file not found
Make sure you're running from the Sales_Agent directory:
```powershell
cd g:\Langchain\Sales_Agent
python main.py
```

## Tips

1. **Use Ctrl+C to interrupt** long-running responses
2. **Type 'exit' or 'quit'** to close the agent
3. **Enable verbose mode** to see what the agent is doing:
   ```python
   # Edit agent_core.py
   agent = create_grocery_agent(verbose=True)
   ```

## Next Steps

1. Try different queries
2. Place test orders
3. Generate inventory reports
4. Explore the codebase in the modular structure
5. Add your own custom tools

Enjoy your LangChain-powered agent! 🎉
