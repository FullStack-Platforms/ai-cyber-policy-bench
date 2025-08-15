"""
Common utilities for Cyber-Policy-Bench.

This module provides shared functionality across the evaluation pipeline including
configuration management, API client initialization, retry logic, and error handling.
"""

import asyncio
import json
import logging
import os
import time
from typing import Dict, Any, Optional, Union, Callable, TypeVar
from pathlib import Path
import configparser
import openai
from datetime import datetime

# Type variable for generic retry functions
T = TypeVar("T")

# Global configuration instance
_config = None


class ConfigError(Exception):
    """Configuration related errors."""

    pass


class APIError(Exception):
    """API related errors."""

    pass


class ValidationError(Exception):
    """Data validation errors."""

    pass


def get_config(config_path: str = "config.cfg") -> configparser.ConfigParser:
    """
    Load and cache configuration from file.

    Args:
        config_path: Path to configuration file

    Returns:
        ConfigParser instance

    Raises:
        ConfigError: If configuration file cannot be loaded
    """
    global _config

    if _config is None:
        _config = configparser.ConfigParser()

        if not Path(config_path).exists():
            raise ConfigError(f"Configuration file not found: {config_path}")

        try:
            _config.read(config_path)
        except Exception as e:
            raise ConfigError(f"Failed to read configuration: {e}")

    return _config


def get_config_value(
    section: str, key: str, fallback: Any = None, value_type: type = str
) -> Any:
    """
    Get configuration value with type conversion and fallback.

    Args:
        section: Configuration section name
        key: Configuration key name
        fallback: Fallback value if key not found
        value_type: Type to convert value to (str, int, float, bool)

    Returns:
        Configuration value converted to specified type
    """
    config = get_config()

    try:
        if not config.has_section(section):
            if fallback is not None:
                return fallback
            raise ConfigError(f"Configuration section '{section}' not found")

        if not config.has_option(section, key):
            if fallback is not None:
                return fallback
            raise ConfigError(f"Configuration key '{section}.{key}' not found")

        value = config.get(
            section, key, fallback=str(fallback) if fallback is not None else None
        )

        # Type conversion
        if value_type is bool:
            return value.lower() in ("true", "1", "yes", "on")
        elif value_type is int:
            return int(value)
        elif value_type is float:
            return float(value)
        else:
            return value

    except (ValueError, TypeError) as e:
        raise ConfigError(f"Invalid type conversion for {section}.{key}: {e}")


def validate_config() -> Dict[str, Any]:
    """
    Validate configuration and return validation results.

    Returns:
        Dictionary with validation results and any issues found
    """
    config = get_config()
    issues = []
    warnings = []

    # Required sections
    required_sections = [
        "OpenRouter",
        "Vector Database",
        "Cyber Policy Benchmark",
        "Scoring",
        "Evaluation",
    ]

    for section in required_sections:
        if not config.has_section(section):
            issues.append(f"Missing required section: [{section}]")

    # API key validation
    openrouter_key = config.get("OpenRouter", "api_key", fallback="").strip()
    openai_key = config.get("OpenAI", "api_key", fallback="").strip()

    if not openrouter_key and not openai_key:
        warnings.append("No API keys configured - model evaluation will fail")

    # Path validation
    required_paths = [
        ("Vector Database", "db_path"),
        ("Cyber Policy Benchmark", "output_dir"),
        ("Cyber Policy Benchmark", "cache_dir"),
    ]

    for section, key in required_paths:
        if config.has_option(section, key):
            path = config.get(section, key)
            if path and not Path(path).parent.exists():
                warnings.append(
                    f"Parent directory does not exist for {section}.{key}: {path}"
                )

    # Judge model validation
    judge_mode = get_config_value("Scoring", "judge_mode", "single")
    if judge_mode == "dual":
        judge_1 = get_config_value("Scoring", "judge_model_1", "")
        judge_2 = get_config_value("Scoring", "judge_model_2", "")

        if not judge_1 or not judge_2:
            warnings.append(
                "Dual judge mode requires both judge_model_1 and judge_model_2"
            )

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "warnings": warnings,
        "sections": list(config.sections()),
    }


def get_openai_client() -> openai.OpenAI:
    """
    Create and configure OpenAI client based on configuration.

    Returns:
        Configured OpenAI client

    Raises:
        APIError: If client cannot be configured
    """
    config = get_config()

    # Try OpenRouter first
    openrouter_key = config.get("OpenRouter", "api_key", fallback="").strip()
    if openrouter_key and openrouter_key != "your-openrouter-key":
        return openai.OpenAI(
            base_url="https://openrouter.ai/api/v1", api_key=openrouter_key
        )

    # Try OpenAI
    openai_key = config.get("OpenAI", "api_key", fallback="").strip()
    if openai_key and openai_key != "your-openai-key":
        openai_url = config.get("OpenAI", "openai_compatible_url", fallback=None)
        base_url = openai_url if openai_url and openai_url.strip() else None

        return openai.OpenAI(api_key=openai_key, base_url=base_url)

    # No valid keys found
    raise APIError("No valid API keys found in configuration")


