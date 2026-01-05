"""OpenAI API client for making LLM requests."""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from .config import OPENAI_API_KEY, REASONING_EFFORT


# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
    reasoning_effort: str = REASONING_EFFORT
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenAI API using the new responses API for GPT-5 models.

    Args:
        model: OpenAI model identifier (e.g., "gpt-5-mini")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds
        reasoning_effort: Reasoning effort for gpt-5 models (low, medium, high)

    Returns:
        Response dict with 'content' and 'reasoning', or None if failed
    """
    try:
        # Use the new responses API for GPT-5 models with reasoning summary
        response = await client.responses.create(
            model=model,
            reasoning={
                "effort": reasoning_effort,
                "summary": "auto"  # Request reasoning summary
            },
            input=messages,
            timeout=timeout
        )

        # Extract content from output_text
        content = response.output_text

        # Extract reasoning summary from output array
        reasoning_summary = None
        if hasattr(response, 'output') and response.output:
            for item in response.output:
                if item.get('type') == 'reasoning' and item.get('summary'):
                    # Combine summary text items
                    summary_parts = []
                    for summary_item in item['summary']:
                        if summary_item.get('type') == 'summary_text':
                            summary_parts.append(summary_item.get('text', ''))
                    reasoning_summary = '\n'.join(summary_parts)
                    break

        return {
            'content': content,
            'reasoning': reasoning_summary
        }

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
    reasoning_effort: str = REASONING_EFFORT
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenAI model identifiers
        messages: List of message dicts to send to each model
        reasoning_effort: Reasoning effort for gpt-5 models

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages, reasoning_effort=reasoning_effort) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
