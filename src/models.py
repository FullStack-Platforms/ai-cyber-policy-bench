"""
Model management for Cyber-Policy-Bench.

This module handles model discovery, validation, capability detection,
and provides centralized model management functionality.
"""

import asyncio
import requests
from typing import List, Dict, Optional, Set, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .utils import (
    retry_with_backoff,
    save_json,
    load_json,
)
from .base import BaseComponent, ComponentStatus


class ModelProvider(Enum):
    """Supported model providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OPENROUTER = "openrouter"
    MISTRAL = "mistralai"
    GOOGLE = "google"
    DEEPSEEK = "deepseek"
    META = "meta-llama"
    UNKNOWN = "unknown"


class ModelCapability(Enum):
    """Model capabilities."""

    TEXT_GENERATION = "text_generation"
    FUNCTION_CALLING = "function_calling"
    JSON_MODE = "json_mode"
    LARGE_CONTEXT = "large_context"  # >32k tokens
    VERY_LARGE_CONTEXT = "very_large_context"  # >128k tokens
    MULTILINGUAL = "multilingual"
    CODE_GENERATION = "code_generation"


@dataclass
class ModelInfo:
    """Information about a model."""

    id: str
    name: str
    provider: ModelProvider
    context_length: int = 0
    capabilities: Set[ModelCapability] = field(default_factory=set)
    pricing: Dict[str, float] = field(default_factory=dict)
    training_data_cutoff: Optional[str] = None
    description: Optional[str] = None
    performance_score: float = 0.0
    is_available: bool = True
    last_updated: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Post-init processing."""
        self.last_updated = self.last_updated or datetime.now().isoformat()

        # Infer capabilities from context length
        if self.context_length > 128000:
            self.capabilities.add(ModelCapability.VERY_LARGE_CONTEXT)
        elif self.context_length > 32000:
            self.capabilities.add(ModelCapability.LARGE_CONTEXT)

        # Infer provider from model ID
        if self.provider == ModelProvider.UNKNOWN:
            self.provider = self._infer_provider()

    def _infer_provider(self) -> ModelProvider:
        """Infer provider from model ID."""
        id_lower = self.id.lower()

        if "openai/" in id_lower or "gpt" in id_lower:
            return ModelProvider.OPENAI
        elif "anthropic/" in id_lower or "claude" in id_lower:
            return ModelProvider.ANTHROPIC
        elif "mistralai/" in id_lower or "mistral" in id_lower:
            return ModelProvider.MISTRAL
        elif "google/" in id_lower or "gemini" in id_lower:
            return ModelProvider.GOOGLE
        elif "deepseek/" in id_lower or "deepseek" in id_lower:
            return ModelProvider.DEEPSEEK
        elif "meta-llama/" in id_lower or "llama" in id_lower:
            return ModelProvider.META
        else:
            return ModelProvider.UNKNOWN

    def has_capability(self, capability: ModelCapability) -> bool:
        """Check if model has specific capability."""
        return capability in self.capabilities

    def is_suitable_for_judging(self) -> bool:
        """Check if model is suitable for use as a judge."""
        # Criteria for good judge models
        return (
            self.context_length >= 8000  # Sufficient context
            and self.performance_score > 0.5  # Good performance
            and self.is_available  # Available for use
            and ModelCapability.TEXT_GENERATION in self.capabilities
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "provider": self.provider.value,
            "context_length": self.context_length,
            "capabilities": [cap.value for cap in self.capabilities],
            "pricing": self.pricing,
            "training_data_cutoff": self.training_data_cutoff,
            "description": self.description,
            "performance_score": self.performance_score,
            "is_available": self.is_available,
            "last_updated": self.last_updated,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ModelInfo":
        """Create from dictionary."""
        capabilities = {ModelCapability(cap) for cap in data.get("capabilities", [])}
        provider = ModelProvider(data.get("provider", "unknown"))

        return cls(
            id=data["id"],
            name=data.get("name", data["id"]),
            provider=provider,
            context_length=data.get("context_length", 0),
            capabilities=capabilities,
            pricing=data.get("pricing", {}),
            training_data_cutoff=data.get("training_data_cutoff"),
            description=data.get("description"),
            performance_score=data.get("performance_score", 0.0),
            is_available=data.get("is_available", True),
            last_updated=data.get("last_updated"),
            metadata=data.get("metadata", {}),
        )


class ModelManager(BaseComponent):
    """Manager for model discovery and management."""

    def __init__(self, cache_duration_hours: int = None):
        """Initialize model manager."""
        super().__init__("model_manager")

        from .utils import get_config_value

        # Load configuration values
        self.cache_duration_hours = cache_duration_hours or get_config_value(
            "Models", "model_cache_hours", 24, int
        )
        self.models: Dict[str, ModelInfo] = {}

        cache_dir = get_config_value("Paths", "cache_dir", "./experiment_cache")
        self.model_cache_file = Path(cache_dir) / "model_cache.json"

        self.use_dynamic_models = get_config_value(
            "Models", "use_dynamic_models", False, bool
        )

        # Default model lists from config
        self.default_eval_models = self._get_default_eval_models()
        self.default_judge_models = self._get_default_judge_models()

        # Initialize
        self._load_cached_models()

    def _get_default_eval_models(self) -> List[str]:
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

    def _get_default_judge_models(self) -> List[str]:
        """Get default judge models from config."""
        from .utils import get_config_value, ConfigError

        models_str = get_config_value("Models", "judge_models", "")
        if not models_str:
            raise ConfigError(
                "No judge models configured. Please set 'judge_models' in [Models] section of config.cfg"
            )

        models = [model.strip() for model in models_str.split(",") if model.strip()]
        if not models:
            raise ConfigError(
                "Invalid judge models configuration. Please provide comma-separated model names."
            )

        return models

    def _load_cached_models(self) -> None:
        """Load models from cache if available and valid."""
        try:
            if self.model_cache_file.exists():
                cache_data = load_json(self.model_cache_file)
                cache_timestamp = datetime.fromisoformat(
                    cache_data.get("timestamp", "")
                )

                # Check if cache is still valid
                cache_age = datetime.now() - cache_timestamp
                if cache_age < timedelta(hours=self.cache_duration_hours):
                    self.models = {
                        model_id: ModelInfo.from_dict(model_data)
                        for model_id, model_data in cache_data.get("models", {}).items()
                    }
                    self.logger.info(f"Loaded {len(self.models)} models from cache")
                    self.set_status(ComponentStatus.READY)
                    return

        except Exception as e:
            self.logger.warning(f"Failed to load model cache: {e}")

        # Cache invalid or missing, need to refresh
        self.set_status(ComponentStatus.UNINITIALIZED)

    def _save_model_cache(self) -> None:
        """Save models to cache."""
        try:
            self.model_cache_file.parent.mkdir(parents=True, exist_ok=True)

            cache_data = {
                "timestamp": datetime.now().isoformat(),
                "models": {
                    model_id: model_info.to_dict()
                    for model_id, model_info in self.models.items()
                },
            }

            save_json(cache_data, self.model_cache_file)
            self.logger.info(f"Saved {len(self.models)} models to cache")

        except Exception as e:
            self.logger.error(f"Failed to save model cache: {e}")

    def calculate_model_score(self, model_data: Dict[str, Any]) -> float:
        """Calculate objective performance score for a model."""
        score = 0.0

        # Context length score (0-20 points)
        context_length = model_data.get("context_length", 0)
        score += min(context_length / 5000, 20)

        # Recency score (0-10 points)
        if model_data.get("training_data_cutoff"):
            try:
                cutoff_date = datetime.fromisoformat(
                    model_data["training_data_cutoff"].replace("Z", "+00:00")
                )
                days_old = (datetime.now() - cutoff_date.replace(tzinfo=None)).days
                recency_score = max(0, 10 - (days_old / 100))
                score += recency_score
            except (ValueError, TypeError):
                pass

        # Pricing score (prefer models with reasonable pricing)
        pricing = model_data.get("pricing", {})
        prompt_price = pricing.get("prompt", 0)
        if prompt_price and prompt_price != "0":
            try:
                price_float = float(prompt_price)
                # Prefer models with price between $0.001 and $0.01 per 1k tokens
                if 0.001 <= price_float <= 0.01:
                    score += 5
                elif price_float < 0.001:
                    score += 3  # Very cheap might be lower quality
                elif price_float <= 0.05:
                    score += 2  # Expensive but acceptable
            except (ValueError, TypeError):
                pass

        # Model type preferences (heuristic-based)
        model_id = model_data.get("id", "").lower()
        if any(term in model_id for term in ["gpt-4", "claude-3", "claude-4", "opus"]):
            score += 10  # Premium models
        elif any(term in model_id for term in ["turbo", "pro", "large"]):
            score += 5  # High-end models

        return score

    async def fetch_openrouter_models(
        self, api_key: Optional[str] = None
    ) -> List[ModelInfo]:
        """Fetch available models from OpenRouter API."""
        from .utils import get_config_value, ConfigError

        if not api_key:
            api_key = get_config_value("OpenRouter", "api_key", "")

        if not api_key or api_key == "your-openrouter-key":
            raise ConfigError("No valid OpenRouter API key found in configuration")

        try:
            headers = {"Authorization": f"Bearer {api_key}"}

            response = await retry_with_backoff(
                requests.get,
                "https://openrouter.ai/api/v1/models",
                headers=headers,
                timeout=30,
            )
            response.raise_for_status()

            models_data = response.json()
            models = models_data.get("data", [])

            model_infos = []
            for model in models:
                # Filter out unavailable models
                if model.get("context_length", 0) <= 0:
                    continue

                # Calculate performance score
                performance_score = self.calculate_model_score(model)

                # Extract pricing information
                pricing = {}
                if "pricing" in model:
                    pricing = {
                        "prompt": model["pricing"].get("prompt", "0"),
                        "completion": model["pricing"].get("completion", "0"),
                    }

                # Determine capabilities
                capabilities = {ModelCapability.TEXT_GENERATION}
                context_length = model.get("context_length", 0)

                if context_length > 128000:
                    capabilities.add(ModelCapability.VERY_LARGE_CONTEXT)
                elif context_length > 32000:
                    capabilities.add(ModelCapability.LARGE_CONTEXT)

                model_info = ModelInfo(
                    id=model["id"],
                    name=model.get("name", model["id"]),
                    provider=ModelProvider.OPENROUTER,
                    context_length=context_length,
                    capabilities=capabilities,
                    pricing=pricing,
                    training_data_cutoff=model.get("training_data_cutoff"),
                    description=model.get("description"),
                    performance_score=performance_score,
                    metadata={
                        "top_provider": model.get("top_provider"),
                        "per_request_limits": model.get("per_request_limits"),
                    },
                )

                model_infos.append(model_info)

            self.logger.info(f"Fetched {len(model_infos)} models from OpenRouter")
            return model_infos

        except Exception as e:
            self.logger.error(f"Failed to fetch OpenRouter models: {e}")
            return []

    def create_default_models(self) -> List[ModelInfo]:
        """Create model info from configured model lists."""
        configured_models = []

        for model_id in self.default_eval_models:
            # Infer basic information from model ID
            provider = ModelProvider.UNKNOWN

            # Get default context length from config or use conservative default
            from .utils import get_config_value

            default_context = get_config_value(
                "Models", "default_context_length", 8192, int
            )
            context_length = default_context
            capabilities = {ModelCapability.TEXT_GENERATION}

            # Infer capabilities from model name
            model_lower = model_id.lower()
            if any(term in model_lower for term in ["gpt-4", "gpt-5"]):
                context_length = 128000
                capabilities.add(ModelCapability.LARGE_CONTEXT)
                provider = ModelProvider.OPENAI
            elif "claude" in model_lower:
                context_length = 200000
                capabilities.add(ModelCapability.VERY_LARGE_CONTEXT)
                provider = ModelProvider.ANTHROPIC
            elif "gemini" in model_lower:
                context_length = 32000
                capabilities.add(ModelCapability.LARGE_CONTEXT)
                provider = ModelProvider.GOOGLE
            elif any(term in model_lower for term in ["deepseek", "qwen", "mistral"]):
                context_length = 32000
                capabilities.add(ModelCapability.LARGE_CONTEXT)

            # Get default performance score from config
            default_score = get_config_value(
                "Models", "default_performance_score", 0.5, float
            )

            model_info = ModelInfo(
                id=model_id,
                name=model_id.split("/")[-1] if "/" in model_id else model_id,
                provider=provider,
                context_length=context_length,
                capabilities=capabilities,
                performance_score=default_score,
                metadata={"source": "configured"},
            )

            configured_models.append(model_info)

        return configured_models

    async def refresh_models(self, force: bool = False) -> None:
        """Refresh model information from APIs."""
        if not force and self.status == ComponentStatus.READY:
            self.logger.info("Models already loaded and cache is valid")
            return

        self.set_status(ComponentStatus.INITIALIZING)

        try:
            new_models = {}

            if self.use_dynamic_models:
                # Fetch from OpenRouter API
                openrouter_models = await self.fetch_openrouter_models()
                for model in openrouter_models:
                    new_models[model.id] = model

            # If no dynamic models obtained, create from config
            if not new_models:
                self.logger.info("Using configured model list")
                configured_models = self.create_default_models()
                for model in configured_models:
                    new_models[model.id] = model

            self.models = new_models
            self._save_model_cache()

            self.set_status(ComponentStatus.READY)
            self.logger.info(f"Refreshed {len(self.models)} models")

        except Exception as e:
            self.set_status(ComponentStatus.ERROR)
            self.logger.error(f"Failed to refresh models: {e}")
            raise

    def get_models(
        self,
        limit: Optional[int] = None,
        capabilities: Optional[List[ModelCapability]] = None,
        min_performance_score: float = 0.0,
    ) -> List[ModelInfo]:
        """Get models matching criteria."""
        if self.status != ComponentStatus.READY:
            asyncio.run(self.refresh_models())

        # Filter models
        filtered_models = []
        for model in self.models.values():
            # Check capabilities
            if capabilities:
                if not all(model.has_capability(cap) for cap in capabilities):
                    continue

            # Check performance score
            if model.performance_score < min_performance_score:
                continue

            # Check availability
            if not model.is_available:
                continue

            filtered_models.append(model)

        # Sort by performance score
        filtered_models.sort(key=lambda m: m.performance_score, reverse=True)

        # Apply limit
        if limit:
            filtered_models = filtered_models[:limit]

        return filtered_models

    def get_model_ids(self, limit: Optional[int] = None, **kwargs) -> List[str]:
        """Get list of model IDs matching criteria."""
        models = self.get_models(limit=limit, **kwargs)
        return [model.id for model in models]

    def get_judge_models(self, limit: int = 2) -> List[ModelInfo]:
        """Get models suitable for use as judges."""
        judge_models = []

        # Filter to suitable judge models
        for model in self.models.values():
            if model.is_suitable_for_judging():
                judge_models.append(model)

        # Sort by performance score
        judge_models.sort(key=lambda m: m.performance_score, reverse=True)

        # Ensure we have models from configuration
        if not judge_models:
            from .utils import ConfigError

            raise ConfigError(
                "No suitable judge models found. Please check your configuration and model availability."
            )

        return judge_models[:limit]

    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about managed models."""
        if not self.models:
            return {"total_models": 0}

        stats = {
            "total_models": len(self.models),
            "by_provider": {},
            "by_capability": {},
            "context_length_distribution": {
                "small": 0,  # < 8k
                "medium": 0,  # 8k - 32k
                "large": 0,  # 32k - 128k
                "very_large": 0,  # > 128k
            },
            "performance_score_distribution": {
                "low": 0,  # < 0.3
                "medium": 0,  # 0.3 - 0.7
                "high": 0,  # > 0.7
            },
            "available_models": 0,
            "suitable_judges": 0,
        }

        for model in self.models.values():
            # Provider distribution
            provider = model.provider.value
            stats["by_provider"][provider] = stats["by_provider"].get(provider, 0) + 1

            # Capability distribution
            for capability in model.capabilities:
                cap_name = capability.value
                stats["by_capability"][cap_name] = (
                    stats["by_capability"].get(cap_name, 0) + 1
                )

            # Context length distribution
            if model.context_length < 8000:
                stats["context_length_distribution"]["small"] += 1
            elif model.context_length < 32000:
                stats["context_length_distribution"]["medium"] += 1
            elif model.context_length < 128000:
                stats["context_length_distribution"]["large"] += 1
            else:
                stats["context_length_distribution"]["very_large"] += 1

            # Performance distribution
            if model.performance_score < 0.3:
                stats["performance_score_distribution"]["low"] += 1
            elif model.performance_score < 0.7:
                stats["performance_score_distribution"]["medium"] += 1
            else:
                stats["performance_score_distribution"]["high"] += 1

            # Availability
            if model.is_available:
                stats["available_models"] += 1

            # Judge suitability
            if model.is_suitable_for_judging():
                stats["suitable_judges"] += 1

        return stats


# Global model manager instance
_model_manager: Optional[ModelManager] = None


def get_model_manager() -> ModelManager:
    """Get global model manager instance."""
    global _model_manager
    if _model_manager is None:
        _model_manager = ModelManager()
    return _model_manager


def list_eval_models(limit: int = 20, use_cache: bool = True) -> List[str]:
    """Get evaluation model IDs (backwards compatibility)."""
    manager = get_model_manager()

    if not use_cache:
        import asyncio

        asyncio.run(manager.refresh_models(force=True))

    return manager.get_model_ids(limit=limit)


def list_judge_models(limit: int = 2) -> List[str]:
    """Get judge model IDs."""
    manager = get_model_manager()
    judge_models = manager.get_judge_models(limit=limit)
    return [model.id for model in judge_models]
