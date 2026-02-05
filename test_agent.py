"""Quick test script for the LangChain grocery agent."""

from agent_core import create_grocery_agent, get_agent_config
from rich.console import Console

console = Console()


def test_agent():
    """Test basic agent functionality."""
    
    console.print("\n[bold cyan]Testing LangChain Grocery Agent[/bold cyan]\n")
    
    # Initialize agent
    console.print("[yellow]1. Initializing agent...[/yellow]")
    try:
        agent = create_grocery_agent(verbose=True)
        console.print("[green]✅ Agent initialized successfully![/green]\n")
    except Exception as e:
        console.print(f"[red]❌ Failed: {str(e)}[/red]")
        return
    
    # Test cases
    test_queries = [
        "How many products do we have in inventory?",
        "Show me products with low stock",
        "What's the stock level of milk?",
    ]
    
    config = get_agent_config("test_session")
    
    for i, query in enumerate(test_queries, 1):
        console.print(f"\n[bold]Test {i}:[/bold] {query}")
        console.print("[dim]" + "─" * 60 + "[/dim]")
        
        try:
            messages_input = {
                "messages": [{"role": "user", "content": query}],
                "session_id": "test_session",
                "user_preferences": {},
                "pending_orders": [],
                "context": {}
            }
            
            response = agent.invoke(messages_input, config)
            
            if "messages" in response and response["messages"]:
                latest = response["messages"][-1]
                if hasattr(latest, 'content'):
                    console.print(f"[green]Response:[/green] {latest.content[:200]}...")
            
            console.print("[green]✅ Test passed[/green]")
        
        except Exception as e:
            console.print(f"[red]❌ Test failed: {str(e)}[/red]")
    
    console.print("\n[bold green]Testing complete![/bold green]")


if __name__ == "__main__":
    test_agent()
