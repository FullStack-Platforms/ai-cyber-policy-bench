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
import json
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
            # Try to use optimized framework processor if available
            try:
                from src.rag_optimizer import OptimizedFrameworkProcessor
                framework_processor = OptimizedFrameworkProcessor()
                logger.info("Using optimized framework processor with smart chunking")
            except ImportError:
                framework_processor = FrameworkProcessor()
                logger.info("Using standard framework processor")
            
            all_chunks = framework_processor.process_all_frameworks()
            framework_processor.save_chunks(all_chunks)

    logger.info("Initializing vector database...")

    with Timer("Vector database initialization"):
        vector_db = VectorDatabase.initialize_from_chunks()
        
        # Use optimized chunks if available
        chunks_path = Path(chunks_dir)
        if chunks_path.exists():
            all_chunks = {}
            for chunk_file in chunks_path.glob("*_chunks.json"):
                with open(chunk_file, "r", encoding="utf-8") as f:
                    framework_data = json.load(f)
                    framework_name = framework_data["metadata"]["framework"]["name"]
                    all_chunks[framework_name] = framework_data
            
            # Use optimized add method if available
            if hasattr(vector_db, 'add_optimized_chunks'):
                vector_db.add_optimized_chunks(all_chunks)
            else:
                vector_db.add_chunks(all_chunks)

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
