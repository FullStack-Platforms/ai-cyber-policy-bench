import asyncio
import json
import openai
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import time
from dataclasses import dataclass
from enum import Enum

from .db import VectorDatabase
from .benchmark import get_eval_models, client

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
    
    def __init__(self, vector_db: Optional[VectorDatabase] = None):
        """Initialize evaluator with optional vector database."""
        self.vector_db = vector_db
        self.client = client
        
    def load_evaluation_questions(self, questions_file: str = "data/prompts/cyber_evals.jsonl") -> List[Dict]:
        """Load evaluation questions from JSONL file."""
        questions = []
        with open(questions_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    questions.append(json.loads(line))
        return questions
    
    def load_raw_framework_files(self, frameworks_dir: str = "data/cyber-frameworks") -> Dict[str, str]:
        """Load raw framework markdown files for context."""
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
                    with open(md_file, 'r', encoding='utf-8') as f:
                        combined_content.append(f"## {md_file.name}\n{f.read()}")
                framework_content[framework_dir.name] = "\n\n".join(combined_content)
        
        return framework_content
    
    async def query_model(self, model_name: str, prompt: str, max_retries: int = 3) -> str:
        """Query a model with the given prompt."""
        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1000,
                    temperature=0.1
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                if attempt == max_retries - 1:
                    return f"Error: {str(e)}"
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    def create_prompt(self, question: str, context: Optional[str] = None) -> str:
        """Create evaluation prompt with optional context."""
        if context:
            return f"""Context:
{context}

Question: {question}

Please provide a precise answer based on the context provided. Be specific about which requirements or controls are relevant."""
        else:
            return f"Question: {question}\n\nPlease provide a precise answer based on your knowledge of cybersecurity frameworks and compliance requirements."
    
    def get_vector_context(self, question: str, n_results: int = 3) -> Optional[str]:
        """Retrieve relevant context from vector database."""
        if not self.vector_db:
            return None
            
        results = self.vector_db.search(question, n_results=n_results)
        if not results:
            return None
            
        context_parts = []
        for result in results:
            fw_name = result['metadata']['framework_name']
            context_parts.append(f"[{fw_name}] {result['text']}")
        
        return "\n\n".join(context_parts)
    
    def get_raw_file_context(self, question: str, framework_files: Dict[str, str]) -> Optional[str]:
        """Get relevant raw file context by searching for framework mentions in question."""
        # Simple heuristic: look for framework keywords in the question
        question_lower = question.lower()
        relevant_frameworks = []
        
        framework_keywords = {
            'soc': 'soc2-trust-services',
            'soc 2': 'soc2-trust-services',
            'cmmc': 'cmmc',
            'nist': 'nist-csf',
            'pci': 'pci-dss',
            'hipaa': 'hipaa',
            'gdpr': 'gdpr',
            'fedramp': 'fedramp'
        }
        
        for keyword, framework_key in framework_keywords.items():
            if keyword in question_lower and framework_key in framework_files:
                relevant_frameworks.append(framework_files[framework_key])
        
        if relevant_frameworks:
            return "\n\n".join(relevant_frameworks)
        
        # If no specific framework found, return first available (fallback)
        if framework_files:
            return list(framework_files.values())[0]
        
        return None
    
    async def evaluate_single_question(self, question_data: Dict, model_name: str, 
                                     evaluation_mode: EvaluationMode, 
                                     framework_files: Optional[Dict[str, str]] = None) -> EvaluationResult:
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
        model_response = await self.query_model(model_name, prompt)
        
        return EvaluationResult(
            question=question,
            ideal_answer=ideal_answer,
            model_response=model_response,
            model_name=model_name,
            evaluation_mode=evaluation_mode,
            context_provided=context,
            timestamp=datetime.now().isoformat()
        )
    
    async def run_evaluation(self, models: List[str], questions: List[Dict], 
                           modes: List[EvaluationMode], 
                           output_dir: str = "experiment_results") -> Dict[str, List[EvaluationResult]]:
        """Run complete evaluation across models, questions, and modes."""
        results = {}
        framework_files = None
        
        # Load framework files if needed
        if EvaluationMode.RAW_FILES in modes:
            framework_files = self.load_raw_framework_files()
        
        # Initialize vector DB if needed
        if EvaluationMode.VECTOR_DB in modes and not self.vector_db:
            print("Initializing vector database...")
            self.vector_db = VectorDatabase.initialize_from_chunks()
        
        total_evaluations = len(models) * len(questions) * len(modes)
        completed = 0
        
        print(f"Starting evaluation: {len(models)} models × {len(questions)} questions × {len(modes)} modes = {total_evaluations} total evaluations")
        
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
        
        # Save results
        self.save_results(results, output_dir)
        print(f"\nEvaluation complete! Results saved to {output_dir}")
        
        return results
    
    def save_results(self, results: Dict[str, List[EvaluationResult]], output_dir: str) -> None:
        """Save evaluation results to files."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Save detailed results
        detailed_results = {}
        for model_name, model_results in results.items():
            detailed_results[model_name] = [
                {
                    'question': r.question,
                    'ideal_answer': r.ideal_answer,
                    'model_response': r.model_response,
                    'evaluation_mode': r.evaluation_mode.value,
                    'context_provided': r.context_provided,
                    'accuracy_score': r.accuracy_score,
                    'timestamp': r.timestamp
                }
                for r in model_results
            ]
        
        with open(output_path / "detailed_results.json", 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2, ensure_ascii=False)
        
        print(f"Detailed results saved to {output_path / 'detailed_results.json'}")

async def run_benchmark_poc(num_models: int = 3, num_questions: int = 5):
    """Run a proof of concept benchmark with a subset of models and questions."""
    print("=== AI Cyber Policy Benchmark - Proof of Concept ===")
    
    # Initialize evaluator
    evaluator = CyberPolicyEvaluator()
    
    # Get subset of models and questions
    all_models = get_eval_models()
    models = all_models[:num_models]
    
    questions = evaluator.load_evaluation_questions()
    questions = questions[:num_questions]
    
    # Define evaluation modes
    modes = [EvaluationMode.NO_CONTEXT, EvaluationMode.RAW_FILES, EvaluationMode.VECTOR_DB]
    
    print(f"Testing {len(models)} models with {len(questions)} questions in {len(modes)} modes")
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