"""Order management tools."""

import uuid
from typing import Optional
from datetime import datetime
from langchain.tools import tool
from utils.data_loader import (
    load_inventory,
    load_suppliers,
    get_supplier_info,
    save_order,
    update_inventory_quantity,
    get_recent_orders as load_recent_orders,
)


@tool
def place_order(product_id: str, quantity: int, urgent: bool = False) -> dict:
    """Place an order for a specific product.
    
    Use this tool to create a purchase order for restocking inventory.
    This will create the order and update the inventory quantity.
    
    Args:
        product_id: The Product ID (e.g., 'P00001', 'P00123')
        quantity: Number of units to order (must be positive)
        urgent: Whether this is an urgent order requiring expedited delivery
        
    Returns:
        Dictionary containing:
        - order_id: Unique order identifier
        - product: Product name
        - quantity: Quantity ordered
        - total_cost: Total order cost
        - supplier: Supplier name
        - supplier_contact: Supplier contact information
        - expected_delivery: Delivery timeframe
        - status: Order status
        - message: Human-readable confirmation
    """
    try:
        if quantity <= 0:
            return {
                "success": False,
                "message": "Quantity must be positive",
                "error": "Invalid quantity"
            }
        
        inventory = load_inventory()
        suppliers = load_suppliers()
        
        # Find product
        product = inventory[inventory['Product_ID'] == product_id]
        if product.empty:
            return {
                "success": False,
                "message": f"Product {product_id} not found in inventory",
                "error": "Product not found"
            }
        
        product = product.iloc[0]
        supplier_info = get_supplier_info(product['Supplier'], suppliers)
        
        # Calculate delivery time
        delivery_days = supplier_info.get('Delivery_Days', 7) if supplier_info else 7
        if urgent and supplier_info and supplier_info.get('Express_Available'):
            delivery_days = delivery_days // 2
        
        # Create order
        total_bill = quantity * product['Cost_Price']
        order_id = str(uuid.uuid4())
        
        order = {
            "Order_ID": order_id,
            "Product_ID": product['Product_ID'],
            "Product_Name": product['Product_Name'],
            "Supplier": product['Supplier'],
            "Supplier_Contact": supplier_info.get('Contact_Phone', 'N/A') if supplier_info else 'N/A',
            "Supplier_Email": supplier_info.get('Contact_Email', 'N/A') if supplier_info else 'N/A',
            "Current_Stock": int(product['Quantity_In_Stock']),
            "Ordered_Quantity": int(quantity),
            "Total_Bill": float(total_bill),
            "Order_Status": "CONFIRMED",
            "Order_Date": datetime.now().isoformat(),
            "Expected_Delivery": f"{delivery_days} days"
        }
        
        # Save order
        save_order(order)
        
        # Update inventory (add expected quantity)
        update_inventory_quantity(product_id, quantity)
        
        return {
            "success": True,
            "order_id": order_id,
            "product": product['Product_Name'],
            "product_id": product['Product_ID'],
            "quantity": int(quantity),
            "unit_price": float(product['Cost_Price']),
            "total_cost": float(total_bill),
            "supplier": product['Supplier'],
            "supplier_contact": order['Supplier_Contact'],
            "expected_delivery": f"{delivery_days} days",
            "status": "CONFIRMED",
            "current_stock": int(product['Quantity_In_Stock']),
            "new_stock_after_delivery": int(product['Quantity_In_Stock']) + quantity,
            "message": f"Order confirmed: {quantity} units of {product['Product_Name']} from {product['Supplier']} for ${total_bill:.2f}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "message": f"Error placing order: {str(e)}",
            "error": str(e)
        }


@tool
def get_recent_orders(limit: int = 10, status_filter: Optional[str] = None) -> dict:
    """Retrieve recent orders from the system.
    
    Use this tool to check order history, delivery status, or track purchases.
    
    Args:
        limit: Maximum number of orders to return (default: 10)
        status_filter: Optional filter by status (PENDING, CONFIRMED, DELIVERED, CANCELLED)
        
    Returns:
        Dictionary containing:
        - count: Number of orders returned
        - orders: List of order details
        - message: Summary message
    """
    try:
        orders = load_recent_orders(limit)
        
        # Apply status filter if provided
        if status_filter:
            orders = [o for o in orders if o.get('Order_Status', '').upper() == status_filter.upper()]
        
        return {
            "count": len(orders),
            "orders": orders,
            "message": f"Retrieved {len(orders)} recent order(s)" + 
                      (f" with status {status_filter}" if status_filter else "")
        }
    
    except Exception as e:
        return {
            "count": 0,
            "orders": [],
            "message": f"Error retrieving orders: {str(e)}",
            "error": str(e)
        }
