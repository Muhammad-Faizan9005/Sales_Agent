"""Tool error handling middleware."""

from langchain_core.messages import ToolMessage
from langchain.agents.middleware import wrap_tool_call


@wrap_tool_call
def handle_tool_errors(request, handler):
    """Handle tool execution errors gracefully with user-friendly messages.
    
    This middleware catches exceptions from tool execution and returns
    helpful error messages instead of raw Python exceptions.
    
    Args:
        request: Tool execution request
        handler: Next handler in the chain
        
    Returns:
        ToolMessage with result or error information
    """
    try:
        return handler(request)
    
    except FileNotFoundError as e:
        return ToolMessage(
            content=f"❌ Data file not found: {str(e)}. Please check that all inventory CSV files are present in the correct location.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call.get("name", "unknown")
        )
    
    except ValueError as e:
        return ToolMessage(
            content=f"❌ Invalid input: {str(e)}. Please check your parameters and try again.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call.get("name", "unknown")
        )
    
    except KeyError as e:
        return ToolMessage(
            content=f"❌ Missing required field: {str(e)}. The data might be incomplete or in an unexpected format.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call.get("name", "unknown")
        )
    
    except PermissionError as e:
        return ToolMessage(
            content=f"❌ Permission denied: {str(e)}. Check file permissions for inventory data files.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call.get("name", "unknown")
        )
    
    except Exception as e:
        # Catch-all for unexpected errors
        return ToolMessage(
            content=f"❌ An unexpected error occurred: {str(e)}. Please try again or contact support if the issue persists.",
            tool_call_id=request.tool_call["id"],
            name=request.tool_call.get("name", "unknown")
        )
