"""Inventory management tools."""

import re
from typing import Optional
from langchain.tools import tool
from utils.data_loader import (
    load_inventory,
    update_critical_low_stock,
)


def find_product_by_name(user_query: str, inventory) -> Optional[dict]:
    """Find a product from inventory using smart matching.
    
    Args:
        user_query: User's query string
        inventory: Inventory dataframe
        
    Returns:
        Product row as dictionary or None if not found
    """
    query_lower = user_query.lower()
    
    # Remove common prefixes/suffixes
    query_clean = re.sub(
        r'\b(order|buy|get|need|want|check|show|quantity|of|the|a|an|items|units|pieces|more)\b',
        '', query_lower
    )
    query_clean = query_clean.strip()
    
    # Strategy 1: Exact product name match
    for _, row in inventory.iterrows():
        product_name_lower = row['Product_Name'].lower()
        if product_name_lower == query_clean or product_name_lower in query_lower:
            return row.to_dict()
    
    # Strategy 2: All product words must be present in query
    best_match = None
    best_score = 0
    
    for _, row in inventory.iterrows():
        product_name_lower = row['Product_Name'].lower()
        product_words = [w for w in product_name_lower.replace('-', ' ').split() if len(w) > 2]
        
        matches = sum(1 for prod_word in product_words 
                     if prod_word in query_clean or prod_word in query_lower)
        
        if len(product_words) > 0:
            match_percentage = matches / len(product_words)
            
            if match_percentage == 1.0:
                score = 100 + len(product_name_lower)
            elif match_percentage >= 0.8:
                score = 80 + matches
            else:
                score = matches * 10
            
            if score > best_score:
                best_score = score
                best_match = row.to_dict()
    
    if best_score >= 80:
        return best_match
    
    return None


@tool
def search_inventory(
    query: str,
    category: Optional[str] = None,
    low_stock_only: bool = False,
    threshold: int = 50
) -> dict:
    """Search for products in the grocery inventory.
    
    Use this tool to find products, check stock levels, or search by category.
    
    Args:
        query: Product name or keyword to search for (e.g., "milk", "chicken")
        category: Optional filter by category (Dairy, Meat, Produce, Bakery, etc.)
        low_stock_only: If True, only return items with stock below threshold
        threshold: Stock level threshold for low_stock_only filter (default: 50)
        
    Returns:
        Dictionary containing:
        - found: Number of matching products
        - products: List of product dictionaries with details
        - message: Human-readable summary
    """
    try:
        inventory = load_inventory()
        
        # Apply filters
        if category:
            inventory = inventory[inventory['Category'].str.lower() == category.lower()]
        
        if low_stock_only:
            inventory = inventory[inventory['Quantity_In_Stock'] < threshold]
        
        # Search by query
        if query and query.strip():
            query_lower = query.lower()
            mask = inventory['Product_Name'].str.lower().str.contains(query_lower, na=False) | \
                   inventory['Category'].str.lower().str.contains(query_lower, na=False)
            matches = inventory[mask]
        else:
            matches = inventory
        
        products = matches.to_dict('records')
        
        return {
            "found": len(products),
            "products": products[:20],  # Limit to 20 results
            "message": f"Found {len(products)} product(s) matching your search.",
            "filters_applied": {
                "category": category,
                "low_stock_only": low_stock_only,
                "threshold": threshold if low_stock_only else None
            }
        }
    
    except Exception as e:
        return {
            "found": 0,
            "products": [],
            "message": f"Error searching inventory: {str(e)}",
            "error": str(e)
        }


@tool
def generate_low_stock_report(threshold: int = 50) -> dict:
    """Generate a comprehensive report of products below stock threshold.
    
    Use this tool to identify products that need reordering.
    
    Args:
        threshold: Stock level threshold (default: 50 units)
        
    Returns:
        Dictionary containing:
        - total_low_stock: Count of low stock items
        - critical_items: Count of items below threshold
        - items: List of low-stock products with details
        - estimated_reorder_cost: Total cost to restock all items
        - recommendations: List of actionable recommendations
    """
    try:
        inventory = load_inventory()
        low_stock = inventory[inventory['Quantity_In_Stock'] < threshold]
        
        # Update critical low stock CSV
        critical_items = update_critical_low_stock(inventory, threshold)
        
        # Calculate reorder cost
        low_stock['reorder_needed'] = low_stock['Reorder_Level'] - low_stock['Quantity_In_Stock']
        low_stock['reorder_needed'] = low_stock['reorder_needed'].clip(lower=0)
        low_stock['reorder_cost'] = low_stock['reorder_needed'] * low_stock['Cost_Price']
        
        total_reorder_cost = low_stock['reorder_cost'].sum()
        
        # Generate recommendations
        recommendations = []
        if len(critical_items) > 0:
            recommendations.append(f"Immediate action needed for {len(critical_items)} critical items")
        
        # Find most urgent items (lowest stock)
        urgent = low_stock.nsmallest(5, 'Quantity_In_Stock')
        if not urgent.empty:
            recommendations.append(f"Most urgent: {urgent.iloc[0]['Product_Name']} (only {urgent.iloc[0]['Quantity_In_Stock']} units left)")
        
        # High-value reorders
        expensive = low_stock.nlargest(3, 'reorder_cost')
        if not expensive.empty and expensive.iloc[0]['reorder_cost'] > 1000:
            recommendations.append(f"High-cost reorder needed: {expensive.iloc[0]['Product_Name']} (${expensive.iloc[0]['reorder_cost']:.2f})")
        
        return {
            "total_low_stock": len(low_stock),
            "critical_items": len(critical_items),
            "items": low_stock[['Product_ID', 'Product_Name', 'Quantity_In_Stock', 
                               'Reorder_Level', 'Supplier', 'Cost_Price']].to_dict('records'),
            "estimated_reorder_cost": float(total_reorder_cost),
            "recommendations": recommendations,
            "message": f"Report generated: {len(low_stock)} items below threshold of {threshold} units"
        }
    
    except Exception as e:
        return {
            "total_low_stock": 0,
            "critical_items": 0,
            "items": [],
            "estimated_reorder_cost": 0.0,
            "recommendations": [],
            "message": f"Error generating report: {str(e)}",
            "error": str(e)
        }