async def retry_with_backoff(
    func: Callable[..., T],
    *args,
    max_retries: int = None,
    base_delay: float = None,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    **kwargs,
) -> T:
    """
    Retry a function with exponential backoff.

    Args:
        func: Function to retry (can be async or sync)
        *args: Positional arguments for function
        max_retries: Maximum number of retries (from config if None)
        base_delay: Base delay between retries (from config if None)
        max_delay: Maximum delay between retries
        exponential_base: Base for exponential backoff
        **kwargs: Keyword arguments for function

    Returns:
        Function result

    Raises:
        Last exception if all retries exhausted
    """
    if max_retries is None:
        max_retries = get_config_value("Evaluation", "max_retries", 3, int)

    if base_delay is None:
        base_delay = get_config_value("Evaluation", "retry_delay", 2, float)

    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)

        except Exception as e:
            last_exception = e

            if attempt == max_retries:
                # Last attempt failed, raise the exception
                raise

            # Calculate delay with exponential backoff
            delay = min(base_delay * (exponential_base**attempt), max_delay)

            logging.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                f"Retrying in {delay:.1f}s..."
            )

            await asyncio.sleep(delay)

    # Should never reach here, but just in case
    raise last_exception


def setup_logging(
    level: str = "INFO", log_file: Optional[str] = None
) -> logging.Logger:
    """
    Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup root logger
    logger = logging.getLogger("cyber_benchmark")
    logger.setLevel(numeric_level)

    # Clear any existing handlers
    logger.handlers.clear()

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def save_json(data: Any, file_path: Union[str, Path], indent: int = 2) -> None:
    """
    Save data to JSON file with error handling.

    Args:
        data: Data to save
        file_path: Path to save file
        indent: JSON indentation

    Raises:
        ValidationError: If data cannot be serialized
    """
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False, default=str)

    except (TypeError, ValueError) as e:
        raise ValidationError(f"Cannot serialize data to JSON: {e}")
    except OSError as e:
        raise ValidationError(f"Cannot write to file {file_path}: {e}")


def load_json(file_path: Union[str, Path]) -> Any:
    """
    Load data from JSON file with error handling.

    Args:
        file_path: Path to JSON file

    Returns:
        Loaded data

    Raises:
        ValidationError: If file cannot be loaded or parsed
    """
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            raise ValidationError(f"File does not exist: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    except json.JSONDecodeError as e:
        raise ValidationError(f"Invalid JSON in file {file_path}: {e}")
    except OSError as e:
        raise ValidationError(f"Cannot read file {file_path}: {e}")


def truncate_text(text: str, max_length: int, suffix: str = "...[truncated]") -> str:
    """
    Truncate text to maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum allowed length
        suffix: Suffix to add to truncated text

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    # Account for suffix length
    truncate_length = max_length - len(suffix)
    if truncate_length <= 0:
        return suffix[:max_length]

    return text[:truncate_length] + suffix


def get_timestamp() -> str:
    """Get current timestamp in ISO format."""
    return datetime.now().isoformat()


def ensure_directory(path: Union[str, Path]) -> Path:
    """
    Ensure directory exists, creating it if necessary.

    Args:
        path: Directory path

    Returns:
        Path object for the directory
    """
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path


def get_file_size(file_path: Union[str, Path]) -> int:
    """
    Get file size in bytes.

    Args:
        file_path: Path to file

    Returns:
        File size in bytes, or 0 if file doesn't exist
    """
    try:
        return Path(file_path).stat().st_size
    except (OSError, FileNotFoundError):
        return 0


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human readable string.

    Args:
        seconds: Duration in seconds

    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"


class Timer:
    """Context manager for timing operations."""

    def __init__(self, description: str = "Operation"):
        self.description = description
        self.start_time = None
        self.end_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = time.time()
        duration = self.end_time - self.start_time
        print(f"{self.description} completed in {format_duration(duration)}")

    @property
    def duration(self) -> Optional[float]:
        """Get duration in seconds if timing is complete."""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None


# Environment variable helpers
def get_env_bool(name: str, default: bool = False) -> bool:
    """Get boolean value from environment variable."""
    value = os.environ.get(name, "").lower()
    if value in ("true", "1", "yes", "on"):
        return True
    elif value in ("false", "0", "no", "off"):
        return False
    else:
        return default


def get_env_int(name: str, default: int = 0) -> int:
    """Get integer value from environment variable."""
    try:
        return int(os.environ.get(name, str(default)))
    except ValueError:
        return default


def get_env_float(name: str, default: float = 0.0) -> float:
    """Get float value from environment variable."""
    try:
        return float(os.environ.get(name, str(default)))
    except ValueError:
        return default
