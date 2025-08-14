"""
Reporting and monitoring functionality for Cyber-Policy-Bench.

This module provides comprehensive reporting capabilities including HTML reports,
performance metrics tracking, model reliability scoring, and comparison reports.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field
import statistics

from .utils import (
    save_json,
    load_json,
    ensure_directory,
    get_timestamp,
    format_duration,
)
from .base import BaseComponent, ComponentStatus, MonitoringMixin


@dataclass
class BenchmarkMetrics:
    """Comprehensive benchmark metrics."""

    total_evaluations: int = 0
    total_models: int = 0
    total_questions: int = 0
    evaluation_modes: List[str] = field(default_factory=list)

    # Timing metrics
    total_duration: float = 0.0
    average_evaluation_time: float = 0.0

    # Success/failure metrics
    successful_evaluations: int = 0
    failed_evaluations: int = 0
    scoring_failures: int = 0

    # Score statistics
    overall_average_score: float = 0.0
    score_std_dev: float = 0.0
    min_score: float = 0.0
    max_score: float = 0.0

    # Model performance
    best_performing_model: Optional[str] = None
    worst_performing_model: Optional[str] = None

    # Mode performance
    mode_performance: Dict[str, float] = field(default_factory=dict)

    def calculate_success_rate(self) -> float:
        """Calculate overall success rate."""
        if self.total_evaluations == 0:
            return 0.0
        return (self.successful_evaluations / self.total_evaluations) * 100.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert metrics to dictionary."""
        return {
            "total_evaluations": self.total_evaluations,
            "total_models": self.total_models,
            "total_questions": self.total_questions,
            "evaluation_modes": self.evaluation_modes,
            "total_duration": self.total_duration,
            "average_evaluation_time": self.average_evaluation_time,
            "successful_evaluations": self.successful_evaluations,
            "failed_evaluations": self.failed_evaluations,
            "success_rate": self.calculate_success_rate(),
            "scoring_failures": self.scoring_failures,
            "overall_average_score": self.overall_average_score,
            "score_std_dev": self.score_std_dev,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "best_performing_model": self.best_performing_model,
            "worst_performing_model": self.worst_performing_model,
            "mode_performance": self.mode_performance,
        }


