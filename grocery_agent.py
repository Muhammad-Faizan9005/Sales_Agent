import os
import json
import uuid
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

from langchain_ollama import OllamaLLM
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# ---------------- LOAD ENV ----------------
load_dotenv()

INVENTORY_CSV = os.getenv("INVENTORY_CSV", "grocery_inventory.csv")
SUPPLIERS_CSV = os.getenv("SUPPLIERS_CSV", "suppliers.csv")
ORDER_CSV = os.getenv("ORDER_CSV", "stock_order.csv")
CRITICAL_LOW_STOCK_CSV = os.getenv("CRITICAL_LOW_STOCK_CSV", "critical_low_stock.csv")
MEMORY_FILE = os.getenv("MEMORY_FILE", "agent_memory.json")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", 0))

# ---------------- UTILITIES ----------------

def load_inventory():
    return pd.read_csv(INVENTORY_CSV)

def save_inventory(inventory_df):
    """Save updated inventory back to CSV"""
    inventory_df.to_csv(INVENTORY_CSV, index=False)

def update_inventory_quantity(product_id, quantity_ordered):
    """Update inventory quantity after an order is placed"""
    inventory = load_inventory()
    # Find the product and update quantity
    mask = inventory['Product_ID'] == product_id
    if mask.any():
        current_qty = inventory.loc[mask, 'Quantity_In_Stock'].values[0]
        new_qty = current_qty + quantity_ordered  # Add to stock (order incoming)
        inventory.loc[mask, 'Quantity_In_Stock'] = new_qty
        save_inventory(inventory)
        return True
    return False

def load_suppliers():
    return pd.read_csv(SUPPLIERS_CSV)

def get_supplier_info(supplier_name, suppliers_df):
    """Get supplier details from suppliers dataframe"""
    supplier = suppliers_df[suppliers_df['Supplier_Name'] == supplier_name]
    if not supplier.empty:
        return supplier.iloc[0].to_dict()
    return None

def get_recent_orders(limit=5):
    """Get most recent orders"""
    try:
        orders_df = load_orders()
        if orders_df.empty:
            return []
        # Sort by date and get most recent
        orders_df['Order_Date'] = pd.to_datetime(orders_df['Order_Date'])
        recent = orders_df.sort_values('Order_Date', ascending=False).head(limit)
        return recent.to_dict('records')
    except:
        return []

def load_orders():
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

def save_order(row):
    df = load_orders()
    new_row = pd.DataFrame([row])
    if df.empty:
        df = new_row
    else:
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_csv(ORDER_CSV, index=False)

# ---------------- MEMORY ----------------

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                content = f.read().strip()
                if content:
                    return json.loads(content)
        except (json.JSONDecodeError, ValueError):
            pass
    return {"chat_history": [], "orders": {}}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_chat_to_memory(chat_history, persistent_state):
    """Save chat history to persistent state"""
    messages = []
    for msg in chat_history.messages:
        messages.append({
            "type": msg.__class__.__name__,
            "content": msg.content
        })
    persistent_state["chat_history"] = messages
    save_memory(persistent_state)

def load_chat_from_memory(chat_history, persistent_state):
    """Load chat history from persistent state"""
    if "chat_history" in persistent_state:
        for msg_dict in persistent_state["chat_history"]:
            if msg_dict["type"] == "HumanMessage":
                chat_history.add_user_message(msg_dict["content"])
            elif msg_dict["type"] == "AIMessage":
                chat_history.add_ai_message(msg_dict["content"])

# ---------------- CORE LOGIC ----------------

def detect_low_stock(df, threshold=10):
    return df[df["Quantity_In_Stock"] <= threshold]

def update_critical_low_stock(inventory):
    """Track items with quantity < 50 in separate CSV"""
    critical_items = inventory[inventory["Quantity_In_Stock"] < 50].copy()
    critical_items.to_csv(CRITICAL_LOW_STOCK_CSV, index=False)
    return critical_items

