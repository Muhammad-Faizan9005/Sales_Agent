"""Core agent initialization and configuration."""

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain.agents import create_agent
from langchain_core.messages import SystemMessage

# Import tools
from tools import (
    search_inventory,
    generate_low_stock_report,
    place_order,
    get_recent_orders,
    get_supplier_details,
)

# Import middleware
from middleware import (
    handle_tool_errors,
    InventoryContextMiddleware,
    create_complexity_routing,
)

# Import models
from models import GroceryAgentState

# Load environment variables
load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
BASE_MODEL_NAME = os.getenv("BASE_MODEL", "gpt-oss:20b-cloud")
# BASE_MODEL_NAME = os.getenv("BASE_MODEL", "glm-4.6:cloud")
ADVANCED_MODEL_NAME = os.getenv("ADVANCED_MODEL", "glm-4.6:cloud")
TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.3"))


def get_system_prompt(context: dict = None) -> str:
    """Generate dynamic system prompt with current context.
    
    Args:
        context: Optional context dictionary with inventory stats
        
    Returns:
        System prompt string
    """
    base_prompt = """You are a professional grocery inventory management assistant.

Your role is to help manage grocery store inventory, process orders, and provide insights.

**CAPABILITIES:**
- Search and query inventory (products, stock levels, categories)
- Generate low-stock reports and recommendations
- Place orders with suppliers
- Retrieve order history and status
- Look up supplier information

**GUIDELINES:**
- Always use tools to get real-time data - never make up information
- Be proactive about alerting to low stock situations
- Confirm orders with specific details before execution
- Format numbers clearly (e.g., "150 units", "$2,456.50")
- Provide actionable recommendations
- Be concise but complete in your responses

**TOOL USAGE:**
- Use search_inventory for product queries and stock checks
- Use generate_low_stock_report for inventory analysis
- Use place_order to create purchase orders (confirm details first!)
- Use get_recent_orders to check order history
- Use get_supplier_details for supplier information
"""
    
    if context and "total_products" in context:
        context_info = f"""
**CURRENT INVENTORY STATUS:**
- Total Products: {context.get('total_products', 'N/A')}
- Low Stock Items: {context.get('low_stock_count', 'N/A')} (below 50 units)
- Total Stock Units: {context.get('total_stock_units', 'N/A'):,}
- Lowest Stock: {context.get('lowest_stock_product', 'N/A')} ({context.get('lowest_stock_quantity', 0)} units)
- Last Updated: {context.get('timestamp', 'Unknown')}

"""
        return base_prompt + context_info
    
    return base_prompt


def create_grocery_agent(
    use_dynamic_routing: bool = True,
    enable_memory: bool = True,
    verbose: bool = False
):
    """Create and configure the grocery inventory agent.
    
    Args:
        use_dynamic_routing: If True, use dynamic model selection based on complexity
        enable_memory: If True, enable conversation persistence
        verbose: If True, show detailed execution logs
        
    Returns:
        Configured LangChain agent
    """
    
    # Initialize models
    base_model = ChatOllama(
        model=BASE_MODEL_NAME,
        base_url=OLLAMA_URL,
        temperature=TEMPERATURE,
        num_predict=2048,  # Max tokens
    )
    
    advanced_model = ChatOllama(
        model=ADVANCED_MODEL_NAME,
        base_url=OLLAMA_URL,
        temperature=TEMPERATURE,
        num_predict=4096,  # More tokens for complex queries
    )
    
    # Prepare tools list
    tools = [
        search_inventory,
        generate_low_stock_report,
        place_order,
        get_recent_orders,
        get_supplier_details,
    ]
    
    # Prepare middleware
    middleware_list = [
        handle_tool_errors,
        InventoryContextMiddleware(),
    ]
    
    # Add dynamic routing if enabled
    if use_dynamic_routing:
        routing_middleware = create_complexity_routing(base_model, advanced_model)
        middleware_list.append(routing_middleware)
        model = base_model  # Default model
    else:
        model = base_model
    
    # Get initial system prompt
    system_prompt_text = get_system_prompt()
    
    # Create agent with all components
    agent = create_agent(
        model=model,
        tools=tools,
        state_schema=GroceryAgentState,
        middleware=middleware_list,
        system_prompt=SystemMessage(content=system_prompt_text),
    )
    
    if verbose:
        print(f"✅ Agent initialized")
        print(f"   Base Model: {BASE_MODEL_NAME}")
        print(f"   Advanced Model: {ADVANCED_MODEL_NAME}")
        print(f"   Dynamic Routing: {'Enabled' if use_dynamic_routing else 'Disabled'}")
        print(f"   Tools: {len(tools)}")
        print(f"   Middleware: {len(middleware_list)}")
    
    return agent


def get_agent_config(session_id: str = "default") -> dict:
    """Get configuration for agent invocation.
    
    Args:
        session_id: Session identifier for conversation tracking
        
    Returns:
        Configuration dictionary
    """
    return {
        "configurable": {
            "thread_id": session_id,
        },
        "recursion_limit": 50,  # Max iterations for ReAct loop
    }


if __name__ == "__main__":
    # Test agent initialization
    print("Testing agent initialization...")
    agent = create_grocery_agent(verbose=True)
    print("\n✅ Agent ready for use!")
