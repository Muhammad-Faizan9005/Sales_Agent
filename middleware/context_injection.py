"""Context injection middleware for providing inventory updates."""

from typing import Any
from datetime import datetime
from langchain.agents.middleware import AgentMiddleware
from models.state import GroceryAgentState
from utils.data_loader import load_inventory


class InventoryContextMiddleware(AgentMiddleware):
    """Middleware to inject current inventory context into agent state.
    
    This middleware updates the agent's context with fresh inventory statistics
    before each model call, ensuring the agent has up-to-date information.
    """
    
    state_schema = GroceryAgentState
    
    def before_model(self, state: GroceryAgentState, runtime) -> dict[str, Any] | None:
        """Inject inventory context before model is called.
        
        Args:
            state: Current agent state
            runtime: Runtime configuration
            
        Returns:
            Dictionary with updated context information
        """
        try:
            inventory = load_inventory()
            
            # Calculate key metrics
            total_products = len(inventory)
            low_stock_count = len(inventory[inventory['Quantity_In_Stock'] < 50])
            total_stock_units = int(inventory['Quantity_In_Stock'].sum())
            avg_stock = float(inventory['Quantity_In_Stock'].mean())
            
            # Find critical items
            lowest_stock = inventory.nsmallest(1, 'Quantity_In_Stock')
            lowest_product = lowest_stock.iloc[0]['Product_Name'] if not lowest_stock.empty else 'N/A'
            lowest_qty = int(lowest_stock.iloc[0]['Quantity_In_Stock']) if not lowest_stock.empty else 0
            
            # Categories and suppliers
            categories = inventory['Category'].unique().tolist()
            suppliers = inventory['Supplier'].unique().tolist()
            
            context = {
                "total_products": total_products,
                "low_stock_count": low_stock_count,
                "total_stock_units": total_stock_units,
                "avg_stock_per_product": round(avg_stock, 1),
                "lowest_stock_product": lowest_product,
                "lowest_stock_quantity": lowest_qty,
                "categories_count": len(categories),
                "suppliers_count": len(suppliers),
                "last_update": datetime.now().isoformat(),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            return {"context": context}
        
        except Exception as e:
            # If we can't load inventory, provide empty context
            return {
                "context": {
                    "error": str(e),
                    "last_update": datetime.now().isoformat()
                }
            }
