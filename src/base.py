"""
Base classes for Cyber-Policy-Bench.

This module provides abstract base classes and common functionality
to reduce code duplication across evaluators, scorers, and other components.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum
import logging
from pathlib import Path

from .utils import get_openai_client, retry_with_backoff, setup_logging, get_timestamp


class ComponentStatus(Enum):
    """Status of a benchmark component."""

    UNINITIALIZED = "uninitialized"
    INITIALIZING = "initializing"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
    COMPLETED = "completed"


@dataclass
class ComponentMetrics:
    """Metrics for benchmark components."""

    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    total_duration: float = 0.0
    average_duration: float = 0.0

    def update_success(self, duration: float) -> None:
        """Update metrics for successful operation."""
        self.total_operations += 1
        self.successful_operations += 1
        self.total_duration += duration
        self.average_duration = self.total_duration / self.total_operations

    def update_failure(self, duration: float = 0.0) -> None:
        """Update metrics for failed operation."""
        self.total_operations += 1
        self.failed_operations += 1
        self.total_duration += duration
        self.average_duration = self.total_duration / max(1, self.total_operations)

    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_operations == 0:
            return 0.0
        return (self.successful_operations / self.total_operations) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_operations": self.total_operations,
            "successful_operations": self.successful_operations,
            "failed_operations": self.failed_operations,
            "success_rate": self.success_rate,
            "total_duration": self.total_duration,
            "average_duration": self.average_duration,
        }


class BaseComponent(ABC):
    """Base class for all benchmark components."""

    def __init__(self, component_name: str, enable_logging: bool = True):
        """Initialize base component."""
        self.component_name = component_name
        self.status = ComponentStatus.UNINITIALIZED
        self.metrics = ComponentMetrics()
        self.created_at = get_timestamp()
        self.last_operation_at: Optional[str] = None

        # Setup logging
        if enable_logging:
            self.logger = setup_logging()
        else:
            self.logger = logging.getLogger(component_name)

    def set_status(self, status: ComponentStatus) -> None:
        """Update component status."""
        self.logger.debug(
            f"{self.component_name} status: {self.status.value} -> {status.value}"
        )
        self.status = status

    def log_operation(
        self,
        operation_name: str,
        success: bool,
        duration: float = 0.0,
        details: Optional[Dict] = None,
    ) -> None:
        """Log operation result and update metrics."""
        self.last_operation_at = get_timestamp()

        if success:
            self.metrics.update_success(duration)
            self.logger.info(
                f"{operation_name} completed successfully in {duration:.2f}s"
            )
        else:
            self.metrics.update_failure(duration)
            self.logger.warning(f"{operation_name} failed after {duration:.2f}s")

        if details:
            self.logger.debug(f"{operation_name} details: {details}")

    def get_status_info(self) -> Dict[str, Any]:
        """Get comprehensive status information."""
        return {
            "component_name": self.component_name,
            "status": self.status.value,
            "created_at": self.created_at,
            "last_operation_at": self.last_operation_at,
            "metrics": self.metrics.to_dict(),
        }


class BaseEvaluator(BaseComponent):
    """Base class for evaluation components."""

    def __init__(self, component_name: str = "evaluator"):
        """Initialize base evaluator."""
        super().__init__(component_name)
        self.client = None
        self._initialize_client()

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            self.set_status(ComponentStatus.INITIALIZING)
            self.client = get_openai_client()
            self.set_status(ComponentStatus.READY)
            self.logger.info("OpenAI client initialized successfully")
        except Exception as e:
            self.set_status(ComponentStatus.ERROR)
            self.logger.error(f"Failed to initialize OpenAI client: {e}")
            raise

    async def safe_api_call(
        self, operation_name: str, api_call: callable, *args, **kwargs
    ) -> Any:
        """
        Safely execute API call with retry logic and error handling.

        Args:
            operation_name: Name of the operation for logging
            api_call: API function to call
            *args: Positional arguments for API call
            **kwargs: Keyword arguments for API call

        Returns:
            API call result

        Raises:
            Exception: If all retries are exhausted
        """
        import time

        start_time = time.time()

        try:
            result = await retry_with_backoff(api_call, *args, **kwargs)
            duration = time.time() - start_time
            self.log_operation(operation_name, True, duration)
            return result

        except Exception as e:
            duration = time.time() - start_time
            self.log_operation(operation_name, False, duration, {"error": str(e)})
            raise

    @abstractmethod
    async def evaluate(self, *args, **kwargs) -> Any:
        """Abstract method for evaluation logic."""
        pass


class BaseScorer(BaseComponent):
    """Base class for scoring components."""

    def __init__(self, component_name: str = "scorer"):
        """Initialize base scorer."""
        super().__init__(component_name)
        self.client = None
        self._initialize_client()

        # Scoring statistics
        self.total_scores_computed = 0
        self.scores_by_method: Dict[str, int] = {}

    def _initialize_client(self) -> None:
        """Initialize OpenAI client."""
        try:
            self.set_status(ComponentStatus.INITIALIZING)
            self.client = get_openai_client()
            self.set_status(ComponentStatus.READY)
            self.logger.info("Scorer OpenAI client initialized successfully")
        except Exception as e:
            self.set_status(ComponentStatus.ERROR)
            self.logger.error(f"Failed to initialize scorer OpenAI client: {e}")
            raise

    def update_scoring_stats(self, scoring_method: str) -> None:
        """Update scoring statistics."""
        self.total_scores_computed += 1
        self.scores_by_method[scoring_method] = (
            self.scores_by_method.get(scoring_method, 0) + 1
        )

    def get_scoring_stats(self) -> Dict[str, Any]:
        """Get scoring statistics."""
        return {
            "total_scores_computed": self.total_scores_computed,
            "scores_by_method": self.scores_by_method,
            "average_scores_per_method": {
                method: count / max(1, len(self.scores_by_method))
                for method, count in self.scores_by_method.items()
            },
        }

    @abstractmethod
    async def score(self, *args, **kwargs) -> Any:
        """Abstract method for scoring logic."""
        pass


class BaseProcessor(BaseComponent):
    """Base class for data processing components."""

    def __init__(
        self,
        component_name: str = "processor",
        input_dir: str = None,
        output_dir: str = None,
    ):
        """Initialize base processor."""
        super().__init__(component_name)

        # Setup directories
        self.input_dir = Path(input_dir) if input_dir else None
        self.output_dir = Path(output_dir) if output_dir else None

        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

        # Processing statistics
        self.files_processed = 0
        self.total_input_size = 0
        self.total_output_size = 0
        self.processing_errors: List[Dict[str, Any]] = []

    def log_processing_error(self, file_path: str, error: Exception) -> None:
        """Log processing error."""
        error_info = {
            "file_path": str(file_path),
            "error": str(error),
            "error_type": type(error).__name__,
            "timestamp": get_timestamp(),
        }
        self.processing_errors.append(error_info)
        self.logger.error(f"Processing error for {file_path}: {error}")

    def update_processing_stats(self, input_size: int, output_size: int) -> None:
        """Update processing statistics."""
        self.files_processed += 1
        self.total_input_size += input_size
        self.total_output_size += output_size

    def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics."""
        return {
            "files_processed": self.files_processed,
            "total_input_size": self.total_input_size,
            "total_output_size": self.total_output_size,
            "compression_ratio": (
                (self.total_output_size / max(1, self.total_input_size))
                if self.total_input_size > 0
                else 0.0
            ),
            "processing_errors": len(self.processing_errors),
            "error_rate": len(self.processing_errors)
            / max(1, self.files_processed)
            * 100.0,
        }

    @abstractmethod
    def process(self, *args, **kwargs) -> Any:
        """Abstract method for processing logic."""
        pass


