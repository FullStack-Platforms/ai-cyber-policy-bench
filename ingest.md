(Files content cropped to 300k characters, download full ingest to see more)
================================================
FILE: README.md
================================================
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
- Python 3.9+
- API keys for OpenRouter and/or OpenAI
- Git

### Basic Setup
```bash
# Clone the repository
git clone https://github.com/your-org/cyber-policy-bench.git
cd cyber-policy-bench

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure the benchmark
cp config.example.cfg config.cfg
# Edit config.cfg with your API keys

# Run a quick test
python cyber_policy_bench.py --models 2 --questions 3 --setup-db
```

## 📦 Installation

### Standard Installation
```bash
pip install -r requirements.txt
```

### Development Installation
```bash
# Install with development dependencies
pip install -r requirements.txt
pip install black

# Install pre-commit hooks (optional)
pre-commit install
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
python cyber_policy_bench.py --setup-db

# Custom evaluation
python cyber_policy_bench.py --models 5 --questions 10 --setup-db

# Use existing vector database
python cyber_policy_bench.py --models 3 --questions 5
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
ruff check src/

# Formatting
black src/

# Type checking
mypy src/ --ignore-missing-imports
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


================================================
FILE: company_definition.md
================================================
# Cybersecurity Compliance Company Overview Generation Prompt

## Objective
Generate 30 distinct, semi-realistic company overviews in Markdown format. Each overview must provide essential context for determining cybersecurity compliance requirements while maintaining industry authenticity and regulatory logic.

## Template Structure

```markdown
### [Company Name]

**Organization Overview:**
* **Business Details:** [2-3 sentences describing core business activities, primary services/products, and target market segment]
* **Industry:** [Primary industry classification with sub-sector if relevant]
* **Size:** [Employee count range AND annual revenue bracket (e.g., "250-500 employees, $50-100M revenue")]
* **Structure:** [Legal structure, ownership type, and operational scope (local/national/international)]
* **Technology Infrastructure:** [Primary infrastructure model, cloud providers, critical systems, and data processing scale]

