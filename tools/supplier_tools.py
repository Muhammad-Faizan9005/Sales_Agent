"""Supplier information tools."""

from typing import Optional
from langchain.tools import tool
from utils.data_loader import load_suppliers


@tool
def get_supplier_details(supplier_name: str) -> dict:
    """Get detailed information about a supplier.
    
    Use this tool to find supplier contact information, delivery times,
    and other supplier-specific details.
    
    Args:
        supplier_name: Name of the supplier (e.g., 'Metro Wholesale', 'Prime Vendors LLC')
        
    Returns:
        Dictionary containing:
        - supplier_name: Name of the supplier
        - contact_phone: Phone number
        - contact_email: Email address
        - delivery_days: Standard delivery time in days
        - express_available: Whether express delivery is available
        - payment_terms: Payment terms
        - message: Summary message
    """
    try:
        suppliers = load_suppliers()
        
        # Try exact match first
        supplier = suppliers[suppliers['Supplier_Name'].str.lower() == supplier_name.lower()]
        
        # If not found, try partial match
        if supplier.empty:
            supplier = suppliers[suppliers['Supplier_Name'].str.contains(supplier_name, case=False, na=False)]
        
        if supplier.empty:
            # Return list of available suppliers
            available = suppliers['Supplier_Name'].tolist()
            return {
                "found": False,
                "message": f"Supplier '{supplier_name}' not found",
                "available_suppliers": available,
                "error": "Supplier not found"
            }
        
        supplier_data = supplier.iloc[0].to_dict()
        
        return {
            "found": True,
            "supplier_name": supplier_data.get('Supplier_Name', 'N/A'),
            "contact_phone": supplier_data.get('Contact_Phone', 'N/A'),
            "contact_email": supplier_data.get('Contact_Email', 'N/A'),
            "delivery_days": supplier_data.get('Delivery_Days', 'N/A'),
            "express_available": supplier_data.get('Express_Available', False),
            "payment_terms": supplier_data.get('Payment_Terms', 'N/A'),
            "address": supplier_data.get('Address', 'N/A'),
            "rating": supplier_data.get('Rating', 'N/A'),
            "message": f"Found supplier information for {supplier_data.get('Supplier_Name', 'N/A')}"
        }
    
    except Exception as e:
        return {
            "found": False,
            "message": f"Error retrieving supplier information: {str(e)}",
            "error": str(e)
        }