class BasePipeline(BaseComponent):
    """Base class for processing pipelines."""

    def __init__(self, component_name: str = "pipeline"):
        """Initialize base pipeline."""
        super().__init__(component_name)
        self.components: List[BaseComponent] = []
        self.pipeline_metrics: Dict[str, Any] = {}

    def add_component(self, component: BaseComponent) -> None:
        """Add component to pipeline."""
        self.components.append(component)
        self.logger.info(f"Added component {component.component_name} to pipeline")

    def get_component_by_name(self, name: str) -> Optional[BaseComponent]:
        """Get component by name."""
        for component in self.components:
            if component.component_name == name:
                return component
        return None

    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get status of all components in pipeline."""
        component_statuses = {}

        for component in self.components:
            component_statuses[component.component_name] = component.get_status_info()

        # Overall pipeline status
        all_ready = all(c.status == ComponentStatus.READY for c in self.components)
        any_error = any(c.status == ComponentStatus.ERROR for c in self.components)
        any_running = any(c.status == ComponentStatus.RUNNING for c in self.components)

        if any_error:
            overall_status = ComponentStatus.ERROR
        elif any_running:
            overall_status = ComponentStatus.RUNNING
        elif all_ready:
            overall_status = ComponentStatus.READY
        else:
            overall_status = ComponentStatus.INITIALIZING

        return {
            "pipeline_name": self.component_name,
            "overall_status": overall_status.value,
            "component_count": len(self.components),
            "components": component_statuses,
            "metrics": self.get_status_info(),
        }

    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate pipeline configuration and components."""
        validation_results = {"valid": True, "issues": [], "warnings": []}

        # Check if pipeline has components
        if not self.components:
            validation_results["valid"] = False
            validation_results["issues"].append("Pipeline has no components")

        # Check component dependencies and configurations
        for component in self.components:
            if component.status == ComponentStatus.ERROR:
                validation_results["valid"] = False
                validation_results["issues"].append(
                    f"Component {component.component_name} is in error state"
                )
            elif component.status == ComponentStatus.UNINITIALIZED:
                validation_results["warnings"].append(
                    f"Component {component.component_name} is not initialized"
                )

        return validation_results

    @abstractmethod
    async def run(self, *args, **kwargs) -> Any:
        """Abstract method for running the pipeline."""
        pass


