"""Output formatting utilities."""

from typing import Any


def format_order_confirmation(order: dict) -> str:
    """Format an order confirmation for display.
    
    Args:
        order: Order dictionary with details
        
    Returns:
        Formatted string for console output
    """
    return f"""
{'='*50}
ORDER CONFIRMED
{'='*50}
Product:          {order.get('Product_Name', 'N/A')}
Product ID:       {order.get('Product_ID', 'N/A')}
Quantity:         {order.get('Ordered_Quantity', 0)} units
Current Stock:    {order.get('Current_Stock', 0)} units
Supplier:         {order.get('Supplier', 'N/A')}
Contact:          {order.get('Supplier_Contact', 'N/A')}
Total Cost:       ${order.get('Total_Bill', 0):.2f}
Expected:         {order.get('Expected_Delivery', 'N/A')}
Order ID:         {order.get('Order_ID', 'N/A')[:8]}...
Status:           {order.get('Order_Status', 'N/A')}
{'='*50}
"""


def format_inventory_report(report_data: dict) -> str:
    """Format an inventory report for display.
    
    Args:
        report_data: Dictionary containing report information
        
    Returns:
        Formatted string for console output
    """
    output = f"""
{'='*60}
📊 INVENTORY REPORT
{'='*60}
Total Products:        {report_data.get('total_products', 0)}
Low Stock Items:       {report_data.get('total_low_stock', 0)}
Critical Items (<50):  {report_data.get('critical_items', 0)}
Estimated Reorder:     ${report_data.get('estimated_reorder_cost', 0):,.2f}
{'='*60}
"""
    
    if 'items' in report_data and report_data['items']:
        output += "\n⚠️  LOW STOCK ITEMS:\n"
        for item in report_data['items'][:10]:  # Show first 10
            output += f"  • {item['Product_Name']}: {item['Quantity_In_Stock']} units (Supplier: {item['Supplier']})\n"
    
    return output


def format_product_list(products: list[dict], max_items: int = 15) -> str:
    """Format a list of products for display.
    
    Args:
        products: List of product dictionaries
        max_items: Maximum number of products to display
        
    Returns:
        Formatted string
    """
    if not products:
        return "No products found."
    
    output = f"\nFound {len(products)} product(s):\n"
    output += "-" * 60 + "\n"
    
    for product in products[:max_items]:
        output += f"• {product.get('Product_Name', 'Unknown')} (ID: {product.get('Product_ID', 'N/A')})\n"
        output += f"  Stock: {product.get('Quantity_In_Stock', 0)} units | "
        output += f"Supplier: {product.get('Supplier', 'N/A')} | "
        output += f"Price: ${product.get('Cost_Price', 0):.2f}\n"
    
    if len(products) > max_items:
        output += f"\n... and {len(products) - max_items} more items\n"
    
    return output
