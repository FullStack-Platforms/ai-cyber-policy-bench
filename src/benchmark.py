import openai
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta
import configparser

# Load configuration
config = configparser.ConfigParser()
config.read("config.cfg")


# Configure client based on config
def get_client():
    """Get OpenAI client configured from config.cfg"""
    openrouter_key = config.get("OpenRouter", "api_key", fallback=None)
    openai_key = config.get("OpenAI", "api_key", fallback=None)
    openai_url = config.get("OpenAI", "openai_compatible_url", fallback=None)

    if openrouter_key and openrouter_key.strip():
        return openai.OpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=openrouter_key
        )
    elif openai_key and openai_key.strip():
        base_url = openai_url if openai_url and openai_url.strip() else None
        return openai.OpenAI(api_key=openai_key, base_url=base_url)
    else:
        # Return client with placeholder - will fail at runtime if no key
        return openai.OpenAI(
            base_url="https://openrouter.ai/api/v1", api_key="your-openrouter-key"
        )


client = get_client()

# Configuration options
USE_DYNAMIC_MODELS = False  # Set to False to use FIXED_EVAL_MODELS
CACHE_DURATION_HOURS = 24  # Cache model list for 24 hours


# Function to get default model list from config
def get_default_eval_models():
    """Get default evaluation models from config."""
    models_str = config.get("Models", "default_eval_models", fallback="")
    if models_str:
        return [model.strip() for model in models_str.split(",") if model.strip()]
    else:
        # Fallback if config is missing
        return [
            "mistralai/mistral-nemo",
            "qwen/qwen3-30b-a3b",
            "deepseek/deepseek-v3",
            "qwen/qwen3-coder",
            "z-ai/glm-4.5",
            "gpt-5-mini",
            "moonshotai/kimi-k2",
            "google/gemini-2.5-flash",
            "google/gemini-2.5-pro",
            "gpt-5-chat",
            "gpt-4.1",
            "anthropic/claude-sonnet-4",
            "x-ai/grok-4",
            "anthropic/claude-3.7-sonnet",
            "anthropic/claude-opus-4.1",
        ]


# Global cache for models
_model_cache = {"models": [], "timestamp": None}


def calculate_model_score(model: Dict) -> float:
    """
    Calculate an objective score for a model based on its capabilities.

    Args:
        model: Model data dictionary from OpenRouter API

    Returns:
        Numerical score representing model capabilities
    """
    # Extract model metadata
    context_length = model.get("context_length", 0)

    # Calculate score based on objective factors
    score = 0

    # Prioritize models with larger context windows
    score += min(context_length / 5000, 20)  # Scale context length, cap at 20 points

    # Consider other objective factors if available
    if model.get("training_data_cutoff"):
        # Newer models get higher scores
        try:
            cutoff_date = datetime.fromisoformat(
                model["training_data_cutoff"].replace("Z", "+00:00")
            )
            days_old = (datetime.now() - cutoff_date).days
            recency_score = max(0, 10 - (days_old / 100))  # Newer models score higher
            score += recency_score
        except (ValueError, TypeError):
            pass

    return score


def fetch_top_models_from_openrouter(
    limit: int = 20, api_key: Optional[str] = None
) -> List[str]:
    """
    Fetch top models from OpenRouter API sorted by objective metrics.

    Args:
        limit: Number of top models to return (default 20)
        api_key: OpenRouter API key (uses environment or falls back to client key)

    Returns:
        List of model IDs sorted by performance metrics
    """
    try:
        # Prepare authentication headers
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        elif hasattr(client, "api_key") and client.api_key != "your-openrouter-key":
            headers["Authorization"] = f"Bearer {client.api_key}"

        # Fetch models from API
        response = requests.get(
            "https://openrouter.ai/api/v1/models", headers=headers, timeout=30
        )
        response.raise_for_status()

        # Parse response
        models_data = response.json()
        models = models_data.get("data", [])

        # Filter out models that are not available for inference
        available_models = [
            model
            for model in models
            if model.get("context_length", 0) > 0
            and not model.get("pricing", {}).get("prompt", "0").startswith("0")
        ]

        # Sort by score (descending) and take top models
        available_models.sort(key=calculate_model_score, reverse=True)
        top_models = [model["id"] for model in available_models[:limit]]

        return top_models

    except Exception as e:
        print(f"Error fetching models from OpenRouter: {e}")
        print("Falling back to default model list")
        return get_default_eval_models()[:limit]


def get_eval_models(use_cache: bool = True, limit: int = 20) -> List[str]:
    """
    Get the list of models to evaluate, either from OpenRouter API or default list.

    Args:
        use_cache: Whether to use cached results if available
        limit: Maximum number of models to return

    Returns:
        List of model IDs to evaluate
    """
    global _model_cache

    # Use default models if dynamic fetching is disabled
    if not USE_DYNAMIC_MODELS:
        return get_default_eval_models()[:limit]

    # Check cache validity
    if use_cache and _model_cache["timestamp"]:
        cache_age = datetime.now() - _model_cache["timestamp"]
        if cache_age < timedelta(hours=CACHE_DURATION_HOURS) and _model_cache["models"]:
            return _model_cache["models"][:limit]

    # Fetch fresh data
    models = fetch_top_models_from_openrouter(limit=limit)

    # Update cache
    _model_cache["models"] = models
    _model_cache["timestamp"] = datetime.now()

    return models


# Initialize models list
EVAL_MODELS = get_eval_models()