def find_product_by_name(user_query, inventory):
    """Find a product from inventory using smart matching - works for entire inventory"""
    import re
    
    query_lower = user_query.lower()
    
    # Remove common prefixes/suffixes that aren't part of product names
    query_clean = re.sub(r'\b(order|buy|get|need|want|check|show|quantity|of|the|a|an|items|units|pieces|more)\b', '', query_lower)
    query_clean = query_clean.strip()
    
    # Strategy 1: Exact product name match (best)
    for _, row in inventory.iterrows():
        product_name_lower = row['Product_Name'].lower()
        if product_name_lower == query_clean or product_name_lower in query_lower:
            return row
    
    # Strategy 2: All product words must be present in query
    best_match = None
    best_score = 0
    
    for _, row in inventory.iterrows():
        product_name_lower = row['Product_Name'].lower()
        product_words = [w for w in product_name_lower.replace('-', ' ').split() if len(w) > 2]
        
        # Count how many product words are in the query
        matches = 0
        for prod_word in product_words:
            if prod_word in query_clean or prod_word in query_lower:
                matches += 1
        
        # Calculate match percentage
        if len(product_words) > 0:
            match_percentage = matches / len(product_words)
            
            # Bonus for matching all words
            if match_percentage == 1.0:
                score = 100 + len(product_name_lower)  # Prefer longer matches
            elif match_percentage >= 0.8:  # At least 80% words match
                score = 80 + matches
            else:
                score = matches * 10
            
            if score > best_score:
                best_score = score
                best_match = row
    
    # Only return if we have strong confidence (at least 80% match)
    if best_score >= 80:
        return best_match
    
    return None
    return critical_items

def get_inventory_summary(inventory):
    """Get summary statistics of inventory"""
    return {
        "total_products": len(inventory),
        "total_stock": inventory["Quantity_In_Stock"].sum(),
        "lowest_stock_product": inventory.loc[inventory["Quantity_In_Stock"].idxmin()],
        "highest_stock_product": inventory.loc[inventory["Quantity_In_Stock"].idxmax()],
        "avg_stock": inventory["Quantity_In_Stock"].mean(),
        "categories": inventory["Category"].unique().tolist(),
        "suppliers": inventory["Supplier"].unique().tolist()
    }

def find_product_by_name(user_query, inventory):
    """Find a product from inventory using smart matching - works for entire inventory"""
    import re
    
    query_lower = user_query.lower()
    
    # Remove common prefixes/suffixes that aren't part of product names
    query_clean = re.sub(r'\b(order|buy|get|need|want|check|show|quantity|of|the|a|an|items|units|pieces|more)\b', '', query_lower)
    query_clean = query_clean.strip()
    
    # Strategy 1: Exact product name match (best)
    for _, row in inventory.iterrows():
        product_name_lower = row['Product_Name'].lower()
        if product_name_lower == query_clean or product_name_lower in query_lower:
            return row
    
    # Strategy 2: All product words must be present in query
    best_match = None
    best_score = 0
    
    for _, row in inventory.iterrows():
        product_name_lower = row['Product_Name'].lower()
        product_words = [w for w in product_name_lower.replace('-', ' ').split() if len(w) > 2]
        
        # Count how many product words are in the query
        matches = 0
        for prod_word in product_words:
            if prod_word in query_clean or prod_word in query_lower:
                matches += 1
        
        # Calculate match percentage
        if len(product_words) > 0:
            match_percentage = matches / len(product_words)
            
            # Bonus for matching all words
            if match_percentage == 1.0:
                score = 100 + len(product_name_lower)  # Prefer longer matches
            elif match_percentage >= 0.8:  # At least 80% words match
                score = 80 + matches
            else:
                score = matches * 10
            
            if score > best_score:
                best_score = score
                best_match = row
    
    # Only return if we have strong confidence (at least 80% match)
    if best_score >= 80:
        return best_match
    
    return None

def search_products(inventory, query):
    """Search for products matching query - returns list of matches"""
    matches = []
    query_lower = query.lower()
    
    for _, row in inventory.iterrows():
        product_name_lower = row["Product_Name"].lower()
        
        # Exact match
        if query_lower == product_name_lower or product_name_lower in query_lower:
            matches.append(row)
        # Check if all words in query are in product name
        else:
            query_words = [w for w in query_lower.split() if len(w) > 2]
            if query_words and all(word in product_name_lower for word in query_words):
                matches.append(row)
    
    return matches

