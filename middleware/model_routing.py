"""Dynamic model selection middleware."""

from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse
from typing import Callable


def create_complexity_routing(base_model, advanced_model):
    """Create a model routing middleware with the specified models.
    
    Args:
        base_model: Fast model for simple queries (e.g., gemma3:1b)
        advanced_model: Powerful model for complex tasks (e.g., glm-4.6:cloud)
        
    Returns:
        Middleware function for dynamic model selection
    """
    
    @wrap_model_call
    def complexity_based_routing(
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse]
    ) -> ModelResponse:
        """Route to appropriate model based on query complexity.
        
        Uses advanced model for:
        - Analysis and reporting queries
        - Multi-step reasoning tasks
        - Long conversations
        - Queries with multiple conditions
        
        Uses base model for:
        - Simple lookups
        - Basic queries
        - Direct tool calls
        """
        
        messages = request.state.get("messages", [])
        message_count = len(messages)
        
        # Get the last user message
        last_message = ""
        for msg in reversed(messages):
            if hasattr(msg, 'content') and isinstance(msg.content, str):
                # Check if it's a user message (not system or AI)
                msg_type = msg.__class__.__name__
                if msg_type in ['HumanMessage', 'UserMessage']:
                    last_message = msg.content.lower()
                    break
        
        # Define complexity keywords
        complex_keywords = [
            'analyze', 'analysis', 'report', 'summary', 'trend', 'forecast',
            'compare', 'comparison', 'evaluate', 'assessment', 'recommendation',
            'calculate', 'estimate', 'predict', 'strategy', 'optimize',
            'comprehensive', 'detailed', 'explain why', 'what if', 'scenarios'
        ]
        
        multi_step_indicators = [
            'and then', 'after that', 'also', 'additionally', 'furthermore',
            'both', 'all', 'multiple', 'several', 'various'
        ]
        
        # Check for complexity indicators
        has_complex_keywords = any(keyword in last_message for keyword in complex_keywords)
        has_multi_step = any(indicator in last_message for indicator in multi_step_indicators)
        is_long_conversation = message_count > 10
        is_long_query = len(last_message) > 200
        
        # Decision logic
        use_advanced = (
            has_complex_keywords or
            has_multi_step or
            is_long_conversation or
            is_long_query
        )
        
        selected_model = advanced_model if use_advanced else base_model
        
        # Optional: Log the decision for debugging
        model_name = getattr(selected_model, 'model', 'unknown')
        # print(f"[Model Router] Selected: {model_name} (complex={use_advanced})")
        
        return handler(request.override(model=selected_model))
    
    return complexity_based_routing
