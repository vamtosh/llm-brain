"""OpenAI API client for making LLM requests."""

from openai import AsyncOpenAI
from typing import List, Dict, Any, Optional
from .config import OPENAI_API_KEY


# Initialize OpenAI client
client = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def query_model(
    model: str,
    messages: List[Dict[str, str]],
    timeout: float = 120.0,
    temperature: float = 0.7
) -> Optional[Dict[str, Any]]:
    """
    Query a single model via OpenAI API.

    Args:
        model: OpenAI model identifier (e.g., "gpt-4o")
        messages: List of message dicts with 'role' and 'content'
        timeout: Request timeout in seconds
        temperature: Model temperature (0.0-1.0)

    Returns:
        Response dict with 'content', or None if failed
    """
    try:
        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            timeout=timeout
        )

        content = response.choices[0].message.content

        return {
            'content': content
        }

    except Exception as e:
        print(f"Error querying model {model}: {e}")
        return None


async def query_models_parallel(
    models: List[str],
    messages: List[Dict[str, str]],
    temperature: float = 0.7
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    Query multiple models in parallel.

    Args:
        models: List of OpenAI model identifiers
        messages: List of message dicts to send to each model
        temperature: Model temperature

    Returns:
        Dict mapping model identifier to response dict (or None if failed)
    """
    import asyncio

    # Create tasks for all models
    tasks = [query_model(model, messages, temperature=temperature) for model in models]

    # Wait for all to complete
    responses = await asyncio.gather(*tasks)

    # Map models to their responses
    return {model: response for model, response in zip(models, responses)}
