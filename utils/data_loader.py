"""Data loading utilities for CSV files."""

import os
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

INVENTORY_CSV = os.getenv("INVENTORY_CSV", "grocery_inventory.csv")
SUPPLIERS_CSV = os.getenv("SUPPLIERS_CSV", "suppliers.csv")
ORDER_CSV = os.getenv("ORDER_CSV", "stock_order.csv")
CRITICAL_LOW_STOCK_CSV = os.getenv("CRITICAL_LOW_STOCK_CSV", "critical_low_stock.csv")


def load_inventory() -> pd.DataFrame:
    """Load grocery inventory from CSV."""
    return pd.read_csv(INVENTORY_CSV)


def save_inventory(inventory_df: pd.DataFrame) -> None:
    """Save updated inventory back to CSV."""
    inventory_df.to_csv(INVENTORY_CSV, index=False)


def update_inventory_quantity(product_id: str, quantity_ordered: int) -> bool:
    """Update inventory quantity after an order is placed.
    
    Args:
        product_id: The Product ID to update
        quantity_ordered: Number of units ordered (will be added to stock)
        
    Returns:
        True if successful, False if product not found
    """
    inventory = load_inventory()
    mask = inventory['Product_ID'] == product_id
    
    if mask.any():
        current_qty = inventory.loc[mask, 'Quantity_In_Stock'].values[0]
        new_qty = current_qty + quantity_ordered
        inventory.loc[mask, 'Quantity_In_Stock'] = new_qty
        save_inventory(inventory)
        return True
    
    return False


def load_suppliers() -> pd.DataFrame:
    """Load suppliers from CSV."""
    return pd.read_csv(SUPPLIERS_CSV)


def get_supplier_info(supplier_name: str, suppliers_df: pd.DataFrame = None) -> dict:
    """Get supplier details from suppliers dataframe.
    
    Args:
        supplier_name: Name of the supplier
        suppliers_df: Optional suppliers dataframe (will load if not provided)
        
    Returns:
        Dictionary with supplier information or None if not found
    """
    if suppliers_df is None:
        suppliers_df = load_suppliers()
    
    supplier = suppliers_df[suppliers_df['Supplier_Name'] == supplier_name]
    if not supplier.empty:
        return supplier.iloc[0].to_dict()
    return None


def load_orders() -> pd.DataFrame:
    """Load orders from CSV, creating file if it doesn't exist."""
    if not os.path.exists(ORDER_CSV):
        df = pd.DataFrame(columns=[
            "Order_ID",
            "Product_ID",
            "Product_Name",
            "Supplier",
            "Current_Stock",
            "Ordered_Quantity",
            "Total_Bill",
            "Order_Status",
            "Order_Date"
        ])
        df.to_csv(ORDER_CSV, index=False)
        return df
    
    try:
        df = pd.read_csv(ORDER_CSV)
        if df.empty or len(df.columns) == 0:
            raise pd.errors.EmptyDataError
        return df
    except (pd.errors.EmptyDataError, pd.errors.ParserError):
        df = pd.DataFrame(columns=[
            "Order_ID",
            "Product_ID",
            "Product_Name",
            "Supplier",
            "Current_Stock",
            "Ordered_Quantity",
            "Total_Bill",
            "Order_Status",
            "Order_Date"
        ])
        df.to_csv(ORDER_CSV, index=False)
        return df


def save_order(order: dict) -> None:
    """Save a new order to the orders CSV.
    
    Args:
        order: Dictionary containing order details
    """
    df = load_orders()
    new_row = pd.DataFrame([order])
    
    if df.empty:
        df = new_row
    else:
        df = pd.concat([df, new_row], ignore_index=True)
    
    df.to_csv(ORDER_CSV, index=False)


def get_recent_orders(limit: int = 5) -> list[dict]:
    """Get most recent orders.
    
    Args:
        limit: Maximum number of orders to return
        
    Returns:
        List of order dictionaries
    """
    try:
        orders_df = load_orders()
        if orders_df.empty:
            return []
        
        orders_df['Order_Date'] = pd.to_datetime(orders_df['Order_Date'])
        recent = orders_df.sort_values('Order_Date', ascending=False).head(limit)
        return recent.to_dict('records')
    except Exception:
        return []


def update_critical_low_stock(inventory: pd.DataFrame, threshold: int = 50) -> pd.DataFrame:
    """Track items with quantity below threshold in separate CSV.
    
    Args:
        inventory: Inventory dataframe
        threshold: Stock level threshold (default: 50)
        
    Returns:
        DataFrame of critical low stock items
    """
    critical_items = inventory[inventory["Quantity_In_Stock"] < threshold].copy()
    critical_items.to_csv(CRITICAL_LOW_STOCK_CSV, index=False)
    return critical_items