**Compliance Requirements:**
* **Applicable Frameworks/Regulations:** [Select 2-4 frameworks that logically align with the organization's profile]
    * NIST Cybersecurity Framework (CSF) 2.0
    * NIST 800-171 Rev. 3
    * CMMC Level 1/2
    * ISO 27001
    * CIS Controls
    * HIPAA
    * PCI DSS
    * GDPR
    * NJ SISM
    * SOC2
    * CJIS

**Policy Parameters:** [Include only when specific constraints significantly impact compliance approach]
* **Critical Constraints:** [Unique compliance challenges, regulatory obligations, or risk factors]
* **Key Stakeholders:** [Relevant roles/departments for compliance implementation]
* **Sensitive Systems/Data:** [Specific data types or systems requiring enhanced protection]
```

## Generation Requirements

### Industry Distribution Guidelines
Ensure representation across these sectors (aim for 3-4 companies per major category):
- **Healthcare:** Hospitals, clinics, health tech, medical devices
- **Financial Services:** Banks, credit unions, fintech, investment firms
- **Government/Defense:** Federal contractors, state agencies, defense suppliers
- **Technology:** SaaS providers, software development, cloud services
- **Manufacturing:** Industrial, automotive, pharmaceuticals, energy
- **Retail/E-commerce:** Online retailers, payment processors, logistics
- **Education:** Universities, K-12 districts, online learning platforms
- **Critical Infrastructure:** Utilities, telecommunications, transportation

### Size Stratification
- **Small (10-100 employees):** 8 companies
- **Medium (100-1,000 employees):** 12 companies  
- **Large (1,000+ employees):** 10 companies

### Compliance Framework Logic Matrix
**Mandatory Alignments:**
- Healthcare organizations → HIPAA required
- Payment processing → PCI DSS required
- Government contractors → NIST 800-171/CMMC required
- Financial institutions → SOC2 + regulatory frameworks
- International operations → GDPR consideration
- Critical infrastructure → NIST CSF recommended

### Quality Standards

**Organization Overview Requirements:**
- Business descriptions must be specific enough to infer data types and risk profiles
- Technology infrastructure should reflect realistic modern deployments
- Size and structure should align with industry norms
- Geographic scope should influence regulatory selection

**Compliance Requirements Logic:**
- Never select all available frameworks for one company
- Ensure framework selection reflects actual regulatory obligations
- Vary combinations to demonstrate different compliance scenarios
- Include foundational frameworks (NIST CSF, CIS) with sector-specific regulations

**Policy Parameters Usage:**
- Include only when adding meaningful compliance context
- Focus on constraints that affect security control implementation
- Avoid generic statements that apply to all organizations
- Maximum 40% of companies should include this section

### Content Quality Guidelines
- Use industry-appropriate terminology and business models
- Avoid marketing language or promotional content
- Ensure semi-realistic company profiles (could plausibly exist)
- Maintain consistent formatting and structure
- Focus on compliance-relevant details only

### Deliverable Format
- Present all 30 companies in a single response
- Use proper Markdown formatting
- Number companies sequentially (1-30)
- Ensure each company occupies appropriate space (no overly long descriptions)

## Success Criteria
- 30 unique, realistic company profiles
- Logical alignment between business type and compliance requirements  
- Appropriate industry and size distribution
- Varied compliance framework combinations
- Consistent formatting and structure
- Actionable information for compliance assessment


================================================
FILE: config.example.cfg
================================================
# Configuration file for AI Cyber Policy Benchmark
# Copy this file and rename to config.cfg with your actual values

# =============================================================================
# API CREDENTIALS
# Configure access to model providers
# =============================================================================

[OpenAI]
# OpenAI API credentials
api_key = 
# Optional: Alternative OpenAI-compatible endpoint (e.g., local inference servers)
openai_compatible_url = 

[OpenRouter]
# OpenRouter API for accessing multiple models
api_key = 

[Anthropic]
# Anthropic API credentials
api_key = 

[Huggingface]
# Hugging Face Hub access
access_token = 
cache_dir = 

# =============================================================================
# MODEL CONFIGURATION
# Define which models to use for evaluation and scoring
# =============================================================================

[Models]
# Evaluation models (comma-separated list)
eval_models = gpt-5-chat,mistralai/mistral-nemo,qwen/qwen3-30b-a3b,qwen/qwen3-coder,z-ai/glm-4.5,gpt-5-mini,moonshotai/kimi-k2,google/gemini-2.5-flash,deepseek/deepseek-v3,google/gemini-2.5-pro,anthropic/claude-sonnet-4,x-ai/grok-4,anthropic/claude-3.7-sonnet,anthropic/claude-opus-4.1

# Judge models for scoring (comma-separated list)
judge_models = moonshotai/kimi-k2,gpt-5-chat,anthropic/claude-sonnet-4,qwen/qwen3-coder

# Model discovery settings
use_dynamic_models = false
model_cache_hours = 24
max_eval_models = 20
max_judge_models = 4

# =============================================================================
# SCORING CONFIGURATION
# Configure how responses are scored and judged
# =============================================================================

[Scoring]
# Scoring method: single, dual, or ensemble
scoring_method = dual

# Primary judge model
primary_judge = moonshotai/kimi-k2
primary_judge_weight = 0.5

# Secondary judge model (for dual/ensemble scoring)
secondary_judge = gpt-5-chat
secondary_judge_weight = 0.5

# Scoring thresholds and alerts
score_threshold_alert = 0.3
min_consensus_threshold = 0.7
max_score_deviation = 0.3

# Scoring parameters
max_scoring_retries = 3
scoring_timeout = 45
include_reasoning = true

# =============================================================================
# EVALUATION PIPELINE
# Control evaluation execution and behavior
# =============================================================================

[Evaluation]
# Request handling
max_retries = 3
retry_delay = 2.0
timeout_seconds = 30
parallel_requests = 5

# Response parameters
max_response_tokens = 1000
temperature = 0.7
top_p = 1.0

# Context and retrieval
vector_context_results = 5
max_context_length = 8000
include_source_attribution = true

# Evaluation modes (set to false to disable specific modes)
enable_no_context = true
enable_raw_files = true
enable_vector_db = true

# =============================================================================
# VECTOR DATABASE
# Document storage and retrieval configuration
# =============================================================================

[VectorDatabase]
# Storage location
db_path = ./vector_db

# Embedding configuration
embedding_model = all-MiniLM-L6-v2
embedding_dimensions = 384
batch_size = 100

# Search and retrieval
vector_space = cosine
default_search_results = 5
similarity_threshold = 0.7

# Performance settings
chunk_size = 512
chunk_overlap = 50
max_chunks_per_document = 1000

# =============================================================================
# SYSTEM PATHS AND STORAGE
# Configure where data is stored and processed
# =============================================================================

[Paths]
# Core directories
output_dir = ./experiment_results
cache_dir = ./experiment_cache
data_dir = ./data
frameworks_dir = ./data/cyber-frameworks

# Specific files
prompts_file = ./data/prompts/cyber_evals.jsonl
chunks_dir = ./output/chunks
logs_dir = ./logs

# =============================================================================
# REPORTING AND EXPORT
# Configure output formats and destinations
# =============================================================================

[Reporting]
# Report formats (comma-separated: json, csv, html, markdown)
output_formats = json,csv,html

# Report details
include_detailed_results = true
include_model_metadata = true
include_timing_info = true
include_error_analysis = true

# External integrations
google_spreadsheet_url = 
slack_webhook_url = 

# =============================================================================
# SYSTEM OPTIONS
# General system behavior and feature flags
# =============================================================================

[Options]
# Security and trust
trust_remote_code = true
validate_configs = true
strict_mode = false

# Logging and debugging
log_level = INFO
enable_debug_mode = false
log_api_requests = false
log_responses = false

# Performance
enable_caching = true
cache_responses = true
parallel_processing = true

# =============================================================================
# CI/CD AND TESTING
# Automated testing and integration settings
# =============================================================================

[Testing]
# Test execution
run_integration_tests = true
benchmark_on_pr = false
minimum_coverage = 80

# Test parameters
test_model_limit = 2
test_question_limit = 3
test_timeout = 120

# Quality gates
min_accuracy_threshold = 0.6
max_error_rate = 0.1
performance_regression_threshold = 0.05


================================================
FILE: cyber_policy_bench.py
================================================
#!/usr/bin/env python3
"""
Cyber Policy Benchmark

Complete evaluation pipeline for cybersecurity policy frameworks:
1. Setup → Load and vectorize cybersecurity documents
2. Evaluate → Run evaluation across multiple models and modes
3. Score → Score results using configured judge models
4. Report → Generate comprehensive reports

Usage:
    python cyber_policy_bench.py --models 2 --questions 3 --setup-db
"""

import os
import asyncio
import argparse
import sys
from pathlib import Path
from typing import Dict

# Fix tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Import core components
from src.utils import (
    get_config_value,
    setup_logging,
    Timer,
    ValidationError,
    validate_config,
    get_enabled_evaluation_modes,
)
from src.vectorize import FrameworkProcessor
from src.db import VectorDatabase
from src.evaluator import CyberPolicyEvaluator, EvaluationMode
from src.scorer import AccuracyScorer, TwoJudgeScorer, ScoringMethod
from src.models import get_model_manager
from src.reporter import create_benchmark_reporter


def validate_setup() -> bool:
    """Validate that required files and configurations exist."""
    logger = setup_logging()

    # Check required files
    required_files = [
        get_config_value("Paths", "prompts_file", "./data/prompts/cyber_evals.jsonl"),
        get_config_value("Paths", "frameworks_dir", "./data/cyber-frameworks"),
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)

    if missing_files:
        logger.error(f"Missing required files/directories: {missing_files}")
        return False

    # Validate configuration
    validation = validate_config()

    if not validation["valid"]:
        logger.error("Configuration validation failed:")
        for issue in validation["issues"]:
            logger.error(f"  - {issue}")
        return False

    if validation["warnings"]:
        logger.warning("Configuration warnings:")
        for warning in validation["warnings"]:
            logger.warning(f"  - {warning}")

    return True


def setup_vector_database() -> VectorDatabase:
    """Set up vector database from existing chunks or create new ones."""
    logger = setup_logging()

    chunks_dir = Path(get_config_value("Paths", "chunks_dir", "./output/chunks"))

    if not chunks_dir.exists() or not list(chunks_dir.glob("*_chunks.json")):
        logger.info("No existing chunks found. Processing frameworks...")

        with Timer("Framework processing"):
            framework_processor = FrameworkProcessor()
            all_chunks = framework_processor.process_all_frameworks()
            framework_processor.save_chunks(all_chunks)

    logger.info("Initializing vector database...")

    with Timer("Vector database initialization"):
        vector_db = VectorDatabase.initialize_from_chunks()

    stats = vector_db.get_collection_stats()
    logger.info(
        f"Vector database ready: {stats['total_chunks']} chunks from {len(stats['frameworks'])} frameworks"
    )

    return vector_db


async def run_evaluation(
    vector_db: VectorDatabase, num_models: int = 2, num_questions: int = 3
) -> Dict:
    """Run the complete evaluation pipeline."""
    logger = setup_logging()
    logger.info(
        f"Starting evaluation pipeline: {num_models} models, {num_questions} questions"
    )

    with Timer("Model evaluation"):
        # Initialize evaluator
        evaluator = CyberPolicyEvaluator(vector_db=vector_db)

        # Get models from model manager
        model_manager = get_model_manager()
        await model_manager.refresh_models()

        eval_models = model_manager.get_model_ids(
            limit=get_config_value("Models", "max_eval_models", num_models, int)
        )
        models = eval_models[:num_models]

        # Load evaluation questions
        questions = evaluator.load_evaluation_questions()[:num_questions]

        # Get enabled evaluation modes from configuration
        modes = get_enabled_evaluation_modes()

        logger.info(f"Testing models: {models}")
        logger.info(f"Evaluation modes: {[m.value for m in modes]}")

        # Run evaluation
        evaluation_results = await evaluator.run_evaluation(models, questions, modes)

    return evaluation_results


async def score_evaluation_results(evaluation_results: Dict) -> Dict:
    """Score the evaluation results using configured judge system."""
    logger = setup_logging()
    logger.info("Starting scoring with configured judge system")

    with Timer("Result scoring"):
        scoring_method = get_config_value("Scoring", "scoring_method", "dual")

        if scoring_method == "dual":
            scorer = TwoJudgeScorer()
        else:
            scorer = AccuracyScorer()

        scoring_methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]
        scored_results = await scorer.score_evaluation_results(
            evaluation_results, scoring_methods
        )

        # Print judge statistics if available
        if hasattr(scorer, "get_judge_statistics"):
            judge_stats = scorer.get_judge_statistics()
            logger.info(f"Judge performance statistics:")
            logger.info(f"  Total attempts: {judge_stats['total_scoring_attempts']}")
            if "dual_success_rate" in judge_stats:
                logger.info(f"  Success rate: {judge_stats['dual_success_rate']:.2%}")

    return scored_results


def generate_summary_report(scored_results: Dict) -> Dict:
    """Generate summary statistics and report."""
    logger = setup_logging()
    logger.info("Generating summary report")

    from src.utils import get_timestamp

    summary = {
        "total_models": len(scored_results),
        "models": {},
        "mode_performance": {},
        "overall_stats": {},
        "metadata": {
            "timestamp": get_timestamp(),
            "configuration": {
                "scoring_method": get_config_value("Scoring", "scoring_method", "dual"),
                "vector_db_path": get_config_value(
                    "VectorDatabase", "db_path", "./vector_db"
                ),
            },
        },
    }

    all_scores = []
    mode_scores = {mode.value: [] for mode in EvaluationMode}

    for model_name, results in scored_results.items():
        model_scores = []
        model_by_mode = {mode.value: [] for mode in EvaluationMode}

        for result in results:
            score = result.get("accuracy_score", 0.0)
            model_scores.append(score)
            all_scores.append(score)

            mode = result.get("evaluation_mode", "unknown")
            if mode in model_by_mode:
                model_by_mode[mode].append(score)
                mode_scores[mode].append(score)

        summary["models"][model_name] = {
            "total_evaluations": len(results),
            "average_score": (
                sum(model_scores) / len(model_scores) if model_scores else 0.0
            ),
            "score_by_mode": {
                mode: sum(scores) / len(scores) if scores else 0.0
                for mode, scores in model_by_mode.items()
            },
        }

    # Overall statistics
    summary["overall_stats"] = {
        "average_score": sum(all_scores) / len(all_scores) if all_scores else 0.0,
        "total_evaluations": len(all_scores),
    }

    # Mode performance
    summary["mode_performance"] = {
        mode: sum(scores) / len(scores) if scores else 0.0
        for mode, scores in mode_scores.items()
    }

    return summary


def save_results(scored_results: Dict, summary: Dict) -> Path:
    """Save all results to files."""
    output_dir = Path(get_config_value("Paths", "output_dir", "./experiment_results"))
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save detailed results
    from src.utils import save_json

    save_json(scored_results, output_dir / "detailed_results.json")
    save_json(summary, output_dir / "summary.json")

    logger = setup_logging()
    logger.info(f"Results saved to {output_dir}/")

    return output_dir


def print_summary_report(summary: Dict) -> None:
    """Print formatted summary report."""
    print(f"\n{'='*60}")
    print(f"CYBER POLICY BENCHMARK RESULTS")
    print(f"{'='*60}")

    print(f"\nOverall Performance:")
    print(f"  Total Evaluations: {summary['overall_stats']['total_evaluations']}")
    print(f"  Average Score: {summary['overall_stats']['average_score']:.3f}")

    print(f"\nPerformance by Mode:")
    for mode, score in summary["mode_performance"].items():
        print(f"  {mode.replace('_', ' ').title()}: {score:.3f}")

    print(f"\nPerformance by Model:")
    for model_name, stats in summary["models"].items():
        print(f"  {model_name}:")
        print(f"    Average: {stats['average_score']:.3f}")
        for mode, score in stats["score_by_mode"].items():
            if score > 0:  # Only show modes that were tested
                print(f"    {mode.replace('_', ' ').title()}: {score:.3f}")


async def main() -> None:
    """Main execution pipeline: Setup → Evaluate → Score → Report."""
    parser = argparse.ArgumentParser(
        description="Cyber Policy Benchmark - Complete Evaluation Pipeline"
    )
    parser.add_argument(
        "--models",
        type=int,
        default=2,
        help="Number of models to evaluate (default: 2)",
    )
    parser.add_argument(
        "--questions",
        type=int,
        default=3,
        help="Number of questions to test (default: 3)",
    )
    parser.add_argument(
        "--setup-db",
        action="store_true",
        help="Set up vector database from framework chunks",
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip configuration and setup validation",
    )

    args = parser.parse_args()
    logger = setup_logging()

    try:
        with Timer("Complete benchmark pipeline"):
            print("=== Cyber Policy Benchmark - Complete Pipeline ===")

            # STEP 1: SETUP
            if not args.skip_validation and not validate_setup():
                logger.error(
                    "Setup validation failed. Use --skip-validation to bypass."
                )
                sys.exit(1)

            # Set up vector database
            if args.setup_db:
                vector_db = setup_vector_database()
            elif Path(
                get_config_value("VectorDatabase", "db_path", "./vector_db")
            ).exists():
                logger.info("Using existing vector database...")
                vector_db = VectorDatabase()
                stats = vector_db.get_collection_stats()
                logger.info(f"Loaded vector database: {stats['total_chunks']} chunks")
            else:
                logger.error("No vector database found. Use --setup-db to create one.")
                sys.exit(1)

            # STEP 2: EVALUATE
            evaluation_results = await run_evaluation(
                vector_db, args.models, args.questions
            )

            # STEP 3: SCORE
            scored_results = await score_evaluation_results(evaluation_results)

            # STEP 4: REPORT
            summary = generate_summary_report(scored_results)
            output_dir = save_results(scored_results, summary)
            print_summary_report(summary)

            # Generate comprehensive reports using BenchmarkReporter
            logger.info("Generating comprehensive reports...")
            reporter = create_benchmark_reporter(output_dir=str(output_dir))
            report_paths = reporter.generate_all_reports(scored_results, summary)

            print(f"\nReports generated:")
            for report_type, path in report_paths.items():
                print(f"  {report_type}: {path}")

            print(f"\n=== BENCHMARK COMPLETE ===")

    except KeyboardInterrupt:
        logger.info("Benchmark interrupted by user")
        sys.exit(1)
    except ValidationError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Benchmark failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())



================================================
FILE: evals-methodoly.md
================================================
# AI Cyber Policy Benchmark Evaluation Methodology

## Overview

This document outlines the comprehensive methodology for evaluating Large Language Models (LLMs) on their knowledge and application of cybersecurity frameworks and policies. The benchmark system assesses models across multiple dimensions to understand their capability in providing accurate, practical cybersecurity guidance.

## Evaluation Framework

### Evaluation Types

**Accuracy Evaluations**
- Verify correctness of model outputs against established ground truth
- Test factual knowledge of cybersecurity frameworks, regulations, and standards
- Measure precision in citing specific controls, requirements, and procedures
- Validate technical accuracy of security recommendations

**Technical Writing Evaluations**
- Ensure accurate citation and interpretation of source materials
- Verify translation of complex regulatory language into practical actions and behaviors
- Assess clarity and actionability of security guidance
- Evaluate coherence between cited sources and provided recommendations

### Context Provision Modes

The benchmark evaluates models under three distinct context scenarios:

**1. No Additional Context (Baseline)**
- Models rely solely on their pre-trained knowledge
- Tests fundamental understanding of cybersecurity concepts
- Establishes baseline performance without external information
- Reveals gaps in training data coverage

**2. Raw Relevant Files**
- Models receive complete markdown files containing relevant framework documentation
- Tests ability to process and synthesize large amounts of structured information
- Evaluates information retrieval and contextual understanding capabilities
- Simulates scenarios with access to complete documentation

**3. Vector Database Context**
- Models receive semantically relevant chunks retrieved via vector search
- Tests performance with targeted, contextually relevant information
- Evaluates effectiveness of retrieval-augmented generation (RAG) approaches
- Reflects real-world deployment scenarios with knowledge bases

## Framework Coverage

The benchmark encompasses 11 major cybersecurity frameworks and regulations:

### Primary Frameworks
- **NIST Cybersecurity Framework**: Core cybersecurity practices and risk management
- **GDPR (General Data Protection Regulation)**: European data protection and privacy
- **HIPAA (Health Insurance Portability and Accountability Act)**: Healthcare data security
- **SOX (Sarbanes-Oxley Act)**: Financial reporting and corporate governance
- **PCI DSS (Payment Card Industry Data Security Standard)**: Payment card data protection

### Additional Standards
- **ISO 27001**: Information security management systems
- **NIST 800-53**: Security and privacy controls for federal information systems
- **COBIT**: IT governance and management framework
- **SOC 2**: Service organization control reporting
- **FedRAMP**: Federal risk and authorization management program
- **FISMA**: Federal information security modernization act

## Question Design and Categorization

### Question Types

**Simple Factual Questions**
- Direct knowledge queries about specific controls or requirements
- Single-framework focus with clear, verifiable answers
- Test basic comprehension and recall capabilities
- Example: "What are the five core functions of the NIST Cybersecurity Framework?"

**Complex Reasoning Questions**
- Multi-step analysis requiring synthesis of multiple concepts
- Cross-framework integration and comparison
- Practical application scenarios requiring judgment
- Example: "How would an organization implement both GDPR Article 32 and NIST CSF PR.DS requirements for data encryption?"

### Multi-Framework Integration

**Cross-Framework Questions**
- Test understanding of overlaps and relationships between different standards
- Evaluate ability to reconcile potentially conflicting requirements
- Assess practical implementation across multiple compliance contexts
- Measure sophistication in regulatory interpretation

**Framework-Specific Depth**
- Deep dives into specific framework nuances
- Test detailed knowledge of implementation guidance
- Evaluate understanding of framework-specific terminology and concepts

## Scoring Methodology

### Primary Scoring Criteria

**Accuracy (50% weight)**
- Factual correctness of information provided
- Proper citation of relevant controls and requirements
- Technical accuracy of security recommendations
- Alignment with established best practices

**Structural Adherence (30% weight)**
- Following requested output format and structure
- Proper organization of information (lists, sections, etc.)
- Consistent formatting and presentation
- Meeting specific formatting requirements when specified

**Conciseness (20% weight)**
- Efficient communication without unnecessary verbosity
- Direct response to the specific question asked
- Elimination of redundant or irrelevant information
- Clear, focused delivery of key points

### Dual-Judge Evaluation System

**Primary AI Judge**
- Conducts initial comprehensive evaluation
- Applies scoring rubric across all criteria
- Provides detailed feedback and justification
- Generates preliminary scores and recommendations

**Secondary AI Judge (Validation)**
- Independent evaluation of the same response
- Cross-validates primary judge assessments
- Identifies potential scoring discrepancies
- Provides additional perspective on edge cases

**Consensus and Fallback**
- Automatic flagging of significant judge disagreements (>20% score difference)
- Manual review process for disputed evaluations
- Fallback to human evaluation for complex cases
- Continuous improvement of judge calibration

### Control Reference Validation

**Automated Control Extraction**
- Systematic identification of cited controls and standards
- Verification of control numbers, titles, and descriptions
- Cross-reference validation against authoritative sources
- Detection of misattributed or fictional controls

**Reference Accuracy Scoring**
- Precise control citation (full points)
- Correct concept, minor citation errors (partial points)
- Conceptually relevant but incorrect reference (minimal points)
- Inaccurate or fabricated citations (zero points)

## Performance Metrics and Analysis

### Technical Performance Metrics

**Latency Analysis**
- Response time measurement across different context modes
- Comparison of processing time for simple vs. complex questions
- Framework-specific performance timing
- Context size impact on response latency

**Framework-Specific Performance**
- Average accuracy scores by individual framework
- Identification of framework knowledge gaps
- Cross-framework performance correlation analysis
- Evolution of performance across framework updates

**Question Complexity Analysis**
- Simple question accuracy rates
- Complex reasoning question performance
- Multi-framework integration success rates
- Practical application scenario effectiveness

### Reliability and Consistency Metrics

**Judge Agreement Statistics**
- Inter-judge reliability coefficients
- Common areas of judge disagreement
- Score variance analysis across question types
- Judge calibration and improvement tracking

**Response Consistency**
- Test-retest reliability for repeated evaluations
- Consistency across different model instances
- Stability of performance over time
- Impact of context variation on response consistency

## Quality Assurance Framework

### Evaluation Integrity

**Ground Truth Validation**
- Regular updates to reflect framework changes
- Expert review of evaluation criteria
- Continuous refinement of scoring rubrics
- Integration of industry feedback and standards evolution

**Bias Detection and Mitigation**
- Analysis of performance variations across different frameworks
- Detection of systematic scoring biases
- Evaluation of cultural and regional compliance variations
- Mitigation strategies for identified biases

### Continuous Improvement

**Performance Trend Analysis**
- Longitudinal tracking of model performance improvements
- Identification of emerging knowledge gaps
- Framework coverage expansion recommendations
- Question difficulty calibration and adjustment

## Implementation Guidance for LLM Agents

### Designing New Evaluations

**Question Development Process**
1. Identify target framework(s) and specific controls/requirements
2. Determine appropriate complexity level (simple factual vs. complex reasoning)
3. Specify expected output format and structure requirements
4. Develop ground truth answer with proper control citations
5. Test question clarity and unambiguous interpretation

**Context Selection Strategy**
- Match context provision mode to evaluation objectives
- Ensure relevant framework documentation is available and current
- Validate vector database retrieval effectiveness for targeted content
- Consider context size limitations and processing constraints

**Scoring Calibration**
- Establish clear scoring criteria aligned with the three primary dimensions
- Develop specific examples of excellent, good, fair, and poor responses
- Test scoring consistency across multiple evaluators
- Refine rubrics based on edge case analysis

### Best Practices for Evaluation Design

**Framework Integration**
- Understand relationships and overlaps between different standards
- Design questions that test practical application rather than rote memorization
- Include scenarios that require reconciling potentially conflicting requirements
- Validate that questions reflect real-world implementation challenges

**Response Format Specification**
- Clearly define expected output structure (lists, paragraphs, tables, etc.)
- Specify required elements (control citations, practical steps, risk assessments)
- Provide examples of well-formatted responses
- Test format requirements for clarity and feasibility

**Quality Control Measures**
- Implement systematic review processes for new questions
- Validate ground truth accuracy through expert consultation
- Test questions across multiple model types and sizes
- Monitor for unexpected response patterns or evaluation failures

This methodology serves as both a reference for understanding the current benchmark system and a guide for expanding and improving the evaluation framework to maintain its effectiveness and relevance in assessing AI models' cybersecurity knowledge and application capabilities.



================================================
FILE: LICENSE
================================================
MIT License

Copyright (c) Jason M. Rodriguez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

NOTICE: While this repository strives to accurately represent the licenses for all included cybersecurity frameworks (found in data/cyber-frameworks/LICENSE), users are responsible for reviewing and complying with the original source licenses and terms of use for each framework.


================================================
FILE: llm-research.md
================================================
# LLM Cybersecurity Policy Research Guide
*A Comprehensive Framework for Evaluating Large Language Models in Cybersecurity Standards Compliance*

## Research Objectives & Hypotheses

### Primary Research Question
**How do different context delivery methods (no context, full documents, vector retrieval) affect LLM performance in cybersecurity compliance question answering, and which models demonstrate superior accuracy in control reference citation?**

### Hypotheses
1. **H1**: Models with larger context windows will demonstrate better performance when provided with complete framework documents versus vector-retrieved contexts
2. **H2**: Vector database retrieval will outperform no-context evaluation but underperform full document context for complex compliance questions
3. **H3**: Advanced models will show consistent performance across evaluation modes while smaller models will exhibit greater variation
4. **H4**: Control reference accuracy will correlate strongly with overall compliance answer quality across all evaluation modes

## Experimental Design Framework

### Independent Variables

#### Model Characteristics
- **Model Architecture**: Transformer variants (GPT, Claude, Gemini, LLaMA families)
- **Parameter Count**: Small (<7B), Medium (7-70B), Large (>70B)
- **Training Cutoff**: Pre-2023, 2023, 2024+
- **Context Window**: <32K, 32K-128K, >128K tokens

#### Evaluation Context Methods
- **NO_CONTEXT**: Models answer questions using only their training knowledge
- **RAW_FILES**: Complete framework documents provided as context (markdown format)
- **VECTOR_DB**: Relevant chunks retrieved via ChromaDB vector search

#### Document Processing Pipeline
- **Source Format**: PDF documents from cybersecurity frameworks
- **Conversion**: Docling library converts PDFs to structured markdown
- **Chunking**: HierarchicalChunker segments documents for vector storage
- **Embedding**: SentenceTransformer (all-MiniLM-L6-v2) generates embeddings
- **Storage**: ChromaDB with framework-specific collections

#### Standard Characteristics
- **Framework Type**: NIST CSF, ISO 27001, SOC 2, HIPAA, PCI DSS
- **Standard Vintage**: Current version, Previous version, Historical
- **Complexity Level**: Basic, Intermediate, Advanced
- **Document Length**: <50 pages, 50-200 pages, >200 pages

### Dependent Variables

#### Primary Outcomes
1. **LLM Judge Score** (0-1.0): Dual judge assessment of answer quality and accuracy
2. **Control Reference Score** (0-1.0): Overlap analysis of cited control references with ground truth
3. **Overall Accuracy Score** (0-1.0): Combined metric prioritizing LLM judge scores

#### Secondary Outcomes
1. **Judge Performance Metrics**: Success rates and agreement between dual judges
2. **Evaluation Mode Performance**: Comparative analysis across NO_CONTEXT, RAW_FILES, VECTOR_DB
3. **Model Reliability**: Consistency of performance across different question types
4. **Error Analysis**: Classification of failure modes (hallucination, omission, misinterpretation)

## Methodology Standards

### Dual Judge Scoring System

The benchmark implements a robust dual judge scoring system for reliable evaluation:

#### Architecture
- **Primary Judge**: Configurable model (default: anthropic/claude-sonnet-4)
- **Secondary Judge**: Configurable model (default: openai/gpt-4o) 
- **Fallback Mechanism**: If one judge fails, uses the other's score
- **Weighted Averaging**: Configurable weights for combining judge scores
- **Performance Tracking**: Success rates and agreement metrics

#### Scoring Methods
1. **CONTROL_REFERENCE**: Analyzes overlap of control citations (CC6.1, AC-2, etc.)
2. **LLM_JUDGE**: Comprehensive assessment of answer quality and accuracy

#### Judge Performance Metrics
- Individual judge success rates
- Dual judge success rate
- Fallback usage frequency
- Score discrepancy analysis

### Implementation Details

#### Command-Line Interface
```bash
# Basic evaluation with database setup
python cyber_policy_bench.py --models 2 --questions 3 --setup-db

# Custom evaluation parameters
python cyber_policy_bench.py --models 5 --questions 10
```

#### Programmatic Usage
```python
# Core evaluation components
evaluator = CyberPolicyEvaluator(vector_db=db)
scorer = TwoJudgeScorer()
reporter = create_benchmark_reporter()

# Execute evaluation pipeline
results = await evaluator.run_evaluation(models, questions, modes)
scored_results = await scorer.score_evaluation_results(results)
reports = reporter.generate_all_reports(scored_results)
```

### Quality Assurance Measures

#### Evaluation Dataset
- **Source**: data/prompts/cyber_evals.jsonl - curated cybersecurity compliance questions
- **Frameworks Covered**: SOC 2, NIST CSF, HIPAA, PCI DSS, CMMC, GDPR, and more
- **Question Types**: Control identification, compliance requirements, implementation guidance
- **Ground Truth**: Expert-validated ideal answers with proper control references

#### Reliability Measures
- **Dual Judge Validation**: Two independent LLM judges score each response
- **Fallback Protection**: System continues operation if one judge fails
- **Score Reconciliation**: Weighted averaging of judge scores with discrepancy detection
- **Performance Monitoring**: Real-time tracking of judge success rates and agreement

## Technical Implementation Requirements

### Technical Implementation Stack

#### Core Dependencies
- **Python**: 3.9+ runtime environment
- **OpenAI**: API client for model access via OpenRouter/OpenAI
- **ChromaDB**: Vector database with persistent storage
- **Docling**: PDF to markdown document conversion
- **SentenceTransformers**: Text embedding generation (all-MiniLM-L6-v2)
- **Asyncio**: Concurrent evaluation processing

#### System Architecture
```yaml
data_pipeline:
  document_processing:
    - PDF ingestion via Docling DocumentConverter
    - HierarchicalChunker for semantic segmentation
    - Multi-collection ChromaDB storage by framework
  
  evaluation_engine:
    - Async model querying with retry logic
    - Multi-mode evaluation (no_context, raw_files, vector_db)
    - Dual judge scoring with fallback mechanisms
  
  reporting_system:
    - HTML reports with interactive visualizations
    - JSON exports for programmatic access
    - Judge performance statistics
```

### Document Processing Pipeline
1. **Framework Discovery**: Scan data/cyber-frameworks/ directories with metadata.toml
2. **Document Conversion**: Docling converts PDFs to structured markdown
3. **Hierarchical Chunking**: Semantic-aware segmentation preserving document structure
4. **Embedding Generation**: SentenceTransformer creates vector representations
5. **Collection Storage**: Framework-specific ChromaDB collections for organized retrieval
6. **Metadata Preservation**: Framework type, domain, sector information maintained

### Evaluation Metrics Framework

#### Implemented Scoring Metrics
```python
scoring_result = {
    'accuracy_score': float,       # Primary score (0.0-1.0)
    'method': ScoringMethod,       # CONTROL_REFERENCE or LLM_JUDGE
    'explanation': str,            # Human-readable scoring rationale
    'details': dict               # Additional scoring metadata
}

control_reference_scoring = {
    'model_controls': set,         # Controls cited by model
    'ideal_controls': set,         # Expected control citations
    'intersection': set,           # Correctly identified controls
    'precision': float,            # Accuracy of cited controls
    'recall': float               # Coverage of expected controls
}
```

### Evaluation Pipeline Workflow

#### Initialization Phase
1. **Configuration Loading**: API keys and evaluation parameters from config.cfg
2. **Vector Database Setup**: ChromaDB initialization with framework-specific collections
3. **Model Discovery**: Available models from OpenRouter/OpenAI APIs
4. **Question Loading**: Evaluation questions from cyber_evals.jsonl

#### Evaluation Execution
1. **Multi-Mode Testing**: Each model tested across all evaluation modes
   - NO_CONTEXT: Pure model knowledge assessment
   - RAW_FILES: Complete framework documents as context
   - VECTOR_DB: Retrieved relevant chunks as context
2. **Concurrent Processing**: Async execution for efficiency
3. **Error Handling**: Retry logic with exponential backoff
4. **Progress Tracking**: Real-time evaluation progress monitoring

#### Scoring and Analysis
1. **Dual Judge Scoring**: Two independent judges evaluate each response
2. **Multi-Method Assessment**: Both control reference and LLM judge scoring
3. **Score Reconciliation**: Weighted averaging with fallback mechanisms
4. **Performance Analytics**: Success rates, agreement metrics, failure analysis

#### Results Generation
1. **Structured Data Export**: JSON format for programmatic analysis
2. **Interactive HTML Reports**: Visualizations and detailed breakdowns
3. **Judge Performance Metrics**: Reliability and agreement statistics

## Academic Writing Standards

### Research Contribution and Significance

#### Novel Contributions
1. **Comprehensive Multi-Context Evaluation**: First systematic comparison of LLM performance across no-context, full-document, and vector-retrieval scenarios for cybersecurity compliance
2. **Dual Judge Reliability System**: Production-ready scoring architecture with fallback mechanisms and performance monitoring
3. **Framework-Agnostic Assessment**: Standardized evaluation across diverse cybersecurity standards (SOC 2, NIST, HIPAA, PCI DSS, etc.)
4. **Practical Implementation Insights**: Real-world deployment patterns for cybersecurity AI systems

#### Academic and Practical Impact
- **Benchmarking Standard**: Reproducible methodology for evaluating cybersecurity-focused LLMs
- **Industry Application**: Evidence-based model selection for compliance automation
- **Quality Assurance**: Validated approaches for scoring AI-generated compliance responses
- **System Architecture**: Proven patterns for production cybersecurity question-answering systems

### Publication Readiness Checklist
- [x] **Evaluation Methodology**: Three-mode evaluation system fully implemented and documented
- [x] **Scoring Framework**: Dual judge system with multiple scoring methods operational
- [x] **Technical Architecture**: Complete system implementation with vector database and async processing
- [x] **Reproducibility**: Open source code, configuration management, and evaluation datasets available
- [x] **Performance Metrics**: Comprehensive success rates, agreement statistics, and error analysis
- [x] **Framework Coverage**: Multiple major cybersecurity standards processed and evaluated
- [x] **Results Generation**: Automated HTML reports and JSON exports for further analysis

### Statistical Analysis Approach

#### Descriptive Statistics
- **Score Distributions**: Mean, median, standard deviation for accuracy scores
- **Performance by Mode**: Comparative analysis across NO_CONTEXT, RAW_FILES, VECTOR_DB
- **Model Rankings**: Relative performance ordering with confidence intervals
- **Judge Agreement**: Inter-judge reliability and correlation metrics

#### Analytical Methods
- **Comparative Analysis**: Model performance across different evaluation contexts
- **Success Rate Analysis**: Proportion of successful evaluations by model and mode
- **Score Correlation**: Relationship between control reference and LLM judge scores
- **Error Categorization**: Classification of failure modes and their frequencies

#### Reporting Standards
- **Interactive Visualizations**: HTML reports with dynamic charts and tables
- **Performance Matrices**: Model vs. evaluation mode performance grids
- **Confidence Metrics**: Bootstrap confidence intervals for performance estimates
- **Reproducibility Data**: Complete evaluation logs and intermediate results

### Results Interpretation Framework

#### Primary Findings Analysis
1. **Context Method Effectiveness**: Which evaluation modes produce most accurate responses
2. **Model Performance Patterns**: Consistent high-performers vs. variable performers
3. **Judge System Reliability**: Success rates and agreement between scoring judges
4. **Control Citation Accuracy**: Quality of cybersecurity control references

#### Practical Applications
1. **Model Selection Guidance**: Evidence-based recommendations for cybersecurity Q&A
2. **Context Optimization**: Best practices for providing framework documentation
3. **Quality Assurance**: Reliable methods for evaluating compliance response accuracy
4. **System Architecture**: Proven patterns for production cybersecurity AI systems

## Reproducibility Requirements

### Framework Processing and Vector Database Architecture

#### Supported Cybersecurity Frameworks
The system processes multiple major cybersecurity frameworks:
- **SOC 2 Trust Services**: Trust-services-criteria.md
- **NIST Cybersecurity Framework**: NIST.CSWP.29.md
- **HIPAA Security Rule**: 2024-30983.md, NIST.SP.800-66r2.md
- **PCI DSS**: PCI-DSS-v4_0_1.md
- **NIST SP 800-53**: NIST.SP.800-53r5.md
- **CMMC**: AssessmentGuideL1.md, ScopingGuideL1v2.md
- **GDPR**: CELEX_32016R0679_EN_TXT.md

#### Multi-Collection Vector Database Design
```yaml
vector_database_architecture:
  storage_engine: ChromaDB with persistent storage
  embedding_model: SentenceTransformer 'all-MiniLM-L6-v2'
  collection_strategy: Framework-specific collections
  metadata_preservation:
    - framework_name: Standardized framework identifier
    - framework_type: Control-based, risk-based, etc.
    - domain: Healthcare, financial, general
    - sector: Industry-specific applicability
    - document: Source file within framework
```

#### Framework Metadata Structure
Each framework includes standardized metadata.toml:
```toml
[framework]
name = "soc2"
full_name = "SOC 2 Trust Services Criteria"
type = "control-based"

[metadata]
domain = "compliance"
sector = "general"

[files]
documents = ["Trust-services-criteria.md"]
```

### Code and Data Availability
- **Open Source Repository**: Complete implementation in Git with version control
- **Dependency Management**: requirements.txt with pinned versions
- **Configuration**: Example config files with clear documentation
- **Evaluation Data**: cyber_evals.jsonl with expert-validated questions
- **Framework Documents**: Public cybersecurity standards in markdown format

### Reproducibility Features
```yaml
reproducibility_measures:
  - Deterministic evaluation order and question selection
  - API request retry logic with exponential backoff
  - Complete evaluation logs with timestamps
  - Version-controlled evaluation questions and expected answers
  - Configurable model selection and scoring parameters
  - Automated report generation with consistent formatting
```

## Validation Checkpoints

### Current System Status
- [x] **Core Implementation**: Fully functional evaluation pipeline with async processing
- [x] **Vector Database**: Multi-collection ChromaDB with framework-specific organization
- [x] **Scoring System**: Dual judge architecture with graceful fallback handling
- [x] **Framework Processing**: Automated document conversion and chunking pipeline
- [x] **Reporting**: Interactive HTML reports and structured JSON exports
- [x] **Configuration Management**: Flexible API provider and model selection

### Pilot Study Validation
- [ ] 10% sample processed to validate methodology
- [ ] Inter-rater reliability established (α ≥ 0.80)
- [ ] Technical pipeline tested and debugged
- [ ] Statistical assumptions verified with pilot data

### Final Validation
- [ ] All hypotheses addressed with appropriate tests
- [ ] Effect sizes reported with confidence intervals
- [ ] Limitations honestly acknowledged
- [ ] Practical significance discussed alongside statistical significance

## Publication Strategy

### Publication Strategy

#### Target Venues
- **AI/ML Security**: NeurIPS Workshop on ML for Cybersecurity, ICML Security Workshop
- **Cybersecurity Conferences**: IEEE Security & Privacy, USENIX Security, ACM CCS
- **Applied AI Journals**: AI Magazine, Applied Intelligence, Expert Systems with Applications
- **Industry Publications**: IEEE Security & Privacy Magazine, Computer

#### Manuscript Focus Areas
1. **Technical Implementation**: Detailed system architecture and dual judge scoring
2. **Empirical Evaluation**: Comparative analysis across models and evaluation modes
3. **Practical Insights**: Real-world deployment considerations and performance patterns
4. **Reproducibility**: Complete methodology for replicating and extending results

## Ethical Considerations

### Data Protection
- No sensitive organizational data in training or evaluation
- Synthetic test cases where real standards cannot be shared
- IRB approval if human subjects involved in evaluation

### Responsible Disclosure
- Clear limitations stated regarding automated policy generation
- Warnings about need for expert review of AI-generated policies
- Discussion of potential misuse and mitigation strategies

---

*This guide should be reviewed and updated as the research progresses. Regular consultation with domain experts and statisticians is recommended to ensure methodological rigor.*


================================================
FILE: long_prompt_format.md
================================================
# Cybersecurity Policy Generation Prompt

Create a comprehensive **{policy_type}** for **{organization_name}** in Markdown format.

## Required Inputs:
- **Organization Overview:** Business details, industry, size, structure, tech infrastructure
- **Compliance Requirements:** Frameworks/regulations
- **Policy Parameters:** (Optional) Specific constraints, roles, systems, or data types

## Output Structure:

```markdown
# {Policy Type} Policy for {Organization Name}

## 1. Purpose and Scope
- Primary objective and coverage (systems, data, personnel, processes)
- Exclusions and limitations

## 2. Policy Statements
Core requirements varying by policy type:
- **Access Control:** Least privilege, RBAC, segregation of duties, account management, MFA, access reviews
- **Incident Response:** Classification, roles, preparation, detection, containment, recovery, communication
- **Data Classification:** Classification levels, criteria, responsibilities, handling requirements
- **Vulnerability Management:** Identification, prioritization, remediation, reporting, exceptions

## 3. Roles and Responsibilities
- Define specific roles (CISO, IT, Data Owners, Employees)
- Outline duties for each role

## 4. Compliance and Enforcement
- Compliance mechanisms and consequences
- Review cycles

## 5. Policy Review and Updates
- Review frequency and update process

## Appendices

### Appendix A: Glossary
Key terms, acronyms, and definitions

### Appendix B: Specific Requirements (Conditional)
Requirements for particular systems, personnel groups, or data types

### Appendix C: Framework Control Mappings
Direct links between policy statements and cybersecurity framework controls:
- **Policy Section:** Reference
- **Control ID:** Framework identifier
- **Description:** Control classifier
```

## Output Requirements:
- Clear, actionable language
- Direct alignment with compliance requirements
- Comprehensive coverage of the policy domain
- Ready for organizational implementation


================================================
FILE: requirements.txt
================================================
chromadb==1.0.16
docling==2.44.0
docling_core==2.44.1
openai==1.99.9
Requests==2.32.4
sentence_transformers==5.1.0
toml==0.10.2
types-requests


================================================
FILE: short_prompt.md
================================================
Create {policy_type} for {organization_name} as Markdown.

Inputs

Org overview (business, size, tech)
Compliance (standards/regulations)
(optional) Roles, systems, data constraints
Output

# {Policy Type} Policy – {Organization Name}

## Purpose & Scope  
## Policy Statements – Core requirements according to policy type. 
## Roles & Responsibilities  
## Compliance & Enforcement  
## Review Cycle  

## Appendices  
### Appendix A: Glossary
### Framework-Specific Requirements (as many and if any are necessary)
### Framework Mappings 
| Policy | Control ID | Description

Use concise, actionable language, that all personnel can understand and read; align with stated compliance.


================================================
FILE: test_scoring.py
================================================
#!/usr/bin/env python3
"""
Test script for validating the enhanced cyber policy evaluation system.
Tests the critical fixes for empty response handling and qualitative scoring.
"""

import asyncio
import json
from src.scorer import AccuracyScorer, ScoringMethod

async def test_empty_response_handling():
    """Test that empty and invalid responses are correctly scored as 0.0"""
    scorer = AccuracyScorer()
    
    print("Testing Empty Response Handling...")
    print("=" * 60)
    
    test_question = "What SOC 2 controls are required for access management?"
    ideal_answer = "SOC 2 requires CC6.1 (logical access controls), CC6.2 (access authorization), and CC6.3 (access removal)."
    
    # Test cases for invalid responses
    invalid_responses = [
        "",  # Empty
        "   ",  # Whitespace only
        "Error: Model timeout",  # Error message
        "MODEL_FAILURE: Connection failed",  # Model failure
        "I don't know",  # Non-substantive
        "N/A",  # Non-substantive
        "Sorry, I can't help with that",  # Non-substantive
        "Hi!",  # Too short
    ]
    
    for i, response in enumerate(invalid_responses):
        print(f"\n{i+1}. Testing response: '{response}'")
        
        # Test validation
        is_valid, reason = scorer.validate_response(response)
        print(f"   Validation: {'PASS' if not is_valid else 'FAIL'} - {reason}")
        
        # Test control reference scoring
        control_result = scorer.control_reference_score(response, ideal_answer)
        print(f"   Control Reference Score: {control_result.accuracy_score:.3f}")
        
        # Test LLM judge scoring
        judge_result = await scorer.llm_judge_score(test_question, response, ideal_answer)
        print(f"   LLM Judge Score: {judge_result.accuracy_score:.3f}")
        
        # Test contextual relevance
        relevance_result = scorer.contextual_relevance_score(response, test_question, ideal_answer)
        print(f"   Contextual Relevance Score: {relevance_result.accuracy_score:.3f}")
        
        # Verify all scores are 0.0 for invalid responses
        if (control_result.accuracy_score == 0.0 and 
            judge_result.accuracy_score == 0.0 and 
            relevance_result.accuracy_score == 0.0):
            print("   ✓ PASS: All scores correctly 0.0 for invalid response")
        else:
            print("   ✗ FAIL: Some scores not 0.0 for invalid response")

async def test_control_reference_edge_cases():
    """Test the fixed control reference scoring logic"""
    scorer = AccuracyScorer()
    
    print("\n\nTesting Control Reference Edge Cases...")
    print("=" * 60)
    
    # Test case 1: Both ideal and model have no controls, but model response is empty
    print("\n1. Empty response vs ideal with no controls:")
    empty_response = ""
    no_control_ideal = "Ensure proper documentation of security procedures."
    
    result = scorer.control_reference_score(empty_response, no_control_ideal)
    print(f"   Score: {result.accuracy_score:.3f} (should be 0.0)")
    print(f"   Explanation: {result.explanation}")
    
    # Test case 2: Both ideal and model have no controls, but model response is substantive
    print("\n2. Substantive response vs ideal with no controls:")
    good_response = "Security documentation should be comprehensive, regularly updated, and accessible to authorized personnel. It should include incident response procedures, access control policies, and compliance requirements to ensure organizational security posture."
    
    result = scorer.control_reference_score(good_response, no_control_ideal)
    print(f"   Score: {result.accuracy_score:.3f} (should be 1.0)")
    print(f"   Explanation: {result.explanation}")
    
    # Test case 3: Empty response vs ideal with controls
    print("\n3. Empty response vs ideal with controls:")
    control_ideal = "Implement CC6.1 for logical access controls and CC6.2 for access authorization."
    
    result = scorer.control_reference_score(empty_response, control_ideal)
    print(f"   Score: {result.accuracy_score:.3f} (should be 0.0)")
    print(f"   Explanation: {result.explanation}")

async def test_new_scoring_methods():
    """Test the new contextual relevance and completeness scoring methods"""
    scorer = AccuracyScorer()
    
    print("\n\nTesting New Scoring Methods...")
    print("=" * 60)
    
    question = "What are the key GDPR requirements for data breach notification?"
    ideal_answer = "GDPR Article 33 requires breach notification to supervisory authorities within 72 hours, and Article 34 requires notification to data subjects when high risk exists."
    
    # Test good response
    good_response = """GDPR establishes strict data breach notification requirements:

1. **Authority Notification (Article 33)**: Organizations must notify the relevant supervisory authority within 72 hours of becoming aware of a breach, unless the breach is unlikely to result in risk to rights and freedoms.

2. **Individual Notification (Article 34)**: Data subjects must be notified without undue delay when the breach is likely to result in high risk to their rights and freedoms.

3. **Documentation Requirements**: All breaches must be documented regardless of notification requirements, including facts, effects, and remedial actions taken."""
    
    # Test poor response
    poor_response = "You need to tell people about data breaches quickly."
    
    print("\n1. Testing Contextual Relevance Scoring:")
    print("\nGood Response:")
    relevance_result = scorer.contextual_relevance_score(good_response, question, ideal_answer)
    print(f"   Score: {relevance_result.accuracy_score:.3f}")
    print(f"   Details: {relevance_result.explanation}")
    
    print("\nPoor Response:")
    relevance_result = scorer.contextual_relevance_score(poor_response, question, ideal_answer)
    print(f"   Score: {relevance_result.accuracy_score:.3f}")
    print(f"   Details: {relevance_result.explanation}")
    
    print("\n2. Testing Completeness Scoring:")
    print("\nGood Response:")
    completeness_result = scorer.completeness_score(good_response, question, ideal_answer)
    print(f"   Score: {completeness_result.accuracy_score:.3f}")
    print(f"   Details: {completeness_result.explanation}")
    
    print("\nPoor Response:")
    completeness_result = scorer.completeness_score(poor_response, question, ideal_answer)
    print(f"   Score: {completeness_result.accuracy_score:.3f}")
    print(f"   Details: {completeness_result.explanation}")

async def test_composite_scoring():
    """Test the composite policy scoring method."""
    scorer = AccuracyScorer()
    
    # Sample policy question (from cyber_eval_041)
    question = """A SaaS startup wants to draft an acceptable usage policy that is compliant with SOC 2 and CMMC level 1. Create the policy using the short_prompt.md format with the following inputs: Org overview (SaaS startup, 50 employees, cloud-based services), Compliance (SOC 2 Type II, CMMC Level 1), Constraints (remote work environment, BYOD policy)."""
    
    # Sample good response (well-structured policy)
    good_response = """# Acceptable Usage Policy – SaaS Startup

## Purpose & Scope
This policy defines acceptable use of company systems and data to maintain SOC 2 and CMMC Level 1 compliance. Applies to all employees and contractors.

## Policy Statements
1. **System Access**: Multi-factor authentication required for all systems
2. **Data Handling**: Confidential data must be encrypted in transit and at rest
3. **Usage Restrictions**: No unauthorized software installation or credential sharing
4. **Device Management**: BYOD devices must be enrolled in MDM
5. **Monitoring**: All system usage is monitored and logged

## Roles & Responsibilities
- **IT Security**: Policy enforcement and monitoring
- **Employees**: Compliance with usage requirements
- **Management**: Policy exception approvals

## Compliance & Enforcement
Violations result in progressive discipline up to termination.

## Review Cycle
Annual review by IT Security team.

## Framework Mappings
| Policy Section | SOC 2 Control | CMMC Control | Description |
|---|---|---|---|
| System Access | CC6.1, CC6.2 | AC.L1-3.1.1 | Access controls |
| Data Handling | CC6.7 | SC.L1-3.13.1 | Data protection |
"""
    
    # Sample poor response (missing structure)
    poor_response = """Users should use strong passwords and not share them. Data should be protected. Management will enforce this policy. We follow SOC 2 and CMMC requirements."""
    
    ideal_answer = "A structured policy with all required sections per short_prompt.md format."
    
    print("Testing Composite Policy Scoring...")
    print("=" * 50)
    
    # Test good response
    print("\n1. Testing well-structured policy response:")
    result = await scorer.composite_policy_score(question, good_response, ideal_answer)
    print(f"Score: {result.accuracy_score:.3f}")
    print(f"Explanation: {result.explanation}")
    
    # Test poor response
    print("\n2. Testing poorly structured policy response:")
    result = await scorer.composite_policy_score(question, poor_response, ideal_answer)
    print(f"Score: {result.accuracy_score:.3f}")
    print(f"Explanation: {result.explanation}")
    
    print("\n" + "=" * 50)
    print("Testing individual scoring methods...")
    
    # Test structural validation
    struct_result = scorer.structural_validation_score(good_response, question)
    print(f"\nStructural validation score: {struct_result.accuracy_score:.3f}")
    print(f"Details: {struct_result.explanation}")
    
    # Test conciseness scoring
    concise_result = scorer.conciseness_score(good_response, question)
    print(f"\nConciseness score: {concise_result.accuracy_score:.3f}")
    print(f"Details: {concise_result.explanation}")

def test_question_loading():
    """Test loading and filtering of evaluation questions."""
    print("\nTesting question loading and filtering...")
    print("=" * 50)
    
    # Load questions with short_prompt format
    with open('data/prompts/cyber_evals.jsonl', 'r') as f:
        questions = []
        for line in f:
            line = line.strip()
            if line:
                question = json.loads(line)
                questions.append(question)
    
    # Filter for policy generation questions
    policy_questions = [q for q in questions if q['metadata'].get('format') == 'short_prompt']
    
    print(f"Total questions: {len(questions)}")
    print(f"Policy generation questions: {len(policy_questions)}")
    
    print("\nPolicy questions by framework:")
    for q in policy_questions:
        frameworks = q['metadata'].get('framework', 'N/A')
        industry = q['metadata'].get('industry', 'N/A')
        difficulty = q['metadata'].get('difficulty', 'N/A')
        print(f"  {q['question_id']}: {frameworks} ({industry}, {difficulty})")

if __name__ == "__main__":
    print("🧪 CYBER POLICY EVALUATION SYSTEM - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("Testing critical fixes for empty response handling and enhanced scoring\n")
    
    # Run all tests
    asyncio.run(test_empty_response_handling())
    asyncio.run(test_control_reference_edge_cases())
    asyncio.run(test_new_scoring_methods())
    test_question_loading()
    asyncio.run(test_composite_scoring())
    
    print("\n" + "=" * 80)
    print("🎉 COMPREHENSIVE TESTING COMPLETE!")
    print("\nKey fixes validated:")
    print("✓ Empty responses now correctly score 0.0 (prevents masking failures)")
    print("✓ Error messages properly detected and scored as failures") 
    print("✓ Control reference logic fixed for edge cases")
    print("✓ Enhanced rubrics capture qualitative nuance")
    print("✓ Response validation prevents scoring of invalid responses")
    print("✓ Composite scoring includes completeness and relevance assessment")


================================================
FILE: .adr-dir
================================================
doc/architecture/decisions



================================================
FILE: data/cyber-frameworks/LICENSE
================================================
# Cybersecurity Frameworks License and Attribution

## Important Notice

All cybersecurity frameworks, standards, and related documents contained within this directory and its subdirectories are **NOT** the property of this project. These documents have been converted from their original formats using docling for research and educational purposes.

## Original Ownership and Licensing

Each framework retains its original licensing terms, copyright, and ownership. The converted documents are subject to the terms and conditions of their respective original publishers.

## Conversion Notice

These documents have been processed using docling (document conversion tool) to convert from their original formats (typically PDF) into Markdown format for improved accessibility and machine readability. The conversion process:

- May introduce formatting changes from the original documents
- Preserves the substantive content to the best extent possible
- Does not alter the legal meaning or requirements of the original frameworks

## Usage Rights

Users of these converted documents must:

1. **Respect Original Rights**: Comply with all original licensing terms and copyright restrictions
2. **Attribute Properly**: Credit the original publishers and authors when using or referencing these materials
3. **Check for Updates**: Refer to original sources for the most current versions of these frameworks
4. **Non-Commercial Use**: Use these materials for educational, research, and compliance purposes

## Disclaimer

This project:
- Does NOT claim ownership of any cybersecurity framework or standard
- Does NOT guarantee the accuracy of converted documents
- Does NOT provide legal advice regarding compliance with these frameworks
- RECOMMENDS consulting original sources for authoritative guidance

## Questions or Concerns

For questions about specific framework licensing or to report conversion errors, please refer to the original publishing organizations listed above.

---

**Last Updated**: 2025
**Conversion Method**: docling
**Purpose**: Educational and research use within Cyber-Policy-Bench project


================================================
FILE: data/cyber-frameworks/cjis/metadata.toml
================================================
[framework]
name = "cjis"
full_name = "Criminal Justice Information Services"
standard = "CJIS Security Policy"
version = "5.8"
organization = "FBI - Department of Justice"
type = "law_enforcement_security"
scope = "criminal_justice_agencies"

[source]
original_url = "https://www.fbi.gov/services/cjis/cjis-security-policy-resource-center"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["CJIS-Security-Policy_v5-8_20190601.md"]

[metadata]
description = "CJIS Security Policy for protecting Criminal Justice Information"
domain = "law_enforcement_security"
sector = "law_enforcement"


================================================
FILE: data/cyber-frameworks/cmmc/metadata.toml
================================================
[framework]
name = "cmmc"
full_name = "Cybersecurity Maturity Model Certification"
standard = "CMMC Level 1"
version = "2.13"
organization = "Department of Defense"
type = "cybersecurity_maturity"
scope = "defense_contractors"

[source]
original_url = "https://www.acq.osd.mil/cmmc/"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["AssessmentGuideL1.md", "ScopingGuideL1v2.md"]

[metadata]
description = "CMMC Level 1 assessment and scoping guidance for defense contractors"
domain = "defense_cybersecurity"
sector = "defense"


================================================
FILE: data/cyber-frameworks/cmmc/ScopingGuideL1v2.md
================================================
Version 2.13 | September 2024 DoD-CIO-00005 (ZRIN 0790-ZA21)

## NOTICES

The contents of this document do not have the force and effect of law and are not meant to bind the public in any way. This document is intended only to provide clarity to the public regarding existing requirements under the law or departmental policies.

DISTRIBUTION STATEMENT A . Approved for public release. Distribution is unlimited.

## Introduction

This document provides scoping guidance for Level 1 of the Cybersecurity Maturity Model Certification (CMMC) as set forth in section 170.19 of title 32, Code of Federal Regulations (CFR). Guidance for scoping a Level 2 self-assessment or certification assessment can be found in the CMMC Scoping Guide - Level 2 document. Guidance for scoping a Level 3 certification assessment can be found in the CMMC Scoping Guide - Level 3 document. More details on the CMMC Model can be found in the CMMC Model Overview document.

## Purpose and Audience

This guide is intended for Organizations Seeking Assessment (OSAs) that will be conducting a Level 1 self-assessment and the professionals or companies that will support them in those efforts.

## Identifying the CMMC Assessment Scope

## Level 1 Assessment Scope

Prior to a Level 1 self-assessment the OSA must specify the CMMC Assessment Scope. The CMMC Assessment Scope defines which assets within the OSA's environment will be assessed and the details of the self-assessment. There are no documentation requirements for Level 1 self-assessments including In-Scope, Out-of-Scope, and Specialized Assets.

## In-Scope Assets

Assets in scope for a Level 1 self-assessment, as defined in 32 CFR § 170.19(b), are all assets that process, store, or transmit Federal Contract Information (FCI).

- Process - FCI is used by an asset (e.g., accessed, entered, edited, generated, manipulated, or printed).
- Store - FCI is inactive or at rest on an asset (e.g., located on electronic media, in system component memory, or in physical format such as paper documents).
- Transmit - FCI is being transferred from one asset to another asset (e.g., data in transit using physical or digital transport methods).

These assets are part of the CMMC Assessment Scope and are assessed against all Level 1 requirements.

## Out-of-Scope Assets

Assets out of scope for a Level 1 self-assessment, as defined in 32 CFR § 170.19(b)(2), are those that do not process, store, or transmit FCI. These assets are outside of the CMMC Assessment Scope and are not part of the assessment.

## Specialized Assets

Specialized Assets, as defined in 32 CFR § 170.19(b)(2)(ii), are those assets that can process, store, or transmit FCI but are unable to be fully secured, including: Internet of Things (IoT) devices, Industrial Internet of Things (IIoT) devices, Operational Technology (OT), Government Furnished Equipment (GFE), Restricted Information Systems, and Test Equipment. Specialized Assets are not part of the Level 1 self-assessment scope and are not assessed against CMMC requirements. The following assets, defined in 32 CFR § 170.4, are considered specialized assets for a Level 1 self-assessment.

- Government Furnished Equipment (GFE) has the same meaning as 'governmentfurnished property' as defined in 48 CFR § 45.101. Government-furnished property means property in the possession of, or directly acquired by, the Government and subsequently furnished to the contractor for performance of a contract. Governmentfurnished property includes, but is not limited to, spares and property furnished for repair, maintenance, overhaul, or modification. Government-furnished property also includes contractor-acquired property if the contractor-acquired property is a

deliverable under a cost contract when accepted by the Government for continued use under the contract.

- Internet of Things (IoT) or Industrial Internet of Things (IIoT) is defined is NIST SP 800-172A. These are interconnected devices having physical or virtual representation in the digital world, sensing/actuation capability, and programmability features. They are uniquely identifiable and may include smart electric grids, lighting, heating, air conditioning, and fire and smoke detectors [Reference: iot.ieee.org/definition; National Institute of Standards and Technology (NIST) 800-183].
- Operational Technology (OT) 1 means programmable systems or devices that interact with the physical environment (or manage devices that interact with the physical environment). These systems or devices detect or cause a direct change through the monitoring or control of devices, processes, and events. Examples include industrial control systems, building management systems, fire control systems, and physical access control mechanisms. [Source: NIST SP 800-160v2 Rev 1] NOTE: Operational Technology (OT) specifically includes Supervisory Control and Data Acquisition (SCADA); this is a rapidly evolving field. [Source: NIST SP 800-82r3]
- Restricted Information Systems means systems [and associated Information Technology (IT) components comprising the system] that are configured based entirely on government security requirements (i.e., connected to something that was required to support a functional requirement) and are used to support a contract (e.g., fielded systems, obsolete systems, and product deliverable replicas).
- Test Equipment means hardware and/or associated IT components used in the testing of products, system components, and contract deliverables.

1 Operational Technology includes hardware and software that use direct monitoring and control of industrial equipment to detect or cause a change.

## Additional Guidance on Level 1 Scoping

In accordance with 32 CFR § 170.19(b)(3), to appropriately scope a Level 1 self-assessment, the OSA should consider the people, technology, facilities, and external service providers within its environment that process, store, or transmit FCI.

- People - May include, but are not limited to, employees, contractors, vendors, and external service provider personnel.
- Technology - May include, but are not limited to, servers, client computers, mobile devices, network appliances (e.g., firewalls, switches, APs, and routers), VoIP devices, applications, virtual machines, and database systems.
- Facilities - May include, but are not limited to, physical office locations, satellite offices, server rooms, datacenters, manufacturing plants, and secured rooms.
- External Service Provider (ESP) -as defined in 32 CFR § 170.4, means external people, technology, or facilities that an OSA utilizes for provision and management of comprehensive IT and/or cybersecurity services on behalf of the OSA.

In accordance with 32 CFR § 170.19(b)(1), assets that process, store, or transmit FCI and which are not Specialized Assets are in the CMMC Assessment Scope. Using the asset types approach allows an OSA to determine how they will satisfy the Level 1 requirements. FCI is a broad category of information; therefore, the self-assessment may need to address a wide array of assets.

For example, identifying the people within the OSA who process, store, or transmit FCI, will assist with fulfillment of the assessment of the following Level 1 security requirement:

- IA.L1-b.1.v - Identify information system users, processes acting on behalf of users, or devices.

As another example, identification of all technologies may inform assessment of the following Level 1 security requirements:

- AC.L1-b.1.iii - Verify and control/limit connections to and use of external information systems.
- SC.L1-b.1.x - Monitor, control, and protect organizational communications (i.e., information transmitted or received by organizational information systems) at the external boundaries and key internal boundaries of the information systems.

Self-assessments and certification assessments may be valid for a defined CMMC Assessment Scope as outlined in 32 CFR § 170.19 CMMC Scoping. A new assessment is required if there are significant architectural or boundary changes to the previous CMMC Assessment Scope. Examples include, but are not limited to, expansions of networks or mergers and acquisitions. Operational changes within a CMMC Assessment Scope, such as adding or subtracting resources within the existing assessment boundary that follow the existing SSP 2 do not require a new assessment, but rather are covered by the annual affirmations to the continuing compliance with requirements.

2 It is recommended that an OSA develop a SSP as a best practice at Level 1. However, it is not required in order to conduct a Level 1 self-assessment.

This page intentionally left blank.



================================================
FILE: data/cyber-frameworks/fedramp/0012-vulnerability-management.md
================================================
## RFC-0012 Continuous Vulnerability Management Standard

Note: FedRAMP requirements documents use RFC 2119 key words to indicate requirement levels.

## RFC Front Matter

Due to the nature of this RFC, FedRAMP will be hosting two public events and public informal discussions in the FedRAMP Community about this RFC. General questions are encouraged in these public discussions to sharpen and focus public comment but the public must submit formal public comments for official consideration during the comment period.

- Status: Open

- Created By: FedRAMP

- Start Date: 2025-07-15

- Closing Date: 2025-08-21

- Short Name: rfc-0012-vulnerability-management

## Where to Comment

Members of the public may submit multiple different comments on different issues during the public comment period. The public is asked to please refrain from including documents or spreadsheets (especially those with in-line comments or suggested changes) in public comment as this creates a significant additional review burden.

Formal public comment for official consideration by FedRAMP can be made via the following mechanisms in order of preference:

1.  GitHub Post: https://github.com/FedRAMP/community/discussions/59
2.  Public Comment Form: https://forms.gle/adWgLmR9a4d7vMBW6
3.  Email: pete@fedramp.gov with the subject " RFC-0012 Feedback "

Note: FedRAMP will review and publicly post all public comments received via email, but will not otherwise respond. Email submissions from federal agencies will not be made public unless requested.

## Summary &amp; Motivation

This proposed Continuous Vulnerability Management Standard indicates an intended direction from FedRAMP and is not expected to be finalized in its exact current form. Once the RFC phase is completed, a modified version informed by public comment will be tested and evaluated with volunteer cloud service providers during a 20x Pilot and Rev5 Beta Tests then routinely refined and improved. FedRAMP now works with the community to understand the impact of its policies and adjust them based on real world experiences.

This RFC builds on stakeholder feedback to FedRAMP's recent RFC-0008 Continuous Reporting Standard and incorporates previous plans to update the Continuous Monitoring Performance Management Guide for 20x.

This standard's intent is to ensure providers promptly detect and respond to critical vulnerabilities by considering the entire context over Common Vulnerability Scoring System (CVSS) risk scores alone, prioritizing realistically exploitable weaknesses, and encouraging automated vulnerability management. It also aims to facilitate the use of existing commercial tools for cloud service providers and reduce custom government-only reporting requirements.

This standard implements changes in FedRAMP policy to meet this intent by:

- Defining new plain-language terms to move away from some commonly used but confusing language
- Including all weaknesses in the definition of a vulnerability
- Encouraging urgent mitigation of vulnerabilities prior to remediation

- Establishing requirements for assessing the context of vulnerabilities to determine impact and urgency
- Directly defining potential adverse impact levels
- Prioritizing the discovery, mitigation, and remediation of vulnerabilities in internet-reachable resources
- Setting expectations for continuous assessment, detection, and response where feasible with specific worst-case timelines for vulnerability management
- Requiring POA&amp;Ms only when providers won't respond within the recommended timelines

Reviewers are advised to read through the entire document for the full context and are reminded that FedRAMP 20x definitions for all standards apply to terms in this document; these terms are italicized when referenced.

## Effective Date(s) &amp; Overall Applicability

This is a draft standard released for public comment; it does not apply to any FedRAMP authorization and MUST NOT be used in draft form.

- FedRAMP 20x :
- This standard will initially apply to all FedRAMP 20x authorizations when formalized.
- FedRAMP Rev5 :
- See Balancing FedRAMP Rev5 against improvements to FedRAMP 20x for general information how improved FedRAMP standards will be applied carefully and deliberately to Rev5 authorizations.

## Background &amp; Authority

OMB Circular A-130: Managing Information as a Strategic Resource defines continuous monitoring as 'maintaining ongoing awareness of information security, vulnerabilities, threats, and incidents to support agency risk management decisions.'

The FedRAMP Authorization Act (44 USC § 3609 (a) (7)) directs the Administrator of the General Services Administration to 'coordinate with the FedRAMP Board, the Director of the Cybersecurity and Infrastructure Security Agency, and other entities identified by the Administrator, with the concurrence of the Director and the Secretary, to establish and regularly update a framework for continuous monitoring…'

## Purpose

The FedRAMP Continuous Vulnerability Management Standard ensures FedRAMP Authorized cloud service offerings use automated systems to effectively and continuously identify, analyze, prioritize, mitigate, and remediate vulnerabilities and related exposures to threats; and that information related to these activities are effectively and continuously reported to federal agencies for the purposes of ongoing authorization.

## Expected Outcomes

- Cloud service providers following commercial security best practices will be able to meet and validate FedRAMP security requirements with simple changes and automated capabilities
- Third-party independent assessors will have a simpler framework to assess security and implementation decisions that includes consideration of engineering decisions in context
- Federal agencies will be able to easily, quickly, and effectively review and consume security information about the service to make informed risk-based authorizations based on their use case

## Definitions

FRD-CVM-01

Vulnerability: Has the meaning given in NIST FIPS 200, which is 'weakness in an information system, system security procedures, internal controls, or implementation that could be exploited or triggered by a threat source.'

Note: See also the meaning given to 'security vulnerability' in 6 USC § 650 (25), which is 'any attribute of hardware, software, process, or procedure that could enable or facilitate the defeat of [...] management, operational, and technical controls used to protect against an unauthorized effort to adversely affect the confidentiality, integrity, and availability of an information system or its information.' This includes software vulnerabilities, misconfigurations, exposures, weak credentials, insecure services, and other weaknesses.

Reference: https://csrc.nist.gov/pubs/fips/200/final Reference:

https://www.govinfo.gov/app/details/USCODE-2024-title6/USCODE-2024-title 6-chap1-subchapXVIII-sec650

## FRD-CVM-02

Credibly exploitable vulnerability: A vulnerability where a likely threat actor with knowledge of the vulnerability would likely be able to gain unauthorized access, cause harm, disrupt operations, or otherwise have an undesired adverse impact; vulnerabilities must be reachable and not fully mitigated to be credibly exploitable.

## FRD-CVM-03

Remediate: Permanently remove a vulnerability; remediated vulnerabilities are not exploitable and no longer appear in scans or other analyses.

Note: See also the meaning given to 'remediation' in NIST SP 800-216, which is 'the neutralization or elimination of a vulnerability or the likelihood of its exploitation.'

## FRD-CVM-04

Mitigate: Temporarily reduce the risk that a vulnerability will be exploited or the potential adverse impact if it is exploited; mitigated vulnerabilities still appear in assessments until they are remediated.

Note: See also the meaning given to 'mitigation' in NIST SP 800-216, which is 'the temporary reduction or lessening of the adverse impact of a vulnerability or the likelihood of its exploitation.'

Reference: https://csrc.nist.gov/pubs/sp/800/216/final

## FRD-CVM-05

Fully Mitigate: Mitigate a vulnerability to the point where there is no reasonable probability of exploitation by any reasonable threat source, or the potential adverse impact of exploitation is Very Low ; fully mitigated vulnerabilities still appear in assessments until they are remediated.

## FRD-CVM-06

False Positive : Has the meaning given in NIST SP 800-115, which is 'an alert that incorrectly indicates that a vulnerability is present.'

Reference: https://csrc.nist.gov/pubs/sp/800/115/final

## FRD-CVM-07

Internet-reachable: Information resources that are reachable over the public internet such that anyone with an internet connection can interact with or deliver payloads to the information resource .

Note: This includes information resources that have no direct route to the internet but receive or process information or other payloads triggered by internet activity such as some logging services, some application services that process data submitted from internet-facing services, etc.

## FRD-CVM-08

Known Exploited Vulnerability: Has the meaning given in CISA BOD 22-01, which is any vulnerability identified in CISA's Known Exploited Vulnerabilities catalog.

## Reference:

https://www.cisa.gov/news-events/directives/bod-22-01-reducing-significant-r isk-known-exploited-vulnerabilities

Reference: https://www.cisa.gov/known-exploited-vulnerabilities-catalog

## FRD-CVM-09

Potential adverse impact (of vulnerability exploitation): The estimated effect of unauthorized access, disruption, harm, or other adverse impact to federal information that is likely to be caused by a threat actor exploiting a vulnerability. FedRAMP uses the five qualitative values described in NIST SP 800-30 Appendix H, which are:

1.  Very High: Exploitation could be expected to have multiple severe or catastrophic adverse effects.
2.  High: Exploitation could be expected to have a severe or catastrophic adverse effect. A severe or catastrophic adverse effect means that, for example, the threat event might: (i) cause a severe degradation in or loss of mission capability to an extent and duration that the organization is not able to perform one or more of its primary functions; (ii) result in major damage to organizational assets; (iii)

result in major financial loss; or (iv) result in severe or catastrophic harm to individuals involving loss of life or serious life-threatening injuries.

3.  Moderate: Exploitation could be expected to have a serious adverse effect. A serious adverse effect means that, for example, the threat event might: (i) cause a significant degradation in mission capability to an extent and duration that the organization is able to perform its primary functions, but the effectiveness of the functions is significantly reduced; (ii) result in significant damage to organizational assets; (iii) result in significant financial loss; or (iv) result in significant harm to individuals that does not involve loss of life or serious life-threatening injuries.
4.  Low: Exploitation could be expected to have a limited adverse effect. A limited adverse effect means that, for example, the threat event might: (i) cause a degradation in mission capability to an extent and duration that the organization is able to perform its primary functions, but the effectiveness of the functions is noticeably reduced; (ii) result in minor damage to organizational assets; (iii) result in minor financial loss; or (iv) result in minor harm to individuals.
5.  Very Low: Exploitation could be expected to have a negligible adverse effect.

Note: See also NIST FIPS 199 for additional background on measuring Potential Impact on Organizations and Individuals.

Reference: https://csrc.nist.gov/pubs/sp/800/30/r1/final

Reference: https://csrc.nist.gov/pubs/fips/199/final

## FRD-CVM-10

Promptly: As quickly as possible and without unnecessary delay.

## Requirements

## FRR-CVM

These requirements apply ALWAYS to ALL FedRAMP Authorized cloud services based on the current Effective Date(s) and Overall Applicability of this standard.

## FRR-CVM-01

Providers MUST establish and maintain programs that meet the requirements and timeframes in this standard to detect, evaluate, report, mitigate, and remediate vulnerabilities; these requirements supplement controls in FedRAMP Rev5 Baselines and Key Security Indicators in FedRAMP 20x.

Note: FedRAMP recommends that providers reference CISA's Stakeholder-Specific Vulnerability Categorization (SSVC) methodology and CISA's Federal Government Cybersecurity Incident and Vulnerability Response Playbooks.

## Reference:

https://www.cisa.gov/stakeholder-specific-vulnerability-categorization-ssvc Reference:

https://www.cisa.gov/resources-tools/resources/federal-government-cyberse curity-incident-and-vulnerability-response-playbooks

## FRR-CVM-02

Providers MUST create and maintain vulnerability reports showing vulnerability management activity that include at least the following information about all detected vulnerabilities within the FedRAMP Authorized cloud service offering :

1.  Provider's internal unique identifier for the vulnerability or grouping of similar vulnerabilities
2.  Relevant Common Vulnerabilities and Exposures (CVE) ID(s) and/or similar public identifiers
3.  Timeline (including at least time frames for detection, mitigation , and remediation )
4. Internet-reachable status of affected resources
5.  Exploitability assessment (is it credibly exploitable? )
6. Potential adverse impact assessment
7. Mitigation and/or remediation plan (including any customer responsibilities)
8. Mitigation and/or remediation measures taken (including any customer responsibilities)
9.  Changelog or other record of updates
10.  Point of contact for additional information

Note: This information SHOULD be limited to a minimum level of detail required (see FRR-CVM-07).

## FRR-CVM-03

Providers MUST make vulnerability reports available to all necessary parties in similar human-readable and compatible machine-readable formats, including at least FedRAMP, CISA, and all agency customers.

## FRR-CVM-04

Providers MUST adjust the risk and severity of vulnerabilities using CVSS base scores (if applicable) AND the context of the vulnerability, factoring for at least criticality, reachability, exploitability, detectability, prevalence, and mitigation , to determine if vulnerabilities are credibly exploitable and the potential adverse impact of exploitation.

## FRR-CVM-05

Providers SHOULD mitigate and/or remediate vulnerabilities promptly, within the time frames established in FRR-CVM-TM, and MUST create a FedRAMP Plan of Action &amp; Milestones (or future equivalent) to address any vulnerabilities that will not be addressed within those time frames.

## FRR-CVM-06

Providers SHOULD use automated systems to identify, mitigate , and/or remediate credibly exploitable vulnerabilities in internet-reachable information resources with minimal or no human intervention.

## FRR-CVM-07

Providers SHOULD NOT share specific sensitive information about vulnerabilities that would likely lead to exploitation, but MUST share sufficient information about vulnerabilities for oversight, tracking, analysis, action, and risk assessment with all necessary parties.

## FRR-CVM-08

Providers SHOULD maintain records of all false positive vulnerabilities and exclude validated false positive vulnerabilities from vulnerability reports.

## FRR-CVM-09

Providers SHOULD group similar vulnerabilities detected across different resources together for tracking, action, and reporting; these groups MUST use sensible provider-defined shared characteristics such as (but not limited to) common root cause, affected component, or remediation strategy.

## FRR-CVM-TM

These requirements identify specific time frame-based goals related to continuous vulnerability management.

## FRR-CVM-TM-01

Providers MUST provide up-to-date vulnerability reports to all necessary parties at least monthly and SHOULD provide these continuously.

## FRR-CVM-TM-02

Providers MUST make historical vulnerability reports covering at least the preceding 24 months available to all necessary parties.

## FRR-CVM-TM-03

Providers SHOULD remediate Known Exploited Vulnerabilities according to the due dates in the CISA Known Exploited Vulnerabilities Catalog (even if the vulnerability has been fully mitigated ).

Reference: https://www.cisa.gov/known-exploited-vulnerabilities-catalog

## FRR-CVM-TM-04

Providers SHOULD discover, analyze, and assess all internet-reachable resources for vulnerabilities using both authenticated and unauthenticated assessments continuously, otherwise at regular intervals at least every three calendar days.

## FRR-CVM-TM-05

Providers SHOULD fully mitigate or remediate credibly exploitable vulnerabilities in internet-reachable resources promptly , within three calendar days of detection.

## FRR-CVM-TM-06

Providers SHOULD discover, analyze, and assess all resources that are NOT internet-reachable for vulnerabilities using both authenticated and unauthenticated assessments continuously, otherwise at regular intervals at least once every seven calendar days for unauthenticated assessments and at least once every month for authenticated assessments.

## FRR-CVM-TM-07

Providers SHOULD mitigate or remediate credibly exploitable vulnerabilities in resources that are NOT internet-reachable promptly , within seven calendar days of detection, until or unless the potential adverse impact is Low or Very Low.

## FRR-CVM-TM-08

Providers SHOULD mitigate or remediate credibly exploitable impact vulnerabilities in resources that are NOT internet-reachable promptly , within 21 calendar days of detection until or unless the potential adverse impact is Very Low.

## FRR-CVM-TM-09

Providers MUST fully mitigate or remediate all remaining detected vulnerabilities on a regular basis promptly, at least every six months.

Quick Reference - Vulnerability Response Time Frames:

Applies to

Reachability

Impact

Action

Max Time

| Credibly  exploitable  vulnerabilities   | Internet-reachable     | Very High, High,  Moderate, Low   | Fully mitigate  or remediate   | 3 Days   |
|------------------------------------------|------------------------|-----------------------------------|--------------------------------|----------|
| Credibly  exploitable  vulnerabilities   | Not internet-reachable | Very High, High,  Moderate        | Mitigate to  Low or  remediate | 7 Days   |
| Credibly  exploitable  vulnerabilities   | Not internet-reachable | Low                               | Fully mitigate  or remediate   | 21 Days  |
| All detected  vulnerabilities            | Both                   | All                               | Fully mitigate  or remediate   | 6 Months |

Quick Reference - Discovery and Analysis Time Frames:

| Assessment Type   | Target Resources       | Assess At Least   |
|-------------------|------------------------|-------------------|
| Authenticated     | Internet-reachable     | Every 3 days      |
| Unauthenticated   | Internet-reachable     | Every 3 days      |
| Unauthenticated   | Not internet-reachable | Every 7 days      |
| Authenticated     | Not internet-reachable | Every 1 month     |

## FRR-CVM-AY

These requirements provide guidance on the application of this standard.

## FRR-CVM-AY-01

Providers MAY share vulnerability reports publicly or with other parties when doing so will not have a likely impact on the confidentiality, integrity, or availability of federal information .

## FRR-CVM-AY-02

Providers MAY provide additional security relevant metrics in their reporting as they deem appropriate.

## FRR-CVM-AY-03

All parties SHOULD follow FedRAMP's best practices and technical assistance on continuous vulnerability management and vulnerability reporting where applicable.

## FRR-CVM-EX

These exceptions MAY override FedRAMP requirements for this standard.

## FRR-CVM-EX-01

Providers MAY be required to share additional vulnerability information, alternative reports, or to report at an alternative frequency as a condition of a FedRAMP Corrective Action Plan or other agreements with federal agencies.

## FRR-CVM-EX-02

Providers MAY be required to provide additional information or details about vulnerabilities, including sensitive information that would likely lead to exploitation, as part of review, response or investigation by necessary parties; providers MUST NOT use this standard to reject requests for additional information from necessary parties which also includes law enforcement, Congress, and Inspectors General.


================================================
FILE: data/cyber-frameworks/fedramp/metadata.toml
================================================
[framework]
name = "fedramp"
full_name = "Federal Risk and Authorization Management Program"
standard = "RFC-0012 Continuous Vulnerability Management Standard"
version = "RFC-0012"
organization = "FedRAMP"
type = "vulnerability_management"
scope = "federal_cloud_services"

[source]
original_url = "https://www.fedramp.gov/"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["0012-vulnerability-management.md"]

[metadata]
description = "FedRAMP continuous vulnerability management standard for cloud service providers"
domain = "cloud_security"
sector = "government"


================================================
FILE: data/cyber-frameworks/gdpr/metadata.toml
================================================
[framework]
name = "gdpr"
full_name = "General Data Protection Regulation"
standard = "Regulation (EU) 2016/679"
version = "2016/679"
organization = "European Parliament and Council"
type = "data_protection"
scope = "european_union"

[source]
original_url = "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["CELEX_32016R0679_EN_TXT.md"]

[metadata]
description = "EU General Data Protection Regulation for personal data protection"
domain = "data_privacy"
sector = "general"


================================================
FILE: data/cyber-frameworks/hipaa/metadata.toml
================================================
[framework]
name = "hipaa"
full_name = "Health Insurance Portability and Accountability Act"
standard = "HIPAA Security Rule"
version = "2024 NPRM, SP 800-66r2"
organization = "HHS, NIST"
type = "healthcare_security"
scope = "healthcare_organizations"

[source]
original_url = "https://www.hhs.gov/hipaa/"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["2024-30983.md", "NIST.SP.800-66r2.md"]

[metadata]
description = "HIPAA Security Rule for protecting electronic protected health information"
domain = "healthcare_security"
sector = "healthcare"


================================================
FILE: data/cyber-frameworks/new-jersey-state/metadata.toml
================================================
[framework]
name = "new_jersey_state"
full_name = "New Jersey Statewide Information Security Manual"
standard = "New Jersey Executive Branch Information Security Manual"
version = "Current"
organization = "State of New Jersey"
type = "state_information_security"
scope = "new_jersey_state_government"

[source]
original_url = "https://www.state.nj.us/"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["NJ_Statewide_Information_Security_Manual_NOGLOSSARY.md"]

[metadata]
description = "New Jersey statewide information security manual for executive branch agencies"
domain = "state_government_security"
sector = "state_government"


================================================
FILE: data/cyber-frameworks/nist-800-171/metadata.toml
================================================
[framework]
name = "nist_800_171"
full_name = "NIST Special Publication 800-171"
standard = "SP 800-171r3"
version = "Revision 3"
organization = "National Institute of Standards and Technology"
type = "controlled_unclassified_information"
scope = "nonfederal_systems"

[source]
original_url = "https://csrc.nist.gov/publications/detail/sp/800-171/rev-3/final"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["NIST.SP.800-171r3.md"]

[metadata]
description = "NIST 800-171r3 for protecting Controlled Unclassified Information in nonfederal systems"
domain = "information_security"
sector = "general"


================================================
FILE: data/cyber-frameworks/nist-800-53/metadata.toml
================================================
[framework]
name = "nist_800_53"
full_name = "NIST Special Publication 800-53"
standard = "SP 800-53r5"
version = "Revision 5"
organization = "National Institute of Standards and Technology"
type = "security_privacy_controls"
scope = "information_systems_organizations"

[source]
original_url = "https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["NIST.SP.800-53r5.md"]

[metadata]
description = "NIST 800-53r5 security and privacy controls for information systems and organizations"
domain = "security_privacy_controls"
sector = "general"


================================================
FILE: data/cyber-frameworks/nist-csf/metadata.toml
================================================
[framework]
name = "nist_csf"
full_name = "NIST Cybersecurity Framework"
standard = "NIST CSWP 29"
version = "2.0"
organization = "National Institute of Standards and Technology"
type = "cybersecurity_framework"
scope = "all_organizations"

[source]
original_url = "https://www.nist.gov/cyberframework"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["NIST.CSWP.29.md"]

[metadata]
description = "NIST Cybersecurity Framework 2.0 for managing cybersecurity risks"
domain = "cybersecurity_governance"
sector = "general"


================================================
FILE: data/cyber-frameworks/pci-dss/metadata.toml
================================================
[framework]
name = "pci_dss"
full_name = "Payment Card Industry Data Security Standard"
standard = "PCI DSS"
version = "4.0.1"
organization = "PCI Security Standards Council"
type = "payment_card_security"
scope = "payment_card_industry"

[source]
original_url = "https://www.pcisecuritystandards.org/"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["PCI-DSS-v4_0_1.md"]

[metadata]
description = "PCI DSS 4.0.1 requirements and testing procedures for payment card data protection"
domain = "payment_security"
sector = "financial_services"


================================================
FILE: data/cyber-frameworks/soc2-trust-services/metadata.toml
================================================
[framework]
name = "soc_2"
full_name = "System and Organization Controls 2 - Trust Services Criteria"
standard = "Trust Services Criteria"
version = "2017 (Revised 2022)"
organization = "AICPA"
type = "trust_services"
scope = "service_organizations"

[source]
original_url = "https://www.aicpa.org/interestareas/frc/assuranceadvisoryservices/aicpasoc2report"
conversion_method = "docling"
original_format = "PDF"
converted_date = "2025"

[files]
documents = ["Trust-services-criteria.md"]

[metadata]
description = "2017 Trust Services Criteria for security, availability, processing integrity, confidentiality, and privacy"
domain = "service_organization_controls"
sector = "general"

================================================
FILE: doc/architecture/decisions/0001-record-architecture-decisions.md
================================================
# 1. Record architecture decisions

Date: 2025-08-11

## Status

Accepted

## Context

We need to record the architectural decisions made on this project.

## Decision

We will use Architecture Decision Records, as [described by Michael Nygard](http://thinkrelevance.com/blog/2011/11/15/documenting-architecture-decisions).

## Consequences

See Michael Nygard's article, linked above. For a lightweight ADR toolset, see Nat Pryce's [adr-tools](https://github.com/npryce/adr-tools).



================================================
FILE: doc/architecture/decisions/0002-using-docling-to-prepare-context-for-evals.md
================================================
# 2. Using Docling to prepare context for evals

Date: 2025-08-11

## Status

Accepted

## Context

This project initially explored creating custom data formats (YAML/JSON) for cybersecurity frameworks to support LLM evaluation research. However, after establishing the research methodology in `llm-research.md`, we identified that:

1. **Research Focus Shift**: The primary research question centers on LLM performance in cybersecurity policy generation, not data format optimization
2. **Processing Overhead**: Custom format conversion introduces unnecessary complexity and potential parsing errors
3. **Standardization Benefits**: Using consistent markdown format aligns with academic reproducibility standards
4. **Context Window Research**: The research specifically examines how different input formats (including raw text vs. structured) affect LLM performance

The IBM Docling tool provides high-quality PDF-to-markdown conversion that preserves document structure while maintaining readability for LLM processing.

## Decision

We will use Docling-converted markdown files in `data/cyber-frameworks/docling/` as the primary data source for LLM evaluations, abandoning custom YAML/JSON format development.

**Specific changes:**
- Remove `data/cyber-frameworks/json/` and `data/cyber-frameworks/yaml/` directories
- Remove custom conversion scripts and schema definitions
- Focus evaluation pipeline on processing markdown-formatted cybersecurity standards
- Maintain docling conversion outputs as the canonical source for research experiments

## Consequences

**Easier:**
- Simplified data pipeline with fewer conversion steps
- Direct use of high-quality, structured markdown for LLM input
- Reduced maintenance overhead for custom parsers and validators
- Better alignment with reproducible research practices
- Clear separation between data preparation and evaluation methodology

**More Difficult:**
- Loss of structured metadata that was captured in custom formats
- Need to parse requirements from markdown during evaluation rather than using pre-structured data
- Potential inconsistencies in how different documents are converted to markdown

**Risks and Mitigations:**
- **Risk**: Docling conversion quality varies across documents
  - **Mitigation**: Manual review of critical framework conversions, documented conversion quality assessment
- **Risk**: Markdown parsing complexity during evaluation
  - **Mitigation**: Robust evaluation framework with comprehensive error handling and validation checks



================================================
FILE: experiment_cache/model_cache.json
================================================
{
  "timestamp": "2025-08-21T06:38:18.299922",
  "models": {
    "gpt-5-chat": {
      "id": "gpt-5-chat",
      "name": "gpt-5-chat",
      "provider": "openai",
      "context_length": 128000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299650",
      "metadata": {
        "source": "configured"
      }
    },
    "mistralai/mistral-nemo": {
      "id": "mistralai/mistral-nemo",
      "name": "mistral-nemo",
      "provider": "mistralai",
      "context_length": 32000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299674",
      "metadata": {
        "source": "configured"
      }
    },
    "qwen/qwen3-30b-a3b": {
      "id": "qwen/qwen3-30b-a3b",
      "name": "qwen3-30b-a3b",
      "provider": "unknown",
      "context_length": 32000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299690",
      "metadata": {
        "source": "configured"
      }
    },
    "qwen/qwen3-coder": {
      "id": "qwen/qwen3-coder",
      "name": "qwen3-coder",
      "provider": "unknown",
      "context_length": 32000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299702",
      "metadata": {
        "source": "configured"
      }
    },
    "z-ai/glm-4.5": {
      "id": "z-ai/glm-4.5",
      "name": "glm-4.5",
      "provider": "unknown",
      "context_length": 8192,
      "capabilities": [
        "text_generation"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299713",
      "metadata": {
        "source": "configured"
      }
    },
    "gpt-5-mini": {
      "id": "gpt-5-mini",
      "name": "gpt-5-mini",
      "provider": "openai",
      "context_length": 128000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299724",
      "metadata": {
        "source": "configured"
      }
    },
    "moonshotai/kimi-k2": {
      "id": "moonshotai/kimi-k2",
      "name": "kimi-k2",
      "provider": "unknown",
      "context_length": 8192,
      "capabilities": [
        "text_generation"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299735",
      "metadata": {
        "source": "configured"
      }
    },
    "google/gemini-2.5-flash": {
      "id": "google/gemini-2.5-flash",
      "name": "gemini-2.5-flash",
      "provider": "google",
      "context_length": 32000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299747",
      "metadata": {
        "source": "configured"
      }
    },
    "deepseek/deepseek-v3": {
      "id": "deepseek/deepseek-v3",
      "name": "deepseek-v3",
      "provider": "deepseek",
      "context_length": 32000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299756",
      "metadata": {
        "source": "configured"
      }
    },
    "google/gemini-2.5-pro": {
      "id": "google/gemini-2.5-pro",
      "name": "gemini-2.5-pro",
      "provider": "google",
      "context_length": 32000,
      "capabilities": [
        "text_generation",
        "large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299767",
      "metadata": {
        "source": "configured"
      }
    },
    "anthropic/claude-sonnet-4": {
      "id": "anthropic/claude-sonnet-4",
      "name": "claude-sonnet-4",
      "provider": "anthropic",
      "context_length": 200000,
      "capabilities": [
        "text_generation",
        "very_large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299777",
      "metadata": {
        "source": "configured"
      }
    },
    "x-ai/grok-4": {
      "id": "x-ai/grok-4",
      "name": "grok-4",
      "provider": "unknown",
      "context_length": 8192,
      "capabilities": [
        "text_generation"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299787",
      "metadata": {
        "source": "configured"
      }
    },
    "anthropic/claude-3.7-sonnet": {
      "id": "anthropic/claude-3.7-sonnet",
      "name": "claude-3.7-sonnet",
      "provider": "anthropic",
      "context_length": 200000,
      "capabilities": [
        "text_generation",
        "very_large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299797",
      "metadata": {
        "source": "configured"
      }
    },
    "anthropic/claude-opus-4.1": {
      "id": "anthropic/claude-opus-4.1",
      "name": "claude-opus-4.1",
      "provider": "anthropic",
      "context_length": 200000,
      "capabilities": [
        "text_generation",
        "very_large_context"
      ],
      "pricing": {},
      "training_data_cutoff": null,
      "description": null,
      "performance_score": 0.5,
      "is_available": true,
      "last_updated": "2025-08-21T06:38:18.299805",
      "metadata": {
        "source": "configured"
      }
    }
  }
}


================================================
FILE: src/__init__.py
================================================
[Empty file]


================================================
FILE: src/base.py
================================================
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



================================================
FILE: src/benchmark.py
================================================
from typing import List, Dict, Optional
import requests
from datetime import datetime, timedelta

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
EVAL_MODELS = list_default_eval_models()



================================================
FILE: src/db.py
================================================
import chromadb
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from sentence_transformers import SentenceTransformer

# Import torch for MPS cache management on macOS
try:
    import torch

    # Check if MPS is available and enable memory-efficient empty cache
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
except ImportError:
    torch = None


# Use centralized config loading
from .utils import get_config, get_config_value

config = get_config()


class VectorDatabase:
    """Vector database for storing and retrieving cybersecurity framework chunks."""

    def __init__(self, db_path: str = None):
        """Initialize the vector database with multi-collection support."""
        if db_path is None:
            db_path = config.get("VectorDatabase", "db_path", fallback="./vector_db")
        self.db_path = Path(db_path)
        self.db_path.mkdir(exist_ok=True)

        # Initialize ChromaDB
        self.client = chromadb.PersistentClient(path=str(self.db_path))

        # Initialize embedding model
        embedding_model_name = config.get(
            "VectorDatabase", "embedding_model", fallback="all-MiniLM-L6-v2"
        )
        self.embedding_model = SentenceTransformer(embedding_model_name)

        # Store collections by framework name
        self.collections = {}

    def get_or_create_collection(self, framework_name: str) -> chromadb.Collection:
        """Get or create a collection for a specific framework."""
        # Framework names are already standardized, use them directly as collection names
        collection_name = framework_name

        if collection_name in self.collections:
            return self.collections[collection_name]

        try:
            collection = self.client.get_collection(collection_name)
        except Exception:
            vector_space = config.get(
                "VectorDatabase", "vector_space", fallback="cosine"
            )
            collection = self.client.create_collection(
                name=collection_name,
                metadata={"hnsw:space": vector_space, "framework": framework_name},
            )

        self.collections[collection_name] = collection
        return collection

    def add_chunks(self, chunks_data: Dict[str, Any]) -> None:
        """Add framework chunks to separate collections by framework."""
        total_chunks = 0

        for framework_name, framework_data in chunks_data.items():
            collection = self.get_or_create_collection(framework_name)

            documents = []
            metadatas = []
            ids = []

            for chunk in framework_data["chunks"]:
                documents.append(chunk["text"])
                metadatas.append(
                    {
                        "framework_name": chunk["framework_name"],
                        "framework_full_name": chunk["framework_full_name"],
                        "framework_type": chunk["framework_type"],
                        "document": chunk["document"],
                        "domain": chunk["domain"],
                        "sector": chunk["sector"],
                    }
                )
                ids.append(chunk["chunk_id"])

            if documents:
                # Generate embeddings
                embeddings = self.embedding_model.encode(documents).tolist()

                # Add to collection in batches
                batch_size = int(
                    config.get("VectorDatabase", "batch_size", fallback=100)
                )
                for i in range(0, len(documents), batch_size):
                    batch_docs = documents[i : i + batch_size]
                    batch_meta = metadatas[i : i + batch_size]
                    batch_ids = ids[i : i + batch_size]
                    batch_emb = embeddings[i : i + batch_size]

                    collection.add(
                        documents=batch_docs,
                        metadatas=batch_meta,
                        ids=batch_ids,
                        embeddings=batch_emb,
                    )

                total_chunks += len(documents)
                print(f"Added {len(documents)} chunks to {framework_name} collection")

        print(f"Total chunks added: {total_chunks}")

    def search(
        self, query: str, n_results: int = None, frameworks: Optional[List[str]] = None
    ) -> List[Dict]:
        """Search for relevant chunks across specified frameworks or all frameworks."""
        if n_results is None:
            n_results = self.config_overrides.get(
                "default_search_results",
                get_config_value("VectorDatabase", "default_search_results", 5, int),
            )
        all_results = []

        # If no frameworks specified, search all available collections
        if not frameworks:
            available_frameworks = []
            for collection in self.client.list_collections():
                available_frameworks.append(collection.name)
            frameworks = available_frameworks

        for framework_name in frameworks:
            try:
                collection = self.get_or_create_collection(framework_name)
                if collection.count() == 0:
                    continue

                results = collection.query(query_texts=[query], n_results=n_results)

                if results["documents"][0]:
                    for i, doc in enumerate(results["documents"][0]):
                        all_results.append(
                            {
                                "text": doc,
                                "metadata": results["metadatas"][0][i],
                                "distance": (
                                    results["distances"][0][i]
                                    if "distances" in results
                                    else None
                                ),
                                "framework": framework_name,
                            }
                        )
            except Exception as e:
                print(f"Warning: Could not search {framework_name} collection: {e}")
                continue

        # Sort by distance (lower is better) and limit to n_results
        all_results.sort(key=lambda x: x.get("distance", float("inf")))
        return all_results[:n_results]

    def search_framework(
        self, query: str, framework_name: str, n_results: int = None
    ) -> List[Dict]:
        """Search within a specific framework collection."""
        if n_results is None:
            n_results = self.config_overrides.get(
                "default_search_results",
                get_config_value("VectorDatabase", "default_search_results", 5, int),
            )
        try:
            collection = self.get_or_create_collection(framework_name)
            if collection.count() == 0:
                return []

            results = collection.query(query_texts=[query], n_results=n_results)

            formatted_results = []
            if results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append(
                        {
                            "text": doc,
                            "metadata": results["metadatas"][0][i],
                            "distance": (
                                results["distances"][0][i]
                                if "distances" in results
                                else None
                            ),
                            "framework": framework_name,
                        }
                    )

            return formatted_results
        except Exception as e:
            print(f"Warning: Could not search {framework_name} collection: {e}")
            return []

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about all collections."""
        total_chunks = 0
        frameworks = {}
        collection_details = {}

        # Get stats from all existing collections
        for collection_name in self.client.list_collections():
            try:
                collection = self.client.get_collection(collection_name.name)
                count = collection.count()
                total_chunks += count

                # Get framework name from metadata or collection name
                framework_name = collection_name.name
                if hasattr(collection_name, "metadata") and collection_name.metadata:
                    framework_name = collection_name.metadata.get(
                        "framework", collection_name.name
                    )

                frameworks[framework_name] = count
                collection_details[collection_name.name] = {
                    "framework": framework_name,
                    "chunks": count,
                }
            except Exception as e:
                print(
                    f"Warning: Could not get stats for collection {collection_name.name}: {e}"
                )

        return {
            "total_chunks": total_chunks,
            "frameworks": frameworks,
            "collections": collection_details,
            "num_collections": len(collection_details),
        }

    @classmethod
    def initialize_from_chunks(
        cls, chunks_file_dir: str = "output/chunks", db_path: str = None
    ) -> "VectorDatabase":
        """Initialize database from existing chunk files with separate collections."""
        db = cls(db_path=db_path)

        chunks_path = Path(chunks_file_dir)
        all_chunks = {}

        # Load all chunk files
        for chunk_file in chunks_path.glob("*_chunks.json"):
            with open(chunk_file, "r", encoding="utf-8") as f:
                framework_data = json.load(f)
                framework_name = framework_data["metadata"]["framework"]["name"]
                all_chunks[framework_name] = framework_data

        # Add chunks to database (now creates separate collections)
        if all_chunks:
            db.add_chunks(all_chunks)
            print(
                f"Initialized database with {len(all_chunks)} frameworks in separate collections"
            )

        return db



================================================
FILE: src/evaluator.py
================================================
import asyncio
import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass
from enum import Enum
import openai

try:
    from .db import VectorDatabase
    from .utils import get_config_value, get_openai_client
    from .benchmark import list_default_eval_models
except ImportError:
    from src.db import VectorDatabase
    from src.utils import get_config_value, get_openai_client
    from src.benchmark import list_default_eval_models


class EvaluationMode(Enum):
    NO_CONTEXT = "no_context"
    RAW_FILES = "raw_files"
    VECTOR_DB = "vector_db"


@dataclass
class EvaluationResult:
    question: str
    ideal_answer: str
    model_response: str
    model_name: str
    evaluation_mode: EvaluationMode
    context_provided: Optional[str] = None
    accuracy_score: Optional[float] = None
    timestamp: Optional[str] = None


class CyberPolicyEvaluator:
    """Evaluator for cybersecurity policy benchmark tests."""

    def __init__(
        self,
        vector_db: Optional[VectorDatabase] = None,
        client: Optional[openai.OpenAI] = None,
        config_overrides: Optional[Dict[str, Any]] = None,
    ):
        """Initialize evaluator with injected dependencies.

        Args:
            vector_db: Vector database for context retrieval
            client: OpenAI client for API calls
            config_overrides: Override configuration values
        """
        self.vector_db = vector_db
        self.client = client or get_openai_client()
        self.config_overrides = config_overrides or {}

    def load_evaluation_questions(
        self, questions_file: str = None, filter_criteria: Dict[str, str] = None
    ) -> List[Dict]:
        """Load evaluation questions from JSONL file with optional filtering."""
        if questions_file is None:
            questions_file = self.config_overrides.get(
                "prompts_file",
                get_config_value(
                    "Paths", "prompts_file", "./data/prompts/cyber_evals.jsonl"
                ),
            )

        questions = []
        with open(questions_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    question = json.loads(line)

                    # Apply filters if provided
                    if filter_criteria:
                        metadata = question.get("metadata", {})
                        include_question = True

                        for key, value in filter_criteria.items():
                            if key == "difficulty":
                                if metadata.get("difficulty") != value:
                                    include_question = False
                                    break
                            elif key == "framework":
                                frameworks = metadata.get("framework", "").split(",")
                                if value not in [f.strip() for f in frameworks]:
                                    include_question = False
                                    break
                            elif key == "category":
                                if metadata.get("category") != value:
                                    include_question = False
                                    break
                            elif key == "question_type":
                                if metadata.get("question_type") != value:
                                    include_question = False
                                    break

                        if not include_question:
                            continue

                    questions.append(question)
        return questions

    def load_raw_framework_files(self, frameworks_dir: str = None) -> Dict[str, str]:
        """Load raw framework markdown files for context."""
        if frameworks_dir is None:
            frameworks_dir = self.config_overrides.get(
                "frameworks_dir",
                get_config_value("Paths", "frameworks_dir", "./data/cyber-frameworks"),
            )

        framework_content = {}
        frameworks_path = Path(frameworks_dir)

        for framework_dir in frameworks_path.iterdir():
            if not framework_dir.is_dir() or framework_dir.name == "LICENSE":
                continue

            # Find markdown files in the framework directory
            md_files = list(framework_dir.glob("*.md"))
            if md_files:
                combined_content = []
                for md_file in md_files:
                    with open(md_file, "r", encoding="utf-8") as f:
                        combined_content.append(f"## {md_file.name}\n{f.read()}")
                framework_content[framework_dir.name] = "\n\n".join(combined_content)

        return framework_content

    async def query_model(
        self, model_name: str, prompt: str, max_retries: int = 3
    ) -> dict:
        """
        Query a model with the given prompt.

        Returns:
            dict: {"response": str, "error": bool, "error_message": str}
        """
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                )
                content = response.choices[0].message.content.strip()

                # Basic validation of response
                if not content:
                    return {
                        "response": "",
                        "error": True,
                        "error_message": "Model returned empty response",
                    }

                return {"response": content, "error": False, "error_message": ""}

            except Exception as e:
                error_msg = str(e)
                if attempt == max_retries - 1:
                    return {
                        "response": "",
                        "error": True,
                        "error_message": f"Model query failed after {max_retries} attempts: {error_msg}",
                    }
                await asyncio.sleep(2**attempt)  # Exponential backoff

    def create_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Create evaluation prompt with optional context."""
        if context:
            return f"""Context:
{context}

Question: {question}

Please provide a precise answer based on the context provided. Be specific about which requirements or controls are relevant."""
        else:
            return f"Question: {question}\n\nPlease provide a precise answer based on your knowledge of cybersecurity frameworks and compliance requirements."

    def detect_frameworks_in_question(self, question: str) -> List[str]:
        """Detect which frameworks are mentioned in the evaluation question."""
        question_lower = question.lower()
        detected_frameworks = []

        # Framework detection patterns that return standardized names
        framework_patterns = {
            "nist_csf": ["nist csf", "nist cybersecurity framework", "csf"],
            "soc_2": ["soc 2", "soc2", "soc-2", "trust services"],
            "cmmc": ["cmmc", "cybersecurity maturity model certification"],
            "nist_800_53": ["nist 800-53", "800-53", "nist sp 800-53"],
            "nist_800_171": ["nist 800-171", "800-171", "nist sp 800-171"],
            "pci_dss": ["pci dss", "pci", "payment card industry"],
            "hipaa": ["hipaa", "health insurance portability"],
            "gdpr": ["gdpr", "general data protection regulation"],
            "fedramp": ["fedramp", "federal risk and authorization"],
            "cjis": ["cjis", "criminal justice information services"],
            "new_jersey_state": ["new jersey", "nj state"],
        }

        for framework_name, patterns in framework_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                detected_frameworks.append(framework_name)

        return detected_frameworks

    def get_vector_context(self, question: str, n_results: int = None) -> Optional[str]:
        """Retrieve relevant context from vector database with intelligent framework detection."""
        if not self.vector_db:
            return None

        if n_results is None:
            n_results = get_config_value("Evaluation", "vector_context_results", 3, int)

        # Detect frameworks mentioned in the question
        detected_frameworks = self.detect_frameworks_in_question(question)

        # If specific frameworks detected, search those collections
        if detected_frameworks:
            results = self.vector_db.search(
                question, n_results=n_results, frameworks=detected_frameworks
            )
            print(
                f"Detected frameworks: {detected_frameworks}, found {len(results)} results"
            )
        else:
            # Fall back to searching all frameworks
            results = self.vector_db.search(question, n_results=n_results)
            print(
                f"No specific frameworks detected, searching all collections, found {len(results)} results"
            )

        if not results:
            return None

        context_parts = []
        for result in results:
            fw_name = result["metadata"]["framework_name"]
            context_parts.append(f"[{fw_name}] {result['text']}")

        return "\n\n".join(context_parts)

    def get_raw_file_context(
        self, question: str, framework_files: Dict[str, str]
    ) -> Optional[str]:
        """Get relevant raw file context by detecting framework mentions in question."""
        # Use the same framework detection logic
        detected_frameworks = self.detect_frameworks_in_question(question)
        relevant_frameworks = []

        # Map standardized framework names to directory names
        framework_to_dir = {
            "nist_csf": "nist-csf",
            "soc_2": "soc2-trust-services",
            "cmmc": "cmmc",
            "nist_800_53": "nist-800-53",
            "nist_800_171": "nist-800-171",
            "pci_dss": "pci-dss",
            "hipaa": "hipaa",
            "gdpr": "gdpr",
            "fedramp": "fedramp",
            "cjis": "cjis",
            "new_jersey_state": "new-jersey-state",
        }

        # Get content for detected frameworks
        for framework_name in detected_frameworks:
            framework_dir = framework_to_dir.get(framework_name)
            if framework_dir and framework_dir in framework_files:
                relevant_frameworks.append(framework_files[framework_dir])

        if relevant_frameworks:
            return "\n\n".join(relevant_frameworks)

        # If no specific framework found, return first available (fallback)
        if framework_files:
            return list(framework_files.values())[0]

        return None

    async def evaluate_single_question(
        self,
        question_data: Dict,
        model_name: str,
        evaluation_mode: EvaluationMode,
        framework_files: Optional[Dict[str, str]] = None,
    ) -> EvaluationResult:
        """Evaluate a single question with a specific model and mode."""
        question = question_data["input"]
        ideal_answer = question_data["ideal"]

        # Prepare context based on evaluation mode
        context = None
        if evaluation_mode == EvaluationMode.VECTOR_DB:
            context = self.get_vector_context(question)
        elif evaluation_mode == EvaluationMode.RAW_FILES and framework_files:
            context = self.get_raw_file_context(question, framework_files)

        # Create prompt and query model
        prompt = self.create_prompt(question, context)
        query_result = await self.query_model(model_name, prompt)

        # Handle query errors properly
        if query_result["error"]:
            model_response = f"MODEL_FAILURE: {query_result['error_message']}"
        else:
            model_response = query_result["response"]

        return EvaluationResult(
            question=question,
            ideal_answer=ideal_answer,
            model_response=model_response,
            model_name=model_name,
            evaluation_mode=evaluation_mode,
            context_provided=context,
            timestamp=datetime.now().isoformat(),
        )

    async def run_evaluation(
        self,
        models: List[str],
        questions: List[Dict],
        modes: List[EvaluationMode],
        output_dir: str = "experiment_results",
    ) -> Dict[str, List[Dict]]:
        """Run complete evaluation across models, questions, and modes."""
        results = {}
        framework_files = None

        # Load framework files if needed
        if EvaluationMode.RAW_FILES in modes:
            framework_files = self.load_raw_framework_files()

        # Initialize vector DB if needed
        if EvaluationMode.VECTOR_DB in modes and not self.vector_db:
            print("Initializing vector database with multi-collection support...")
            self.vector_db = VectorDatabase.initialize_from_chunks()

        total_evaluations = len(models) * len(questions) * len(modes)
        completed = 0

        print(
            f"Starting evaluation: {len(models)} models × {len(questions)} questions × {len(modes)} modes = {total_evaluations} total evaluations"
        )

        for model_name in models:
            model_results = []
            print(f"\nEvaluating model: {model_name}")

            for mode in modes:
                print(f"  Mode: {mode.value}")

                for i, question_data in enumerate(questions):
                    try:
                        result = await self.evaluate_single_question(
                            question_data, model_name, mode, framework_files
                        )
                        model_results.append(result)
                        completed += 1

                        if (i + 1) % 5 == 0:  # Progress update every 5 questions
                            print(f"    Completed {i + 1}/{len(questions)} questions")

                    except Exception as e:
                        print(f"    Error evaluating question {i + 1}: {e}")
                        completed += 1
                        continue

                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.5)

            results[model_name] = model_results
            print(f"  Completed {model_name}: {len(model_results)} results")

        # Convert results to dict format for downstream compatibility
        dict_results = {}
        for model_name, model_results in results.items():
            dict_results[model_name] = [
                {
                    "question": r.question,
                    "ideal_answer": r.ideal_answer,
                    "model_response": r.model_response,
                    "model_name": r.model_name,
                    "evaluation_mode": r.evaluation_mode.value,
                    "context_provided": r.context_provided,
                    "accuracy_score": r.accuracy_score,
                    "timestamp": r.timestamp,
                }
                for r in model_results
            ]

        # Save results
        self.save_results(results, output_dir)
        print(f"\nEvaluation complete! Results saved to {output_dir}")

        return dict_results

    def save_results(
        self, results: Dict[str, List[EvaluationResult]], output_dir: str
    ) -> None:
        """Save evaluation results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Save detailed results
        detailed_results = {}
        for model_name, model_results in results.items():
            detailed_results[model_name] = [
                {
                    "question": r.question,
                    "ideal_answer": r.ideal_answer,
                    "model_response": r.model_response,
                    "evaluation_mode": r.evaluation_mode.value,
                    "context_provided": r.context_provided,
                    "accuracy_score": r.accuracy_score,
                    "timestamp": r.timestamp,
                }
                for r in model_results
            ]

        with open(output_path / "detailed_results.json", "w", encoding="utf-8") as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)

        print(f"Detailed results saved to {output_path / 'detailed_results.json'}")

    def generate_metadata_report(
        self, results: Dict[str, List[EvaluationResult]], questions: List[Dict]
    ) -> Dict[str, any]:
        """Generate comprehensive report analyzing performance by metadata dimensions."""
        report = {
            "summary": {},
            "by_difficulty": {},
            "by_framework": {},
            "by_category": {},
            "by_question_type": {},
            "recommendations": [],
        }

        # Create question metadata lookup
        question_metadata = {}
        for q in questions:
            question_metadata[q["input"]] = q.get("metadata", {})

        all_scores = []
        difficulty_scores = {}
        framework_scores = {}
        category_scores = {}
        type_scores = {}

        for model_name, model_results in results.items():
            for result in model_results:
                if result.accuracy_score is not None:
                    score = result.accuracy_score
                    all_scores.append(score)

                    # Get metadata for this question
                    metadata = question_metadata.get(result.question, {})

                    # Aggregate by difficulty
                    difficulty = metadata.get("difficulty", "unknown")
                    if difficulty not in difficulty_scores:
                        difficulty_scores[difficulty] = []
                    difficulty_scores[difficulty].append(score)

                    # Aggregate by framework (handle multi-framework)
                    frameworks = metadata.get("framework", "unknown").split(",")
                    for framework in frameworks:
                        framework = framework.strip()
                        if framework not in framework_scores:
                            framework_scores[framework] = []
                        framework_scores[framework].append(score)

                    # Aggregate by category
                    category = metadata.get("category", "unknown")
                    if category not in category_scores:
                        category_scores[category] = []
                    category_scores[category].append(score)

                    # Aggregate by question type
                    q_type = metadata.get("question_type", "unknown")
                    if q_type not in type_scores:
                        type_scores[q_type] = []
                    type_scores[q_type].append(score)

        # Calculate summary statistics
        if all_scores:
            report["summary"] = {
                "total_evaluations": len(all_scores),
                "overall_average": sum(all_scores) / len(all_scores),
                "median_score": sorted(all_scores)[len(all_scores) // 2],
                "min_score": min(all_scores),
                "max_score": max(all_scores),
                "score_distribution": {
                    "excellent_90_100": len([s for s in all_scores if s >= 0.9])
                    / len(all_scores),
                    "good_80_89": len([s for s in all_scores if 0.8 <= s < 0.9])
                    / len(all_scores),
                    "fair_70_79": len([s for s in all_scores if 0.7 <= s < 0.8])
                    / len(all_scores),
                    "poor_below_70": len([s for s in all_scores if s < 0.7])
                    / len(all_scores),
                },
            }

        # Calculate performance by difficulty
        for difficulty, scores in difficulty_scores.items():
            if scores:
                report["by_difficulty"][difficulty] = {
                    "count": len(scores),
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                }

        # Calculate performance by framework
        for framework, scores in framework_scores.items():
            if scores:
                report["by_framework"][framework] = {
                    "count": len(scores),
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                }

        # Calculate performance by category
        for category, scores in category_scores.items():
            if scores:
                report["by_category"][category] = {
                    "count": len(scores),
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                }

        # Calculate performance by question type
        for q_type, scores in type_scores.items():
            if scores:
                report["by_question_type"][q_type] = {
                    "count": len(scores),
                    "average": sum(scores) / len(scores),
                    "min": min(scores),
                    "max": max(scores),
                }

        # Generate recommendations
        recommendations = []

        # Difficulty-based recommendations
        if "expert" in difficulty_scores and "intermediate" in difficulty_scores:
            expert_avg = sum(difficulty_scores["expert"]) / len(
                difficulty_scores["expert"]
            )
            intermediate_avg = sum(difficulty_scores["intermediate"]) / len(
                difficulty_scores["intermediate"]
            )
            if expert_avg < intermediate_avg - 0.1:
                recommendations.append(
                    f"Expert questions showing {intermediate_avg - expert_avg:.2f} point gap vs intermediate - consider expert-specific training"
                )

        # Framework-specific recommendations
        framework_averages = {
            k: sum(v) / len(v) for k, v in framework_scores.items() if v
        }
        if framework_averages:
            lowest_framework = min(framework_averages, key=framework_averages.get)
            highest_framework = max(framework_averages, key=framework_averages.get)
            gap = (
                framework_averages[highest_framework]
                - framework_averages[lowest_framework]
            )
            if gap > 0.15:
                recommendations.append(
                    f"Significant framework gap: {lowest_framework} ({framework_averages[lowest_framework]:.2f}) vs {highest_framework} ({framework_averages[highest_framework]:.2f}) - focus training on {lowest_framework}"
                )

        # Category-based recommendations
        category_averages = {
            k: sum(v) / len(v) for k, v in category_scores.items() if v
        }
        if category_averages:
            lowest_category = min(category_averages, key=category_averages.get)
            if category_averages[lowest_category] < 0.7:
                recommendations.append(
                    f"Low performance in {lowest_category} ({category_averages[lowest_category]:.2f}) - consider specialized training"
                )

        report["recommendations"] = recommendations
        return report


async def run_benchmark_poc(num_models: int = 3, num_questions: int = 5):
    """Run a proof of concept benchmark with a subset of models and questions."""
    print("=== Cyber-Policy-Bench - Proof of Concept ===")

    # Initialize evaluator
    evaluator = CyberPolicyEvaluator()

    # Get subset of models and questions
    all_models = list_default_eval_models()
    models = all_models[:num_models]

    questions = evaluator.load_evaluation_questions()
    questions = questions[:num_questions]

    # Define evaluation modes
    modes = [
        EvaluationMode.NO_CONTEXT,
        EvaluationMode.RAW_FILES,
        EvaluationMode.VECTOR_DB,
    ]

    print(
        f"Testing {len(models)} models with {len(questions)} questions in {len(modes)} modes"
    )
    print(f"Models: {models}")

    # Run evaluation
    results = await evaluator.run_evaluation(models, questions, modes)

    # Print summary
    print("\n=== EVALUATION SUMMARY ===")
    for model_name, model_results in results.items():
        print(f"{model_name}: {len(model_results)} total evaluations")

        # Group by mode
        mode_counts = {}
        for result in model_results:
            mode = result.evaluation_mode.value
            mode_counts[mode] = mode_counts.get(mode, 0) + 1

        for mode, count in mode_counts.items():
            print(f"  {mode}: {count} evaluations")


if __name__ == "__main__":
    # Run POC with 2 models and 3 questions
    asyncio.run(run_benchmark_poc(num_models=2, num_questions=3))



================================================
FILE: src/models.py
================================================
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



================================================
FILE: src/reporter.py
================================================
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



================================================
FILE: src/utils.py
================================================
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
        "VectorDatabase",
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
        ("VectorDatabase", "db_path"),
        ("Paths", "output_dir"),
        ("Paths", "cache_dir"),
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

    # Evaluation modes validation
    enable_no_context = get_config_value("Evaluation", "enable_no_context", True, bool)
    enable_raw_files = get_config_value("Evaluation", "enable_raw_files", True, bool)
    enable_vector_db = get_config_value("Evaluation", "enable_vector_db", True, bool)

    if not any([enable_no_context, enable_raw_files, enable_vector_db]):
        issues.append("At least one evaluation mode must be enabled")

    # Warn if vector_db mode is enabled but no database path configured
    if enable_vector_db:
        db_path = get_config_value("VectorDatabase", "db_path", "")
        if not db_path:
            warnings.append("Vector DB mode enabled but no database path configured")

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


def clear_config_cache() -> None:
    """Clear configuration cache for testing or config reloads."""
    global _config_cache
    _config_cache.clear()


def reload_config(config_path: str = "config.cfg") -> None:
    """Force reload configuration from file."""
    clear_config_cache()
    get_config(config_path, force_reload=True)


def get_config_section(section_name: str) -> Dict[str, str]:
    """Get all key-value pairs from a configuration section."""
    config = get_config()

    if not config.has_section(section_name):
        raise ConfigError(f"Configuration section '{section_name}' not found")

    return dict(config[section_name].items())


def has_config_key(section: str, key: str) -> bool:
    """Check if a configuration key exists."""
    try:
        config = get_config()
        return config.has_section(section) and config.has_option(section, key)
    except ConfigError:
        return False


def _convert_config_value(value: str, value_type: type, section: str, key: str) -> Any:
    """Convert configuration value to specified type."""
    try:
        if value_type is bool:
            return value.lower() in ("true", "1", "yes", "on", "enabled")
        elif value_type is int:
            return int(value)
        elif value_type is float:
            return float(value)
        elif value_type is list:
            # Handle comma-separated lists
            if not value:
                return []
            return [item.strip() for item in value.split(",") if item.strip()]
        else:
            return value
    except (ValueError, TypeError) as e:
        raise ConfigError(f"Invalid type conversion for {section}.{key}: {e}")


def _validate_configuration_structure(config: configparser.ConfigParser) -> None:
    """Validate that the configuration has required sections and keys."""
    required_sections = {
        "Models": ["eval_models", "judge_models"],
        "Scoring": ["scoring_method"],
        "VectorDatabase": ["db_path", "embedding_model"],
        "Paths": ["output_dir"],
    }

    warnings = []
    errors = []

    for section_name, required_keys in required_sections.items():
        if not config.has_section(section_name):
            errors.append(f"Missing required section: [{section_name}]")
            continue

        section = config[section_name]
        for key in required_keys:
            if key not in section or not section[key].strip():
                warnings.append(f"Missing or empty key: {section_name}.{key}")

    if errors:
        raise ConfigError(f"Configuration validation failed: {'; '.join(errors)}")

    if warnings:
        logger = logging.getLogger(__name__)
        for warning in warnings:
            logger.warning(f"Configuration warning: {warning}")


def get_enabled_evaluation_modes():
    """
    Get list of enabled evaluation modes from configuration.

    Returns:
        List of EvaluationMode enum values for enabled modes
    """
    # Import here to avoid circular dependency
    from .evaluator import EvaluationMode

    modes = []

    # Check each mode configuration
    if get_config_value("Evaluation", "enable_no_context", True, bool):
        modes.append(EvaluationMode.NO_CONTEXT)

    if get_config_value("Evaluation", "enable_raw_files", True, bool):
        modes.append(EvaluationMode.RAW_FILES)

    if get_config_value("Evaluation", "enable_vector_db", True, bool):
        modes.append(EvaluationMode.VECTOR_DB)

    # Ensure at least one mode is enabled
    if not modes:
        logger = logging.getLogger(__name__)
        logger.warning("No evaluation modes enabled, defaulting to all modes")
        return [
            EvaluationMode.NO_CONTEXT,
            EvaluationMode.RAW_FILES,
            EvaluationMode.VECTOR_DB,
        ]

    return modes



================================================
FILE: src/vectorize.py
================================================
import toml
import json
from pathlib import Path
from docling_core.transforms.chunker import HierarchicalChunker
from docling.document_converter import DocumentConverter

# Example usage:
# ```python
# from src.vectorize import FrameworkProcessor
#
# # Process all frameworks
# processor = FrameworkProcessor()
# all_chunks = processor.process_all_frameworks()
# processor.print_summary(all_chunks)
# processor.save_chunks(all_chunks)
# ```


class FrameworkProcessor:
    """Process cybersecurity frameworks into chunks for analysis."""

    def __init__(self, converter=None, chunker=None):
        """Initialize with document converter and chunker."""
        self.converter = converter or DocumentConverter()
        self.chunker = chunker or HierarchicalChunker()

    def load_metadata(self, framework_path):
        """Load metadata.toml for a framework directory."""
        metadata_path = framework_path / "metadata.toml"
        return toml.load(metadata_path) if metadata_path.exists() else None

    def process_documents(self, framework_path, metad