def create_test_order(row, ordered_qty, supplier_info):
    total_bill = ordered_qty * row["Cost_Price"]

    order = {
        "Order_ID": str(uuid.uuid4()),
        "Product_ID": row["Product_ID"],
        "Product_Name": row["Product_Name"],
        "Supplier": row["Supplier"],
        "Supplier_Contact": supplier_info.get('Contact_Phone', 'N/A') if supplier_info else 'N/A',
        "Supplier_Email": supplier_info.get('Contact_Email', 'N/A') if supplier_info else 'N/A',
        "Current_Stock": row["Quantity_In_Stock"],
        "Ordered_Quantity": int(ordered_qty),
        "Total_Bill": float(total_bill),
        "Order_Status": "PENDING",
        "Order_Date": datetime.now().isoformat(),
        "Expected_Delivery": supplier_info.get('Delivery_Days', 'N/A') if supplier_info else 'N/A'
    }

    save_order(order)

    notification = {
        "Product": row["Product_Name"],
        "Quantity_Left": int(row["Quantity_In_Stock"]),
        "Ordered_From": row["Supplier"],
        "Supplier_Contact": order["Supplier_Contact"],
        "Quantity_Ordered": int(ordered_qty),
        "Total_Bill": round(total_bill, 2),
        "Expected_Delivery": order["Expected_Delivery"]
    }

    return order, notification

# ---------------- LLM SETUP ----------------
llm = OllamaLLM(
    model=OLLAMA_MODEL,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=OLLAMA_TEMPERATURE,
    base_url=OLLAMA_URL
)

chat_history = ChatMessageHistory()

system_base = """
You are a grocery inventory assistant. Answer questions about the inventory using the provided data.

Guidelines:
- Answer directly based on the inventory summary and data provided
- For lowest/highest stock queries, use the summary statistics
- For specific product queries, use the product list
- For reports, describe the overall inventory status
- Be concise but complete in your answers
"""

# ---------------- CHAT LOOP ----------------

def parse_order_intent(user_input, inventory):
    """Parse if user wants to order a specific product - universal solution"""
    user_lower = user_input.lower()
    
    # Check if user wants to order something
    order_keywords = ['order', 'buy', 'purchase', 'get', 'need', 'want']
    has_order_intent = any(keyword in user_lower for keyword in order_keywords)
    
    if not has_order_intent:
        return None, None
    
    # Extract quantity
    quantity = None
    import re
    numbers = re.findall(r'\d+', user_input)
    if numbers:
        quantity = int(numbers[0])
    
    # Use the universal product finder
    product = find_product_by_name(user_input, inventory)
    
    return product, quantity
    
    if not has_order_intent:
        return None, None
    
    # Extract quantity
    quantity = None
    import re
    numbers = re.findall(r'\d+', user_input)
    if numbers:
        quantity = int(numbers[0])
    
    # Use the universal product finder
    product = find_product_by_name(user_input, inventory)
    
    return product, quantity

