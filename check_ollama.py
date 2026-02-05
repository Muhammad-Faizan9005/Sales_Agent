"""Utility script to check Ollama server health and models."""

import requests
import sys
from rich.console import Console
from rich.table import Table

console = Console()

OLLAMA_URL = "http://localhost:11434"
REQUIRED_MODELS = ["gpt-oss:20b-cloud", "glm-4.6:cloud"]


def check_ollama_server():
    """Check if Ollama server is running."""
    try:
        response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, None
    except requests.exceptions.ConnectionError:
        return False, None
    except Exception as e:
        return False, str(e)


def main():
    """Check Ollama status and models."""
    console.print("\n[bold cyan]🔍 Checking Ollama Server Status...[/bold cyan]\n")
    
    # Check server
    is_running, data = check_ollama_server()
    
    if not is_running:
        console.print("[red]❌ Ollama server is not running![/red]")
        console.print("\n[yellow]Please start Ollama:[/yellow]")
        console.print("  • Windows: Start Ollama from Start Menu or run 'ollama serve'")
        console.print("  • macOS/Linux: Run 'ollama serve' in terminal\n")
        sys.exit(1)
    
    console.print("[green]✅ Ollama server is running![/green]\n")
    
    # Check models
    if data and 'models' in data:
        available_models = [model['name'] for model in data['models']]
        
        table = Table(title="Available Models")
        table.add_column("Model", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Required", style="yellow")
        
        for model in REQUIRED_MODELS:
            is_available = any(model in m for m in available_models)
            status = "✅ Installed" if is_available else "❌ Missing"
            required = "Yes"
            table.add_row(model, status, required)
        
        console.print(table)
        console.print()
        
        # Check if all required models are available
        missing_models = [m for m in REQUIRED_MODELS if not any(m in am for am in available_models)]
        
        if missing_models:
            console.print("[yellow]⚠️  Missing required models![/yellow]")
            console.print("\n[yellow]To install missing models:[/yellow]")
            for model in missing_models:
                console.print(f"  ollama pull {model}")
            console.print()
            sys.exit(1)
        else:
            console.print("[green]✅ All required models are installed![/green]")
            console.print("[green]✅ System is ready to run the agent![/green]\n")
    
    # Test model response
    console.print("[cyan]Testing model response...[/cyan]")
    try:
        test_response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": "gpt-oss:20b-cloud", "prompt": "Hi", "stream": False},
            timeout=30
        )
        if test_response.status_code == 200:
            console.print("[green]✅ Model responding correctly![/green]\n")
        else:
            console.print(f"[yellow]⚠️  Model responded with status {test_response.status_code}[/yellow]\n")
    except Exception as e:
        console.print(f"[yellow]⚠️  Model test failed: {str(e)}[/yellow]\n")


if __name__ == "__main__":
    main()