@dataclass
class ModelPerformanceReport:
    """Performance report for a specific model."""

    model_name: str
    total_evaluations: int = 0
    successful_evaluations: int = 0
    average_score: float = 0.0
    score_std_dev: float = 0.0
    scores_by_mode: Dict[str, List[float]] = field(default_factory=dict)

    # Reliability metrics
    api_success_rate: float = 0.0
    average_response_time: float = 0.0
    timeout_count: int = 0
    error_count: int = 0

    # Quality metrics
    high_quality_responses: int = 0  # Scores > 0.8
    medium_quality_responses: int = 0  # Scores 0.4-0.8
    low_quality_responses: int = 0  # Scores < 0.4

    def calculate_success_rate(self) -> float:
        """Calculate model success rate."""
        if self.total_evaluations == 0:
            return 0.0
        return (self.successful_evaluations / self.total_evaluations) * 100.0

    def calculate_quality_distribution(self) -> Dict[str, float]:
        """Calculate distribution of response quality."""
        total = (
            self.high_quality_responses
            + self.medium_quality_responses
            + self.low_quality_responses
        )
        if total == 0:
            return {"high": 0.0, "medium": 0.0, "low": 0.0}

        return {
            "high": (self.high_quality_responses / total) * 100.0,
            "medium": (self.medium_quality_responses / total) * 100.0,
            "low": (self.low_quality_responses / total) * 100.0,
        }

    def get_mode_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics by evaluation mode."""
        mode_stats = {}
        for mode, scores in self.scores_by_mode.items():
            if scores:
                mode_stats[mode] = {
                    "average": statistics.mean(scores),
                    "std_dev": statistics.stdev(scores) if len(scores) > 1 else 0.0,
                    "min": min(scores),
                    "max": max(scores),
                    "count": len(scores),
                }
            else:
                mode_stats[mode] = {
                    "average": 0.0,
                    "std_dev": 0.0,
                    "min": 0.0,
                    "max": 0.0,
                    "count": 0,
                }

        return mode_stats


class BenchmarkReporter(BaseComponent, MonitoringMixin):
    """Comprehensive benchmark reporting system."""

    def __init__(
        self, output_dir: str = "experiment_results", reports_dir: str = "reports"
    ):
        """Initialize benchmark reporter."""
        BaseComponent.__init__(self, "benchmark_reporter")
        MonitoringMixin.__init__(self)

        self.output_dir = Path(output_dir)
        self.reports_dir = Path(reports_dir)
        ensure_directory(self.reports_dir)

        self.set_status(ComponentStatus.READY)

    def analyze_benchmark_results(
        self, results: Dict[str, List[Dict]], summary: Optional[Dict] = None
    ) -> BenchmarkMetrics:
        """Analyze benchmark results and generate comprehensive metrics."""
        self.logger.info("Analyzing benchmark results...")

        metrics = BenchmarkMetrics()
        all_scores = []
        model_scores = {}
        mode_scores = {}

        # Analyze results by model
        for model_name, model_results in results.items():
            model_scores[model_name] = []

            for result in model_results:
                metrics.total_evaluations += 1

                # Count successful evaluations
                if result.get("accuracy_score") is not None:
                    metrics.successful_evaluations += 1
                    score = result["accuracy_score"]
                    all_scores.append(score)
                    model_scores[model_name].append(score)

                    # Track by evaluation mode
                    mode = result.get("evaluation_mode", "unknown")
                    if mode not in mode_scores:
                        mode_scores[mode] = []
                    mode_scores[mode].append(score)

                else:
                    metrics.failed_evaluations += 1

                # Check for scoring failures
                if result.get("scores", {}).get("error"):
                    metrics.scoring_failures += 1

        # Calculate overall statistics
        metrics.total_models = len(results)
        if all_scores:
            metrics.overall_average_score = statistics.mean(all_scores)
            metrics.score_std_dev = (
                statistics.stdev(all_scores) if len(all_scores) > 1 else 0.0
            )
            metrics.min_score = min(all_scores)
            metrics.max_score = max(all_scores)

        # Find best and worst performing models
        if model_scores:
            model_averages = {
                model: statistics.mean(scores) if scores else 0.0
                for model, scores in model_scores.items()
            }
            metrics.best_performing_model = max(model_averages, key=model_averages.get)
            metrics.worst_performing_model = min(model_averages, key=model_averages.get)

        # Calculate mode performance
        metrics.evaluation_modes = list(mode_scores.keys())
        metrics.mode_performance = {
            mode: statistics.mean(scores) if scores else 0.0
            for mode, scores in mode_scores.items()
        }

        # Estimate timing if available in summary
        if summary and "total_duration" in summary:
            metrics.total_duration = summary["total_duration"]
            metrics.average_evaluation_time = metrics.total_duration / max(
                1, metrics.total_evaluations
            )

        return metrics

    def generate_model_performance_reports(
        self, results: Dict[str, List[Dict]]
    ) -> Dict[str, ModelPerformanceReport]:
        """Generate detailed performance reports for each model."""
        self.logger.info("Generating model performance reports...")

        model_reports = {}

        for model_name, model_results in results.items():
            report = ModelPerformanceReport(model_name=model_name)
            report.total_evaluations = len(model_results)

            scores = []
            successful_count = 0

            for result in model_results:
                score = result.get("accuracy_score")
                if score is not None:
                    successful_count += 1
                    scores.append(score)

                    # Track evaluation mode performance
                    mode = result.get("evaluation_mode", "unknown")
                    if mode not in report.scores_by_mode:
                        report.scores_by_mode[mode] = []
                    report.scores_by_mode[mode].append(score)

                    # Categorize response quality
                    if score > 0.8:
                        report.high_quality_responses += 1
                    elif score >= 0.4:
                        report.medium_quality_responses += 1
                    else:
                        report.low_quality_responses += 1

                # Track errors
                if result.get("model_response", "").startswith("Error:"):
                    report.error_count += 1

            report.successful_evaluations = successful_count

            # Calculate statistics
            if scores:
                report.average_score = statistics.mean(scores)
                report.score_std_dev = (
                    statistics.stdev(scores) if len(scores) > 1 else 0.0
                )

            # Simulate API reliability metrics (would be tracked in real implementation)
            report.api_success_rate = (
                successful_count / max(1, report.total_evaluations)
            ) * 100.0

            model_reports[model_name] = report

        return model_reports

    def generate_html_report(
        self,
        metrics: BenchmarkMetrics,
        model_reports: Dict[str, ModelPerformanceReport],
        output_filename: str = "benchmark_report.html",
    ) -> Path:
        """Generate comprehensive HTML report."""
        self.logger.info(f"Generating HTML report: {output_filename}")

        html_content = self._create_html_report_content(metrics, model_reports)

        report_path = self.reports_dir / output_filename
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"HTML report saved to {report_path}")
        return report_path

    def _create_html_report_content(
        self,
        metrics: BenchmarkMetrics,
        model_reports: Dict[str, ModelPerformanceReport],
    ) -> str:
        """Create HTML content for the report."""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Cyber-Policy-Bench Report</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f5f5f5;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                }}
                .header .subtitle {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                    font-size: 1.1em;
                }}
                .section {{
                    background: white;
                    margin: 20px 0;
                    padding: 25px;
                    border-radius: 10px;
                    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                }}
                .section h2 {{
                    color: #4a5568;
                    border-bottom: 2px solid #e2e8f0;
                    padding-bottom: 10px;
                    margin-top: 0;
                }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                    margin: 20px 0;
                }}
                .metric-card {{
                    background: #f7fafc;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #4299e1;
                    text-align: center;
                }}
                .metric-card h3 {{
                    margin: 0 0 10px 0;
                    color: #2d3748;
                    font-size: 1.1em;
                }}
                .metric-card .value {{
                    font-size: 2em;
                    font-weight: bold;
                    color: #4299e1;
                }}
                .metric-card .label {{
                    color: #718096;
                    font-size: 0.9em;
                    margin-top: 5px;
                }}
                .model-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 20px 0;
                }}
                .model-table th, .model-table td {{
                    padding: 12px;
                    text-align: left;
                    border-bottom: 1px solid #e2e8f0;
                }}
                .model-table th {{
                    background-color: #f7fafc;
                    font-weight: 600;
                    color: #4a5568;
                }}
                .model-table tr:hover {{
                    background-color: #f7fafc;
                }}
                .score-high {{ color: #38a169; font-weight: bold; }}
                .score-medium {{ color: #d69e2e; font-weight: bold; }}
                .score-low {{ color: #e53e3e; font-weight: bold; }}
                .progress-bar {{
                    width: 100%;
                    height: 20px;
                    background-color: #e2e8f0;
                    border-radius: 10px;
                    overflow: hidden;
                }}
                .progress-fill {{
                    height: 100%;
                    background: linear-gradient(90deg, #48bb78, #38a169);
                    transition: width 0.3s ease;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #718096;
                    font-size: 0.9em;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🛡️ Cyber-Policy-Bench Report</h1>
                <div class="subtitle">Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>
            </div>
            
            <div class="section">
                <h2>📊 Overall Performance Metrics</h2>
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h3>Total Evaluations</h3>
                        <div class="value">{metrics.total_evaluations:,}</div>
                        <div class="label">across {metrics.total_models} models</div>
                    </div>
                    <div class="metric-card">
                        <h3>Success Rate</h3>
                        <div class="value">{metrics.calculate_success_rate():.1f}%</div>
                        <div class="label">{metrics.successful_evaluations} successful</div>
                    </div>
                    <div class="metric-card">
                        <h3>Average Score</h3>
                        <div class="value">{metrics.overall_average_score:.3f}</div>
                        <div class="label">±{metrics.score_std_dev:.3f} std dev</div>
                    </div>
                    <div class="metric-card">
                        <h3>Score Range</h3>
                        <div class="value">{metrics.min_score:.3f} - {metrics.max_score:.3f}</div>
                        <div class="label">min - max</div>
                    </div>
                </div>
                
                {self._generate_duration_section(metrics)}
            </div>
            
            <div class="section">
                <h2>🎯 Performance by Evaluation Mode</h2>
                {self._generate_mode_performance_section(metrics)}
            </div>
            
            <div class="section">
                <h2>🤖 Model Performance Comparison</h2>
                {self._generate_model_comparison_table(model_reports)}
            </div>
            
            <div class="section">
                <h2>📈 Detailed Model Analysis</h2>
                {self._generate_detailed_model_analysis(model_reports)}
            </div>
            
            <div class="footer">
                Report generated by Cyber-Policy-Bench Suite<br>
                <a href="https://github.com/your-repo/ai-cyber-policy-bench">View on GitHub</a>
            </div>
        </body>
        </html>
        """

        return html

    def _generate_duration_section(self, metrics: BenchmarkMetrics) -> str:
        """Generate duration metrics section."""
        if metrics.total_duration == 0:
            return ""

        return f"""
        <div style="margin-top: 20px;">
            <h3>⏱️ Timing Statistics</h3>
            <div class="metrics-grid">
                <div class="metric-card">
                    <h3>Total Duration</h3>
                    <div class="value">{format_duration(metrics.total_duration)}</div>
                </div>
                <div class="metric-card">
                    <h3>Average per Evaluation</h3>
                    <div class="value">{format_duration(metrics.average_evaluation_time)}</div>
                </div>
            </div>
        </div>
        """

    def _generate_mode_performance_section(self, metrics: BenchmarkMetrics) -> str:
        """Generate evaluation mode performance section."""
        if not metrics.mode_performance:
            return "<p>No mode performance data available.</p>"

        mode_html = "<div class='metrics-grid'>"

        for mode, avg_score in metrics.mode_performance.items():
            score_class = self._get_score_class(avg_score)
            mode_html += f"""
            <div class="metric-card">
                <h3>{mode.replace('_', ' ').title()}</h3>
                <div class="value {score_class}">{avg_score:.3f}</div>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: {avg_score * 100}%;"></div>
                </div>
            </div>
            """

        mode_html += "</div>"
        return mode_html

    def _generate_model_comparison_table(
        self, model_reports: Dict[str, ModelPerformanceReport]
    ) -> str:
        """Generate model comparison table."""
        if not model_reports:
            return "<p>No model performance data available.</p>"

        # Sort models by average score
        sorted_models = sorted(
            model_reports.items(), key=lambda x: x[1].average_score, reverse=True
        )

        table_html = """
        <table class="model-table">
            <thead>
                <tr>
                    <th>Model</th>
                    <th>Evaluations</th>
                    <th>Success Rate</th>
                    <th>Average Score</th>
                    <th>High Quality</th>
                    <th>Performance</th>
                </tr>
            </thead>
            <tbody>
        """

        for model_name, report in sorted_models:
            score_class = self._get_score_class(report.average_score)
            quality_dist = report.calculate_quality_distribution()

            table_html += f"""
            <tr>
                <td><strong>{model_name}</strong></td>
                <td>{report.total_evaluations}</td>
                <td>{report.calculate_success_rate():.1f}%</td>
                <td class="{score_class}">{report.average_score:.3f}</td>
                <td>{quality_dist['high']:.1f}%</td>
                <td>
                    <div class="progress-bar">
                        <div class="progress-fill" style="width: {report.average_score * 100}%;"></div>
                    </div>
                </td>
            </tr>
            """

        table_html += "</tbody></table>"
        return table_html

    def _generate_detailed_model_analysis(
        self, model_reports: Dict[str, ModelPerformanceReport]
    ) -> str:
        """Generate detailed model analysis section."""
        if not model_reports:
            return "<p>No detailed model data available.</p>"

        analysis_html = ""

        for model_name, report in model_reports.items():
            quality_dist = report.calculate_quality_distribution()
            mode_performance = report.get_mode_performance()

            analysis_html += f"""
            <div style="border: 1px solid #e2e8f0; border-radius: 8px; padding: 20px; margin: 15px 0;">
                <h3>🔍 {model_name}</h3>
                
                <div class="metrics-grid">
                    <div class="metric-card">
                        <h4>Response Quality</h4>
                        <div style="font-size: 0.9em;">
                            <div>High (>0.8): <strong>{quality_dist['high']:.1f}%</strong></div>
                            <div>Medium (0.4-0.8): <strong>{quality_dist['medium']:.1f}%</strong></div>
                            <div>Low (<0.4): <strong>{quality_dist['low']:.1f}%</strong></div>
                        </div>
                    </div>
                    
                    <div class="metric-card">
                        <h4>Reliability</h4>
                        <div style="font-size: 0.9em;">
                            <div>Success Rate: <strong>{report.calculate_success_rate():.1f}%</strong></div>
                            <div>Errors: <strong>{report.error_count}</strong></div>
                        </div>
                    </div>
                </div>
                
                {self._generate_mode_performance_for_model(mode_performance)}
            </div>
            """

        return analysis_html

    def _generate_mode_performance_for_model(
        self, mode_performance: Dict[str, Dict[str, float]]
    ) -> str:
        """Generate mode performance section for a specific model."""
        if not mode_performance:
            return ""

        mode_html = "<h4>Performance by Evaluation Mode:</h4><div class='metrics-grid' style='grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));'>"

        for mode, stats in mode_performance.items():
            score_class = self._get_score_class(stats["average"])
            mode_html += f"""
            <div style="padding: 10px; border: 1px solid #e2e8f0; border-radius: 6px;">
                <div style="font-weight: bold; color: #4a5568;">{mode.replace('_', ' ').title()}</div>
                <div class="{score_class}" style="font-size: 1.2em;">{stats['average']:.3f}</div>
                <div style="font-size: 0.8em; color: #718096;">
                    ({stats['count']} evaluations)
                </div>
            </div>
            """

        mode_html += "</div>"
        return mode_html

    def _get_score_class(self, score: float) -> str:
        """Get CSS class based on score value."""
        if score >= 0.8:
            return "score-high"
        elif score >= 0.4:
            return "score-medium"
        else:
            return "score-low"

    def generate_comparison_report(
        self, current_results: Dict, previous_results_path: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Generate comparison report with previous benchmark results."""
        self.logger.info("Generating comparison report...")

        if not previous_results_path or not previous_results_path.exists():
            return {"error": "No previous results available for comparison"}

        try:
            previous_results = load_json(previous_results_path)

            comparison = {
                "timestamp": get_timestamp(),
                "current_metrics": self.analyze_benchmark_results(current_results),
                "previous_metrics": self.analyze_benchmark_results(previous_results),
                "improvements": {},
                "regressions": {},
                "new_models": [],
                "removed_models": [],
            }

            # Compare models
            current_models = set(current_results.keys())
            previous_models = set(previous_results.keys())

            comparison["new_models"] = list(current_models - previous_models)
            comparison["removed_models"] = list(previous_models - current_models)

            # Compare performance for common models
            common_models = current_models & previous_models

            for model in common_models:
                current_scores = [
                    r.get("accuracy_score", 0)
                    for r in current_results[model]
                    if r.get("accuracy_score") is not None
                ]
                previous_scores = [
                    r.get("accuracy_score", 0)
                    for r in previous_results[model]
                    if r.get("accuracy_score") is not None
                ]

                if current_scores and previous_scores:
                    current_avg = statistics.mean(current_scores)
                    previous_avg = statistics.mean(previous_scores)
                    difference = current_avg - previous_avg

                    if difference > 0.05:  # Significant improvement
                        comparison["improvements"][model] = {
                            "current_score": current_avg,
                            "previous_score": previous_avg,
                            "improvement": difference,
                        }
                    elif difference < -0.05:  # Significant regression
                        comparison["regressions"][model] = {
                            "current_score": current_avg,
                            "previous_score": previous_avg,
                            "regression": abs(difference),
                        }

            return comparison

        except Exception as e:
            self.logger.error(f"Error generating comparison report: {e}")
            return {"error": f"Failed to generate comparison: {str(e)}"}

    def export_metrics_to_json(
        self,
        metrics: BenchmarkMetrics,
        model_reports: Dict[str, ModelPerformanceReport],
        filename: str = "benchmark_metrics.json",
    ) -> Path:
        """Export metrics to JSON format."""
        export_data = {
            "timestamp": get_timestamp(),
            "benchmark_metrics": metrics.to_dict(),
            "model_reports": {
                model_name: {
                    "model_name": report.model_name,
                    "total_evaluations": report.total_evaluations,
                    "successful_evaluations": report.successful_evaluations,
                    "success_rate": report.calculate_success_rate(),
                    "average_score": report.average_score,
                    "score_std_dev": report.score_std_dev,
                    "quality_distribution": report.calculate_quality_distribution(),
                    "mode_performance": report.get_mode_performance(),
                    "api_success_rate": report.api_success_rate,
                    "error_count": report.error_count,
                }
                for model_name, report in model_reports.items()
            },
        }

        export_path = self.reports_dir / filename
        save_json(export_data, export_path)

        self.logger.info(f"Metrics exported to {export_path}")
        return export_path

    def generate_all_reports(
        self,
        results: Dict[str, List[Dict]],
        summary: Optional[Dict] = None,
        previous_results_path: Optional[Path] = None,
    ) -> Dict[str, Path]:
        """Generate all available reports."""
        self.logger.info("Generating comprehensive report suite...")

        self.start_monitoring()

        try:
            # Analyze results
            metrics = self.analyze_benchmark_results(results, summary)
            model_reports = self.generate_model_performance_reports(results)

            # Generate reports
            generated_reports = {}

            # HTML report
            html_report_path = self.generate_html_report(metrics, model_reports)
            generated_reports["html_report"] = html_report_path

            # JSON metrics export
            json_export_path = self.export_metrics_to_json(metrics, model_reports)
            generated_reports["json_export"] = json_export_path

            # Comparison report if previous results available
            if previous_results_path:
                comparison = self.generate_comparison_report(
                    results, previous_results_path
                )
                comparison_path = self.reports_dir / "comparison_report.json"
                save_json(comparison, comparison_path)
                generated_reports["comparison_report"] = comparison_path

            self.set_status(ComponentStatus.COMPLETED)
            self.logger.info(f"Generated {len(generated_reports)} reports")

            return generated_reports

        except Exception as e:
            self.set_status(ComponentStatus.ERROR)
            self.logger.error(f"Error generating reports: {e}")
            raise

        finally:
            monitoring_results = self.end_monitoring()
            self.logger.info(
                f"Report generation completed in {format_duration(monitoring_results.get('total_duration', 0))}"
            )


def create_benchmark_reporter(
    output_dir: str = "experiment_results",
) -> BenchmarkReporter:
    """Factory function to create a configured benchmark reporter."""
    return BenchmarkReporter(output_dir=output_dir)