class ConfigurableMixin:
    """Mixin for components that need configuration management."""

    def __init__(self, config_section: str = None):
        """Initialize configurable component."""
        self.config_section = config_section or getattr(
            self, "component_name", "default"
        )
        self._config_cache: Dict[str, Any] = {}

    def get_config_value(
        self, key: str, default: Any = None, value_type: type = str
    ) -> Any:
        """Get configuration value with caching."""
        cache_key = f"{self.config_section}.{key}"

        if cache_key not in self._config_cache:
            from .utils import get_config_value

            self._config_cache[cache_key] = get_config_value(
                self.config_section, key, default, value_type
            )

        return self._config_cache[cache_key]

    def invalidate_config_cache(self) -> None:
        """Clear configuration cache."""
        self._config_cache.clear()


class MonitoringMixin:
    """Mixin for components that need monitoring capabilities."""

    def __init__(self):
        """Initialize monitoring capabilities."""
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self.checkpoint_times: Dict[str, float] = {}
        self.custom_metrics: Dict[str, Any] = {}

    def start_monitoring(self) -> None:
        """Start monitoring session."""
        import time

        self.start_time = time.time()
        self.checkpoint_times["start"] = self.start_time

    def checkpoint(self, name: str) -> float:
        """Add monitoring checkpoint."""
        import time

        current_time = time.time()
        self.checkpoint_times[name] = current_time

        if self.start_time:
            return current_time - self.start_time
        return 0.0

    def end_monitoring(self) -> Dict[str, Any]:
        """End monitoring session and return metrics."""
        import time

        self.end_time = time.time()

        if self.start_time:
            total_duration = self.end_time - self.start_time

            # Calculate checkpoint durations
            checkpoint_durations = {}
            prev_time = self.start_time

            for name, timestamp in self.checkpoint_times.items():
                if name != "start":
                    checkpoint_durations[name] = timestamp - prev_time
                    prev_time = timestamp

            return {
                "total_duration": total_duration,
                "start_time": self.start_time,
                "end_time": self.end_time,
                "checkpoints": self.checkpoint_times,
                "checkpoint_durations": checkpoint_durations,
                "custom_metrics": self.custom_metrics,
            }

        return {"error": "Monitoring was not started"}

    def set_custom_metric(self, name: str, value: Any) -> None:
        """Set custom monitoring metric."""
        self.custom_metrics[name] = value

    def increment_custom_metric(self, name: str, value: Union[int, float] = 1) -> None:
        """Increment custom monitoring metric."""
        current_value = self.custom_metrics.get(name, 0)
        self.custom_metrics[name] = current_value + value
