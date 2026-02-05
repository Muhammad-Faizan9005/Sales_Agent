"""Pydantic schemas for structured output validation."""

from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from typing import Optional


class OrderConfirmation(BaseModel):
    """Structured order confirmation response."""
    
    order_id: str = Field(..., description="Unique order identifier")
    product_name: str = Field(..., description="Name of the ordered product")
    product_id: str = Field(..., description="Product ID (e.g., P00001)")
    quantity: int = Field(..., gt=0, description="Quantity ordered")
    unit_price: float = Field(..., gt=0, description="Price per unit")
    total_cost: float = Field(..., gt=0, description="Total order cost")
    supplier: str = Field(..., description="Supplier name")
    supplier_contact: str = Field(..., description="Supplier phone/email")
    expected_delivery: str = Field(..., description="Expected delivery timeframe")
    order_status: str = Field(default="PENDING", description="Order status")
    order_timestamp: datetime = Field(default_factory=datetime.now, description="Order creation time")
    current_stock: int = Field(..., ge=0, description="Current stock level before order")
    
    @field_validator('total_cost')
    @classmethod
    def validate_total(cls, v: float, info) -> float:
        """Ensure total cost matches quantity * unit_price."""
        if 'quantity' in info.data and 'unit_price' in info.data:
            expected = info.data['quantity'] * info.data['unit_price']
            if abs(v - expected) > 0.01:
                raise ValueError(f"Total cost {v} doesn't match calculation {expected}")
        return v

    model_config = {
        "json_schema_extra": {
            "example": {
                "order_id": "abc123",
                "product_name": "Milk - Whole",
                "product_id": "P00001",
                "quantity": 50,
                "unit_price": 3.50,
                "total_cost": 175.00,
                "supplier": "Metro Wholesale",
                "supplier_contact": "+1-555-0123",
                "expected_delivery": "3 days",
                "order_status": "PENDING",
                "current_stock": 25
            }
        }
    }


class ProductSummary(BaseModel):
    """Individual product summary."""
    
    product_id: str = Field(..., description="Product ID")
    product_name: str = Field(..., description="Product name")
    current_stock: int = Field(..., ge=0, description="Current stock level")
    reorder_level: int = Field(..., ge=0, description="Recommended reorder level")
    supplier: str = Field(..., description="Supplier name")
    cost_to_restock: float = Field(..., ge=0, description="Cost to restock to reorder level")


class InventoryReport(BaseModel):
    """Comprehensive inventory report."""
    
    report_date: datetime = Field(default_factory=datetime.now, description="Report generation date")
    total_products: int = Field(..., ge=0, description="Total number of products")
    total_stock_value: float = Field(..., ge=0, description="Total inventory value")
    low_stock_items: list[ProductSummary] = Field(default_factory=list, description="Products below threshold")
    critical_items_count: int = Field(..., ge=0, description="Number of critical items")
    top_suppliers: list[str] = Field(default_factory=list, description="Most used suppliers")
    recommendations: list[str] = Field(default_factory=list, description="Actionable recommendations")
    
    def get_summary_text(self) -> str:
        """Generate human-readable summary."""
        return f"""
📊 Inventory Report - {self.report_date.strftime('%Y-%m-%d %H:%M')}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Products: {self.total_products}
Total Stock Value: ${self.total_stock_value:,.2f}
Low Stock Items: {len(self.low_stock_items)}
Critical Items: {self.critical_items_count}

Top Suppliers: {', '.join(self.top_suppliers[:3]) if self.top_suppliers else 'N/A'}

⚠️ Recommendations:
{chr(10).join(f'  • {r}' for r in self.recommendations) if self.recommendations else '  • None'}
"""


class QueryResponse(BaseModel):
    """Response with natural language + structured data."""
    
    summary: str = Field(..., description="Human-readable summary")
    data: dict = Field(..., description="Structured data for programmatic use")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score")
    source: Optional[str] = Field(default=None, description="Data source or tool used")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "summary": "There are 23 items with low stock.",
                "data": {"low_stock_count": 23, "products": []},
                "confidence": 0.95,
                "source": "inventory_database"
            }
        }
    }
