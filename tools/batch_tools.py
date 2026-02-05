"""Batch order processing tool."""

from typing import List
from langchain.tools import tool
from utils.data_loader import (
    load_inventory,
    load_suppliers,
    get_supplier_info,
    save_order,
    update_inventory_quantity,
)
import uuid
from datetime import datetime


@tool
def place_batch_orders(product_ids: List[str], quantities: List[int]) -> dict:
    """Place multiple orders at once for different products.
    
    Use this tool when you need to order multiple products simultaneously.
    This is more efficient than calling place_order multiple times.
    
    Args:
        product_ids: List of Product IDs to order (e.g., ['P00001', 'P00002'])
        quantities: List of quantities for each product (must match product_ids length)
        
    Returns:
        Dictionary containing:
        - success: Overall success status
        - orders_placed: Number of successful orders
        - orders_failed: Number of failed orders
        - results: List of individual order results
        - total_cost: Combined cost of all orders
        - message: Summary message
    """
    try:
        if len(product_ids) != len(quantities):
            return {
                "success": False,
                "message": "Number of product IDs must match number of quantities",
                "error": "Mismatched arrays"
            }
        
        inventory = load_inventory()
        suppliers = load_suppliers()
        
        results = []
        total_cost = 0.0
        orders_placed = 0
        orders_failed = 0
        
        for product_id, quantity in zip(product_ids, quantities):
            try:
                # Find product
                product = inventory[inventory['Product_ID'] == product_id]
                if product.empty:
                    results.append({
                        "product_id": product_id,
                        "success": False,
                        "message": f"Product {product_id} not found"
                    })
                    orders_failed += 1
                    continue
                
                product = product.iloc[0]
                supplier_info = get_supplier_info(product['Supplier'], suppliers)
                
                # Calculate costs
                unit_cost = quantity * product['Cost_Price']
                delivery_days = supplier_info.get('Delivery_Days', 7) if supplier_info else 7
                
                # Create order
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
                    "Total_Bill": float(unit_cost),
                    "Order_Status": "CONFIRMED",
                    "Order_Date": datetime.now().isoformat(),
                    "Expected_Delivery": f"{delivery_days} days"
                }
                
                # Save order and update inventory
                save_order(order)
                update_inventory_quantity(product_id, quantity)
                
                results.append({
                    "product_id": product_id,
                    "product_name": product['Product_Name'],
                    "success": True,
                    "order_id": order_id,
                    "quantity": quantity,
                    "cost": float(unit_cost),
                    "delivery_days": delivery_days,
                    "supplier": product['Supplier']
                })
                
                total_cost += unit_cost
                orders_placed += 1
                
            except Exception as e:
                results.append({
                    "product_id": product_id,
                    "success": False,
                    "message": f"Error: {str(e)}"
                })
                orders_failed += 1
        
        return {
            "success": orders_placed > 0,
            "orders_placed": orders_placed,
            "orders_failed": orders_failed,
            "results": results,
            "total_cost": total_cost,
            "message": f"Successfully placed {orders_placed} order(s), {orders_failed} failed. Total cost: ${total_cost:,.2f}"
        }
    
    except Exception as e:
        return {
            "success": False,
            "orders_placed": 0,
            "orders_failed": len(product_ids),
            "results": [],
            "total_cost": 0.0,
            "message": f"Batch order failed: {str(e)}",
            "error": str(e)
        }
