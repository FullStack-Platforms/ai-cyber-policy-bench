# Cyber Policy Benchmark

[![CI Pipeline](https://github.com/your-org/cyber-policy-bench/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/cyber-policy-bench/actions/workflows/ci.yml)
[![Benchmark Tests](https://github.com/your-org/cyber-policy-bench/actions/workflows/benchmark-test.yml/badge.svg)](https://github.com/your-org/cyber-policy-bench/actions/workflows/benchmark-test.yml)

A comprehensive benchmarking suite for evaluating AI models on cybersecurity policy and compliance questions. This tool evaluates model performance across different contexts including no context, raw framework documents, and vector database retrieval.

## 🚀 Features

### Core Functionality
- **Multi-Context Evaluation**: Tests models with no context, raw framework files, and vector database retrieval
- **Dual Judge Scoring**: Advanced scoring system with two independent LLM judges for reliability
- **Comprehensive Framework Support**: Covers SOC 2, PCI DSS, HIPAA, GDPR, NIST, CMMC, and more
- **Vector Database Integration**: Smart context retrieval using ChromaDB with multi-collection framework support

### Advanced Capabilities
- **Graceful Failure Handling**: Robust error handling with fallback mechanisms
- **Performance Monitoring**: Detailed metrics tracking and performance analysis
- **HTML Reporting**: Beautiful, comprehensive reports with visualizations
- **CI/CD Integration**: Automated testing and validation pipelines
- **Model Management**: Intelligent model discovery and capability detection

## 📋 Table of Contents

1. [Quick Start](#-quick-start)
2. [Installation](#-installation)
3. [Configuration](#-configuration)
4. [Usage](#-usage)
5. [Architecture](#-architecture)
6. [Development](#-development)
7. [CI/CD](#-cicd)
8. [Contributing](#-contributing)

## 🚀 Quick Start

### Prerequisites
- Python 3.10-3.12
- uv
- API keys for OpenRouter and/or OpenAI
- Git

### Basic Setup
```bash
# Clone the repository
git clone https://github.com/your-org/cyber-policy-bench.git
cd cyber-policy-bench

# Create a locked virtual environment
uv sync

# Configure the benchmark
cp config.example.cfg config.cfg
# Edit config.cfg with your API keys

# Run a quick test
uv run python cyber_policy_bench.py --models 2 --questions 3 --setup-db
```

## 📦 Installation

### Standard Installation
```bash
uv sync
```

### Development Installation
```bash
# Install runtime and development dependencies from uv.lock
uv sync --dev

# Install pre-commit hooks (optional)
uv run pre-commit install
```

### Dependencies
- **Core**: `openai`, `chromadb`, `requests`, `pathlib`
- **Document Processing**: `docling` (for PDF/document processing)
- **Development**: `black`

## ⚙️ Configuration

The benchmark uses a comprehensive configuration system with support for multiple API providers and advanced settings.

### Basic Configuration (`config.cfg`)

```ini
[OpenRouter]
api_key = your-openrouter-key

[OpenAI]  
api_key = your-openai-key
# openai_compatible_url = http://localhost:8080/v1/  # For local models

[Scoring]
# Dual Judge Configuration
judge_mode = dual  # single/dual
judge_model_1 = anthropic/claude-sonnet-4
judge_model_2 = openai/gpt-4o
judge_weight_1 = 0.5
judge_weight_2 = 0.5
score_threshold_alert = 0.3

[Evaluation]
max_retries = 3
retry_delay = 2
timeout_seconds = 30
parallel_requests = 5

[Vector Database]
db_path = ./vector_db

[Cyber Policy Benchmark]
output_dir = ./experiment_results
cache_dir = ./experiment_cache
```

### Environment Variables
```bash
# Override config values with environment variables
export OPENROUTER_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export BENCHMARK_OUTPUT_DIR="./results"
```

## 🎯 Usage

### Basic Evaluation
```bash
# Run with default settings (2 models, 3 questions)
uv run python cyber_policy_bench.py --setup-db

# Custom evaluation
uv run python cyber_policy_bench.py --models 5 --questions 10 --setup-db

# Use existing vector database
uv run python cyber_policy_bench.py --models 3 --questions 5
```

### Command Line Options
- `--models N`: Number of models to evaluate (default: 2)
- `--questions N`: Number of questions to test (default: 3)
- `--setup-db`: Setup/rebuild vector database from framework chunks

### Programmatic Usage
```python
import asyncio
from src.evaluator import CyberPolicyEvaluator, EvaluationMode
from src.scorer import TwoJudgeScorer
from src.reporter import create_benchmark_reporter

async def run_custom_evaluation():
    # Initialize components
    evaluator = CyberPolicyEvaluator()
    scorer = TwoJudgeScorer()
    reporter = create_benchmark_reporter()
    
    # Load questions
    questions = evaluator.load_evaluation_questions()[:5]
    models = ["gpt-4.1", "anthropic/claude-sonnet-4"]
    modes = [EvaluationMode.NO_CONTEXT, EvaluationMode.VECTOR_DB]
    
    # Run evaluation
    results = await evaluator.run_evaluation(models, questions, modes)
    scored_results = await scorer.score_evaluation_results(results)
    
    # Generate reports
    reports = reporter.generate_all_reports(scored_results)
    print(f"Reports generated: {reports}")

# Run the evaluation
asyncio.run(run_custom_evaluation())
```

## 🏗️ Architecture

### Core Components

```
src/
├── base.py          # Base classes and mixins
├── utils.py         # Common utilities and helpers
├── models.py        # Model management and discovery
├── evaluator.py     # Core evaluation engine
├── scorer.py        # Scoring system with dual judges
├── reporter.py      # Comprehensive reporting system
├── vectorize.py     # Document processing and vectorization
└── db.py           # Vector database operations
```

### Key Features

#### Dual Judge Scoring System
The benchmark uses an advanced dual judge system for reliable scoring:
- **Parallel Evaluation**: Both judges evaluate simultaneously
- **Graceful Fallback**: If one judge fails, uses the other
- **Discrepancy Detection**: Alerts when judges disagree significantly
- **Weighted Averaging**: Configurable weights for different judges

#### Smart Context Retrieval
- **Framework Detection**: Automatically detects relevant frameworks in questions
- **Multi-Collection Search**: Searches specific framework collections when detected
- **Fallback Search**: Falls back to global search if no frameworks detected
- **Context Truncation**: Prevents context window overflow

#### Robust Error Handling
- **Retry Logic**: Exponential backoff for API failures
- **Input Validation**: Comprehensive input validation and sanitization
- **Graceful Degradation**: System continues working even with partial failures
- **Detailed Logging**: Comprehensive logging for debugging

## 🧪 Development

### Code Quality
```bash
# Linting
uv run ruff check src/

# Formatting
uv run black src/

# Type checking
uv run mypy src/ --ignore-missing-imports
```

### Project Structure
```
cyber-policy-bench/
├── src/                    # Source code
├── data/                   # Framework documents and evaluation data
├── .github/workflows/      # CI/CD pipelines
├── experiment_results/     # Benchmark results
├── reports/               # Generated reports
├── vector_db/             # Vector database storage
└── config.cfg            # Configuration file
```

## 🚀 CI/CD

### GitHub Actions Workflows

#### CI Pipeline (`.github/workflows/ci.yml`)
- **Multi-Python Testing**: Tests on Python 3.9, 3.10, 3.11
- **Code Quality**: Linting, formatting, and type checking
- **Security Scanning**: Automated security analysis with bandit
- **Coverage Reporting**: Codecov integration

#### Benchmark Testing (`.github/workflows/benchmark-test.yml`)
- **Mini Benchmarks**: Quick validation with 2 models, 3 questions
- **Scoring Validation**: Ensures all results receive scores
- **Mode Coverage**: Validates all evaluation modes work
- **Reproducibility**: Tests consistency between runs

#### Scheduled Benchmarks (`.github/workflows/scheduled-benchmark.yml`)
- **Weekly Full Runs**: Comprehensive benchmarks every Sunday
- **Performance Tracking**: Long-term performance monitoring
- **Regression Detection**: Automatic alerts for performance drops
- **Visualization**: Generates charts and analysis

### Configuration for CI

Set these secrets in your GitHub repository:
```bash
OPENROUTER_API_KEY=your-openrouter-key
OPENAI_API_KEY=your-openai-key  
```

## 📊 Reports and Monitoring

### HTML Reports
The benchmark generates comprehensive HTML reports with:
- **Overall Performance Metrics**: Success rates, score distributions
- **Model Comparisons**: Side-by-side performance analysis
- **Evaluation Mode Analysis**: Performance by context type
- **Detailed Statistics**: Standard deviations, confidence intervals
- **Visual Progress Bars**: Interactive performance visualizations

### JSON Exports
Machine-readable exports for:
- **Integration**: Easy integration with other tools
- **Analysis**: Custom analysis and visualization
- **Archival**: Long-term performance tracking

### Judge Performance Tracking
Monitor dual judge system performance:
- **Success Rates**: Individual judge reliability
- **Fallback Usage**: How often fallbacks are needed
- **Discrepancy Detection**: Judge agreement analysis

## 🤝 Contributing

### Development Workflow
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature-name`
3. **Implement** your changes with tests
4. **Run** the test suite: `pytest`
5. **Check** code quality: `ruff check src/` and `black src/`
6. **Submit** a pull request

### Code Standards
- **PEP 8** compliance (enforced by black)
- **Type hints** for public APIs
- **Comprehensive tests** for new features
- **Documentation** for public functions
- **Error handling** with appropriate exceptions

### Adding New Features

#### New Evaluation Modes
1. Add mode to `EvaluationMode` enum in `evaluator.py`
2. Implement context retrieval logic
3. Update `evaluate_single_question` method
4. Add tests in `tests/test_evaluator.py`

#### New Scoring Methods
1. Add method to `ScoringMethod` enum in `scorer.py`
2. Implement scoring logic in `AccuracyScorer` or `TwoJudgeScorer`
3. Update `score_response` method
4. Add tests in `tests/test_scorer.py`

#### New Frameworks
1. Add framework documents to `data/cyber-frameworks/`
2. Create `metadata.toml` file
3. Update framework detection in `evaluator.py`
4. Add test questions to `data/prompts/cyber_evals.jsonl`

## 📚 API Reference

### Core Classes

#### `CyberPolicyEvaluator`
Main evaluation engine with support for multiple context modes.

```python
evaluator = CyberPolicyEvaluator(vector_db=db)
results = await evaluator.run_evaluation(models, questions, modes)
```

#### `TwoJudgeScorer`
Advanced scoring system with dual judge support.

```python
scorer = TwoJudgeScorer(
    judge_model_1="anthropic/claude-sonnet-4",
    judge_model_2="gpt-4.1"
)
scored_results = await scorer.score_evaluation_results(results)
```

#### `BenchmarkReporter`
Comprehensive reporting and visualization system.

```python
reporter = create_benchmark_reporter()
report_paths = reporter.generate_all_reports(results)
```

### Configuration

#### Dual Judge Settings
```ini
[Scoring]
judge_mode = dual
judge_model_1 = anthropic/claude-sonnet-4  
judge_model_2 = openai/gpt-4o
judge_weight_1 = 0.6  # Primary judge weight
judge_weight_2 = 0.4  # Secondary judge weight
```

#### Performance Tuning
```ini  
[Evaluation]
max_retries = 3           # API retry attempts
retry_delay = 2           # Base delay between retries
timeout_seconds = 30      # Request timeout
parallel_requests = 5     # Concurrent requests
```

## 🔧 Troubleshooting

### Common Issues

#### "No API keys found"
- Ensure `config.cfg` exists and has valid API keys
- Check environment variables: `OPENROUTER_API_KEY` or `OPENAI_API_KEY`
- Verify key format and permissions

#### "No scores generated"
- Check judge model availability and API limits  
- Verify context window limits aren't exceeded
- Review dual judge fallback statistics
- Enable debug logging for detailed error information

#### "Vector database not found"
- Run with `--setup-db` flag to initialize database
- Check `db_path` in configuration
- Ensure framework documents exist in `data/cyber-frameworks/`

#### Performance Issues
- Reduce `parallel_requests` in configuration
- Increase `timeout_seconds` for slow models
- Use model filtering to test fewer models
- Check API rate limits

### Debug Mode
Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Or set environment variable:
```bash
export PYTHONPATH=. LOGLEVEL=DEBUG python cyber_policy_bench.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenRouter](https://openrouter.ai/) for model access
- [ChromaDB](https://www.trychroma.com/) for vector database functionality
- [Docling](https://github.com/DS4SD/docling) for document processing
- The cybersecurity community for framework documentation
- [EQ-Bench](https://github.com/EQ-bench/EQ-Bench) for the initial inspiration, 

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/cyber-policy-bench/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/cyber-policy-bench/discussions)
- **Documentation**: [Wiki](https://github.com/your-org/cyber-policy-bench/wiki)

---

**Built with ❤️ for the cybersecurity community**