def main():
    print("Inventory Agent started. Type 'exit' to quit.\n")

    persistent_state = load_memory()
    
    # Load chat history from memory
    load_chat_from_memory(chat_history, persistent_state)

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            save_memory(persistent_state)
            break

        inventory = load_inventory()
        suppliers = load_suppliers()
        
        # Update critical low stock CSV
        critical_items = update_critical_low_stock(inventory)
        
        # Check if user wants to order a specific product
        product_to_order, quantity = parse_order_intent(user_input, inventory)
        
        if product_to_order is not None:
            if quantity is None:
                print(f"\nHow many units of {product_to_order['Product_Name']} would you like to order?")
                qty_input = input("Enter quantity: ")
                try:
                    quantity = int(qty_input)
                except ValueError:
                    print("Invalid quantity. Order cancelled.")
                    continue
            
            if quantity is not None:
                # Get supplier information
                supplier_info = get_supplier_info(product_to_order['Supplier'], suppliers)
                order, note = create_test_order(product_to_order, quantity, supplier_info)
                
                # Update inventory quantity
                update_inventory_quantity(product_to_order['Product_ID'], quantity)
                
                print(f"\n{'='*50}")
                print(f"ORDER CONFIRMED")
                print(f"{'='*50}")
                print(f"Product:          {product_to_order['Product_Name']}")
                print(f"Quantity:         {quantity} units")
                print(f"Current Stock:    {product_to_order['Quantity_In_Stock']} units")
                print(f"New Stock:        {product_to_order['Quantity_In_Stock'] + quantity} units (after delivery)")
                print(f"Supplier:         {product_to_order['Supplier']}")
                print(f"Contact:          {note['Supplier_Contact']}")
                print(f"Total Cost:       ${note['Total_Bill']:.2f}")
                print(f"Expected:         {note['Expected_Delivery']}")
                print(f"Order ID:         {order['Order_ID'][:8]}...")
                print(f"{'='*50}\n")
                
                # Don't pass to LLM if order was placed
                continue
        
        # Analyze the user query to build relevant context
        user_lower = user_input.lower()
        
        # Get inventory summary
        summary = get_inventory_summary(inventory)
        
        # Get recent orders if user asks about orders/delivery
        recent_orders_context = ""
        if any(word in user_lower for word in ['order', 'delivery', 'arrive', 'when', 'shipped']):
            recent_orders = get_recent_orders(5)
            if recent_orders:
                recent_orders_context = "\n\nRecent Orders:\n"
                for order in recent_orders:
                    recent_orders_context += f"- {order['Product_Name']}: {order['Ordered_Quantity']} units, Status: {order['Order_Status']}, Expected: {order.get('Expected_Delivery', 'N/A')}, Order Date: {order['Order_Date']}\n"
        
        # Build focused context based on query type
        if any(word in user_lower for word in ['lowest', 'minimum', 'least']):
            # Query about lowest stock
            context = f"""Inventory Summary:
- Total Products: {summary['total_products']}
- Lowest Stock Item: {summary['lowest_stock_product']['Product_Name']} with {summary['lowest_stock_product']['Quantity_In_Stock']} units
- Supplier: {summary['lowest_stock_product']['Supplier']}
{recent_orders_context}
"""
        elif any(word in user_lower for word in ['highest', 'maximum', 'most']):
            # Query about highest stock
            context = f"""Inventory Summary:
- Total Products: {summary['total_products']}
- Highest Stock Item: {summary['highest_stock_product']['Product_Name']} with {summary['highest_stock_product']['Quantity_In_Stock']} units
- Supplier: {summary['highest_stock_product']['Supplier']}
{recent_orders_context}
"""
        elif any(word in user_lower for word in ['report', 'summary', 'overview', 'status']):
            # Full report request
            low_stock = inventory[inventory['Quantity_In_Stock'] < 50]
            context = f"""Full Inventory Report:
- Total Products: {summary['total_products']}
- Total Stock Units: {summary['total_stock']}
- Average Stock per Product: {summary['avg_stock']:.1f} units
- Lowest Stock: {summary['lowest_stock_product']['Product_Name']} ({summary['lowest_stock_product']['Quantity_In_Stock']} units)
- Highest Stock: {summary['highest_stock_product']['Product_Name']} ({summary['highest_stock_product']['Quantity_In_Stock']} units)
- Critical Low Stock Items (< 50 units): {len(low_stock)}
- Categories: {len(summary['categories'])}
- Suppliers: {len(summary['suppliers'])}
{recent_orders_context}
"""
        else:
            # Search for specific products mentioned
            user_keywords = [w for w in user_lower.split() if len(w) > 3]
            relevant_products = []
            
            for keyword in user_keywords:
                matches = search_products(inventory, keyword)
                relevant_products.extend(matches)
            
            # Remove duplicates
            relevant_products = list({p['Product_ID']: p for p in relevant_products}.values())
            
            if relevant_products:
                context = f"""Inventory Summary:
- Total Products: {summary['total_products']}

Relevant Products Found:\n"""
                for prod in relevant_products[:15]:  # Limit to 15
                    context += f"- {prod['Product_Name']}: {prod['Quantity_In_Stock']} units, {prod['Supplier']}, ${prod['Cost_Price']}\n"
                context += recent_orders_context
            else:
                context = f"""Inventory Summary:
- Total Products: {summary['total_products']}
- Average Stock: {summary['avg_stock']:.1f} units
- Lowest Stock: {summary['lowest_stock_product']['Product_Name']} ({summary['lowest_stock_product']['Quantity_In_Stock']} units)
- Highest Stock: {summary['highest_stock_product']['Product_Name']} ({summary['highest_stock_product']['Quantity_In_Stock']} units)
{recent_orders_context}
"""
        
        # Create messages with focused context
        system_message = system_base + "\n\n" + context
        
        messages = [SystemMessage(content=system_message)]
        messages.extend(chat_history.messages)
        messages.append(HumanMessage(content=user_input))

        response = llm.invoke(messages)
        # Clean up response if it's a string
        if isinstance(response, str):
            response_text = response.strip()
        else:
            response_text = str(response).strip()
        
        # Remove any "AI:" prefix that might appear
        if response_text.startswith("AI:"):
            response_text = response_text[3:].strip()
        
        print("\nAgent:", response_text)

        # Notifications already displayed inline, skip redundant display

        chat_history.add_user_message(user_input)
        chat_history.add_ai_message(response_text)
        
        # Save conversation to persistent memory
        save_chat_to_memory(chat_history, persistent_state)


if __name__ == "__main__":
    main()
