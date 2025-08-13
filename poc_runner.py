#!/usr/bin/env python3
"""
AI Cyber Policy Benchmark - Proof of Concept Runner

This script demonstrates the complete evaluation pipeline:
1. Load and vectorize cybersecurity framework documents  
2. Run evaluation across multiple models in three modes:
   - No context provided
   - Raw framework files as context
   - Vector database retrieval as context
3. Score results using multiple methods
4. Generate summary reports

Usage:
    python poc_runner.py --models 2 --questions 3 --setup-db
"""

import os
import asyncio
import argparse
import json
from pathlib import Path
from typing import Dict, List
import configparser

# Fix tokenizer parallelism warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

from src.vectorize import FrameworkProcessor
from src.db import VectorDatabase
from src.evaluator import CyberPolicyEvaluator, EvaluationMode
from src.scorer import AccuracyScorer, ScoringMethod
from src.benchmark import get_eval_models

class POCRunner:
    """Complete proof of concept runner for the cyber policy benchmark."""
    
    def __init__(self):
        self.framework_processor = None
        self.vector_db = None
        self.evaluator = None
        self.scorer = None
    
    def setup_vector_database(self) -> None:
        """Set up vector database from existing chunks or create new ones."""
        chunks_dir = Path("output/chunks")
        
        if not chunks_dir.exists() or not list(chunks_dir.glob("*_chunks.json")):
            print("No existing chunks found. Processing frameworks...")
            self.framework_processor = FrameworkProcessor()
            all_chunks = self.framework_processor.process_all_frameworks()
            self.framework_processor.save_chunks(all_chunks)
        
        print("Initializing vector database...")
        self.vector_db = VectorDatabase.initialize_from_chunks()
        
        # Print database stats
        stats = self.vector_db.get_collection_stats()
        print(f"Vector database initialized: {stats['total_chunks']} chunks from {len(stats['frameworks'])} frameworks")
    
    def validate_setup(self) -> bool:
        """Validate that required files and configurations exist."""
        required_files = [
            "data/prompts/cyber_evals.jsonl",
            "data/cyber-frameworks"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not Path(file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"ERROR: Missing required files/directories: {missing_files}")
            return False
        
        # Check if we have API keys for model evaluation
        openrouter_key = config.get('OpenRouter', 'api_key', fallback='').strip()
        openai_key = config.get('OpenAI', 'api_key', fallback='').strip()
        
        if not openrouter_key and not openai_key:
            print("WARNING: No API keys found in config.cfg")
            print("Set api_key in [OpenRouter] or [OpenAI] sections of config.cfg")
            print("You can still run the pipeline, but model queries will fail.")
        
        return True
    
    async def run_evaluation(self, num_models: int = 2, num_questions: int = 3) -> Dict:
        """Run the complete evaluation pipeline."""
        print(f"\n=== STARTING EVALUATION PIPELINE ===")
        print(f"Models: {num_models}, Questions: {num_questions}")
        
        # Initialize components
        self.evaluator = CyberPolicyEvaluator(vector_db=self.vector_db)
        
        # Get models and questions
        try:
            all_models = get_eval_models()
            models = all_models[:num_models]
        except Exception as e:
            print(f"Error getting models: {e}")
            # Fallback to test models
            models = ["gpt-3.5-turbo", "anthropic/claude-haiku-3.5"][:num_models]
        
        questions = self.evaluator.load_evaluation_questions()[:num_questions]
        
        # Define evaluation modes
        modes = [EvaluationMode.NO_CONTEXT, EvaluationMode.RAW_FILES, EvaluationMode.VECTOR_DB]
        
        print(f"Testing models: {models}")
        print(f"Evaluation modes: {[m.value for m in modes]}")
        
        # Run evaluation
        evaluation_results = await self.evaluator.run_evaluation(models, questions, modes)
        
        return evaluation_results
    
    async def score_results(self, evaluation_results: Dict) -> Dict:
        """Score the evaluation results."""
        print(f"\n=== SCORING RESULTS ===")
        
        self.scorer = AccuracyScorer()
        scoring_methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]
        
        scored_results = await self.scorer.score_evaluation_results(
            evaluation_results, scoring_methods
        )
        
        return scored_results
    
    def generate_summary_report(self, scored_results: Dict) -> Dict:
        """Generate summary statistics and report."""
        print(f"\n=== GENERATING SUMMARY REPORT ===")
        
        summary = {
            "total_models": len(scored_results),
            "models": {},
            "mode_performance": {},
            "overall_stats": {}
        }
        
        all_scores = []
        mode_scores = {mode.value: [] for mode in EvaluationMode}
        
        for model_name, results in scored_results.items():
            model_scores = []
            model_by_mode = {mode.value: [] for mode in EvaluationMode}
            
            for result in results:
                score = result.get('accuracy_score', 0.0)
                model_scores.append(score)
                all_scores.append(score)
                
                mode = result.get('evaluation_mode', 'unknown')
                if mode in model_by_mode:
                    model_by_mode[mode].append(score)
                    mode_scores[mode].append(score)
            
            summary["models"][model_name] = {
                "total_evaluations": len(results),
                "average_score": sum(model_scores) / len(model_scores) if model_scores else 0.0,
                "score_by_mode": {
                    mode: sum(scores) / len(scores) if scores else 0.0 
                    for mode, scores in model_by_mode.items()
                }
            }
        
        # Overall statistics
        summary["overall_stats"] = {
            "average_score": sum(all_scores) / len(all_scores) if all_scores else 0.0,
            "total_evaluations": len(all_scores)
        }
        
        # Mode performance
        summary["mode_performance"] = {
            mode: sum(scores) / len(scores) if scores else 0.0
            for mode, scores in mode_scores.items()
        }
        
        return summary
    
    def save_results(self, scored_results: Dict, summary: Dict, output_dir: str = None) -> None:
        """Save all results to files."""
        if output_dir is None:
            output_dir = config.get('Cyber Policy Benchmark', 'output_dir', fallback='./experiment_results')
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        with open(output_path / "poc_detailed_results.json", 'w') as f:
            json.dump(scored_results, f, indent=2, ensure_ascii=False)
        
        # Save summary
        with open(output_path / "poc_summary.json", 'w') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"Results saved to {output_path}/")
    
    def print_summary_report(self, summary: Dict) -> None:
        """Print formatted summary report."""
        print(f"\n{'='*60}")
        print(f"PROOF OF CONCEPT EVALUATION SUMMARY")
        print(f"{'='*60}")
        
        print(f"\nOverall Performance:")
        print(f"  Total Evaluations: {summary['overall_stats']['total_evaluations']}")
        print(f"  Average Score: {summary['overall_stats']['average_score']:.3f}")
        
        print(f"\nPerformance by Mode:")
        for mode, score in summary['mode_performance'].items():
            print(f"  {mode.replace('_', ' ').title()}: {score:.3f}")
        
        print(f"\nPerformance by Model:")
        for model_name, stats in summary['models'].items():
            print(f"  {model_name}:")
            print(f"    Average: {stats['average_score']:.3f}")
            for mode, score in stats['score_by_mode'].items():
                if score > 0:  # Only show modes that were tested
                    print(f"    {mode.replace('_', ' ').title()}: {score:.3f}")
    
    async def run_complete_poc(self, args) -> None:
        """Run the complete proof of concept pipeline."""
        print("=== AI CYBER POLICY BENCHMARK - PROOF OF CONCEPT ===")
        
        # Validate setup
        if not self.validate_setup():
            return
        
        # Set up vector database if requested
        if args.setup_db:
            self.setup_vector_database()
        elif Path("vector_db").exists():
            print("Using existing vector database...")
            self.vector_db = VectorDatabase()
            stats = self.vector_db.get_collection_stats()
            print(f"Loaded vector database: {stats['total_chunks']} chunks")
        else:
            print("No vector database found. Use --setup-db to create one.")
            return
        
        try:
            # Run evaluation
            evaluation_results = await self.run_evaluation(args.models, args.questions)
            
            # Score results
            scored_results = await self.score_results(evaluation_results)
            
            # Generate summary
            summary = self.generate_summary_report(scored_results)
            
            # Save and print results
            self.save_results(scored_results, summary)
            self.print_summary_report(summary)
            
            print(f"\n=== PROOF OF CONCEPT COMPLETE ===")
            
        except Exception as e:
            print(f"ERROR during evaluation: {e}")
            import traceback
            traceback.print_exc()

def main():
    parser = argparse.ArgumentParser(description="AI Cyber Policy Benchmark - Proof of Concept")
    parser.add_argument("--models", type=int, default=2, help="Number of models to evaluate (default: 2)")
    parser.add_argument("--questions", type=int, default=3, help="Number of questions to test (default: 3)")
    parser.add_argument("--setup-db", action="store_true", help="Set up vector database from framework chunks")
    
    args = parser.parse_args()
    
    runner = POCRunner()
    asyncio.run(runner.run_complete_poc(args))

if __name__ == "__main__":
    main()