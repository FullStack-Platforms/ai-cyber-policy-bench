import openai
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta
import configparser

# Use centralized config loading
from .utils import get_config

config = get_config()


def get_client():
    """Get OpenAI client configured from config.cfg"""
    from .utils import get_openai_client, APIError
    
    try:
        return get_openai_client()
    except APIError as e:
        raise RuntimeError(f"Failed to initialize API client: {e}")


client = get_client()

# Configuration is now handled via config file - no hardcoded options


def list_default_eval_models():
    """Get default evaluation models from config."""
    from .utils import get_config_value, ConfigError
    
    models_str = get_config_value("Models", "eval_models", "")
    if not models_str:
        raise ConfigError(
            "No evaluation models configured. Please set 'eval_models' in [Models] section of config.cfg"
        )
    
    models = [model.strip() for model in models_str.split(",") if model.strip()]
    if not models:
        raise ConfigError(
            "Invalid evaluation models configuration. Please provide comma-separated model names."
        )
    
    return models


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
    
    Raises:
        ConfigError: If API access fails and no valid configuration is available
    """
    from .utils import get_config_value, ConfigError
    
    try:
        # Get API key from config if not provided
        if not api_key:
            api_key = get_config_value("OpenRouter", "api_key", "")
        
        if not api_key or api_key == "your-openrouter-key":
            raise ConfigError("No valid OpenRouter API key found in configuration")
        
        # Prepare authentication headers
        headers = {"Authorization": f"Bearer {api_key}"}

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
        raise ConfigError(
            f"Failed to fetch models from OpenRouter API: {e}. "
            "Please check your API key or use static model configuration."
        )


def list_eval_models(use_cache: bool = True, limit: int = 20) -> List[str]:
    """
    Get the list of models to evaluate, either from OpenRouter API or config.

    Args:
        use_cache: Whether to use cached results if available
        limit: Maximum number of models to return

    Returns:
        List of model IDs to evaluate
    
    Raises:
        ConfigError: If no valid models can be obtained
    """
    from .utils import get_config_value, ConfigError
    
    global _model_cache
    
    use_dynamic = get_config_value("Models", "use_dynamic_models", False, bool)
    cache_hours = get_config_value("Models", "model_cache_hours", 24, int)

    # Use static models if dynamic fetching is disabled
    if not use_dynamic:
        return list_default_eval_models()[:limit]

    # Check cache validity
    if use_cache and _model_cache["timestamp"]:
        cache_age = datetime.now() - _model_cache["timestamp"]
        if cache_age < timedelta(hours=cache_hours) and _model_cache["models"]:
            return _model_cache["models"][:limit]

    try:
        # Fetch fresh data from API
        models = fetch_top_models_from_openrouter(limit=limit)
        
        # Update cache
        _model_cache["models"] = models
        _model_cache["timestamp"] = datetime.now()
        
        return models
        
    except ConfigError:
        # If API fails, fall back to configured models
        return list_default_eval_models()[:limit]


# Initialize models list
EVAL_MODELS = get_eval_models()
