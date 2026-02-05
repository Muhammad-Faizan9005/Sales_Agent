"""Main entry point for the LangChain-powered Grocery Inventory Agent."""

import sys
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from agent_core import create_grocery_agent, get_agent_config
from utils.formatters import format_order_confirmation

# Initialize rich console for better output
console = Console()


def print_welcome():
    """Print welcome message."""
    welcome_text = """
🛒 **Grocery Inventory Management Agent**
Powered by LangChain & Ollama

**Available Commands:**
• Ask about inventory: "What's the stock level of milk?"
• Check low stock: "Show me low stock items"
• Place orders: "Order 100 units of product P00001"
• View orders: "Show recent orders"
• Get supplier info: "Tell me about Metro Wholesale"
• General queries: "What items need reordering?"

Type 'exit', 'quit', or 'bye' to exit.
"""
    console.print(Panel(welcome_text, border_style="green", title="Welcome"))


def print_streaming_response(agent, user_input: str, session_id: str):
    """Stream agent response with progress indication.
    
    Args:
        agent: The grocery agent instance
        user_input: User's query
        session_id: Session identifier
    """
    config = get_agent_config(session_id)
    
    messages_input = {
        "messages": [{"role": "user", "content": user_input}],
        "session_id": session_id,
        "user_preferences": {},
        "pending_orders": [],
        "context": {}
    }
    
    console.print(f"\n[bold blue]You:[/bold blue] {user_input}")
    console.print("[bold green]Agent:[/bold green] ", end="")
    
    try:
        response_started = False
        full_response = ""
        
        # Stream the response
        last_ai_message = None
        tool_calls_shown = set()
        
        for chunk in agent.stream(messages_input, config, stream_mode="values"):
            if "messages" in chunk and chunk["messages"]:
                for message in chunk["messages"]:
                    # Show tool calls
                    if hasattr(message, '__class__') and \
                       message.__class__.__name__ in ['AIMessage', 'AIMessageChunk']:
                        
                        if hasattr(message, 'tool_calls') and message.tool_calls:
                            for tool_call in message.tool_calls:
                                tool_id = tool_call.get('id', '')
                                if tool_id not in tool_calls_shown:
                                    tool_name = tool_call.get('name', 'unknown')
                                    console.print(f"\n[dim]🔧 Using tool: {tool_name}[/dim]")
                                    tool_calls_shown.add(tool_id)
                        
                        # Keep track of last AI message
                        if hasattr(message, 'content') and message.content:
                            last_ai_message = message.content
        
        # Print the final complete response
        if last_ai_message:
            console.print(last_ai_message)
        
        console.print()  # New line after response
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]⚠️  Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n\n[red]❌ Error: {str(e)}[/red]")


def main():
    """Main application loop."""
    
    # Print welcome message
    print_welcome()
    
    # Initialize agent
    console.print("\n[yellow]Initializing agent...[/yellow]")
    
    try:
        agent = create_grocery_agent(
            use_dynamic_routing=True,
            enable_memory=True,
            verbose=False
        )
        console.print("[green]✅ Agent initialized successfully![/green]\n")
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize agent: {str(e)}[/red]")
        console.print("[yellow]Please ensure Ollama is running and models are available.[/yellow]")
        return
    
    # Generate session ID
    session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            console.print("\n" + "─" * 60)
            user_input = console.input("[bold cyan]You:[/bold cyan] ").strip()
            
            # Check for exit commands
            if user_input.lower() in ['exit', 'quit', 'bye', 'q']:
                console.print("\n[green]👋 Goodbye! Have a great day![/green]")
                break
            
            # Skip empty input
            if not user_input:
                continue
            
            # Process query with streaming
            print_streaming_response(agent, user_input, session_id)
        
        except KeyboardInterrupt:
            console.print("\n\n[yellow]⚠️  Interrupted. Type 'exit' to quit.[/yellow]")
            continue
        except EOFError:
            console.print("\n[green]👋 Goodbye![/green]")
            break
        except Exception as e:
            console.print(f"\n[red]❌ Unexpected error: {str(e)}[/red]")
            console.print("[yellow]Please try again or type 'exit' to quit.[/yellow]")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {str(e)}[/red]")
        sys.exit(1)
