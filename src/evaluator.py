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
        
        # Initialize semaphore for rate limiting parallel requests
        parallel_requests = get_config_value("Evaluation", "parallel_requests", 5, int)
        self.semaphore = asyncio.Semaphore(parallel_requests)
        
        # Initialize async lock for progress tracking
        self.progress_lock = asyncio.Lock()

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
        async with self.semaphore:  # Rate limiting with semaphore
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

    async def _evaluate_single_question_with_progress(
        self,
        question_data: Dict,
        model_name: str,
        evaluation_mode: EvaluationMode,
        framework_files: Optional[Dict[str, str]] = None,
        total_evaluations: int = 0,
    ) -> EvaluationResult:
        """Evaluate a single question with async-safe progress tracking."""
        # Initialize completed counter as class attribute if not exists
        if not hasattr(self, '_completed_evaluations'):
            self._completed_evaluations = 0
        
        try:
            # Perform the actual evaluation
            result = await self.evaluate_single_question(
                question_data, model_name, evaluation_mode, framework_files
            )
            
            # Update progress with thread safety
            async with self.progress_lock:
                self._completed_evaluations += 1
                completed = self._completed_evaluations
                
                # Print progress every 10 completions or at significant milestones
                if completed % 10 == 0 or completed == total_evaluations:
                    progress_percent = (completed / total_evaluations * 100) if total_evaluations > 0 else 0
                    print(f"Progress: {completed}/{total_evaluations} ({progress_percent:.1f}%) - Latest: {model_name}/{evaluation_mode.value}")
            
            return result
            
        except Exception as e:
            # Update progress even for failed evaluations
            async with self.progress_lock:
                self._completed_evaluations += 1
                completed = self._completed_evaluations
                print(f"Failed evaluation {completed}/{total_evaluations}: {model_name}/{evaluation_mode.value} - {str(e)}")
            
            raise

    async def run_evaluation(
        self,
        models: List[str],
        questions: List[Dict],
        modes: List[EvaluationMode],
        output_dir: str = "experiment_results",
    ) -> Dict[str, List[Dict]]:
        """Run complete evaluation across models, questions, and modes with parallel execution."""
        framework_files = None

        # Load framework files if needed
        if EvaluationMode.RAW_FILES in modes:
            framework_files = self.load_raw_framework_files()

        # Initialize vector DB if needed
        if EvaluationMode.VECTOR_DB in modes and not self.vector_db:
            print("Initializing vector database with multi-collection support...")
            self.vector_db = VectorDatabase.initialize_from_chunks()

        total_evaluations = len(models) * len(questions) * len(modes)
        
        # Initialize progress tracking
        self._completed_evaluations = 0
        
        print(
            f"Starting parallel evaluation: {len(models)} models × {len(questions)} questions × {len(modes)} modes = {total_evaluations} total evaluations"
        )
        print(f"Parallel requests limit: {self.semaphore._value}")

        # Create all evaluation tasks
        tasks = []
        task_metadata = []  # Track model/question/mode for each task
        
        for model_name in models:
            for mode in modes:
                for question_data in questions:
                    task = self._evaluate_single_question_with_progress(
                        question_data, model_name, mode, framework_files, total_evaluations
                    )
                    tasks.append(task)
                    task_metadata.append((model_name, mode, question_data["input"]))

        print(f"Created {len(tasks)} parallel evaluation tasks")

        # Execute all tasks in parallel with semaphore rate limiting
        try:
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            print(f"Error in parallel execution: {e}")
            raise

        # Group results by model
        results = {}
        for i, result in enumerate(all_results):
            model_name, mode, question = task_metadata[i]
            
            if model_name not in results:
                results[model_name] = []
            
            # Handle exceptions from individual tasks
            if isinstance(result, Exception):
                print(f"Task failed for {model_name}/{mode.value}: {result}")
                # Create a failure result
                failure_result = EvaluationResult(
                    question=question,
                    ideal_answer="N/A",
                    model_response=f"TASK_FAILURE: {str(result)}",
                    model_name=model_name,
                    evaluation_mode=mode,
                    context_provided=None,
                    timestamp=datetime.now().isoformat(),
                )
                results[model_name].append(failure_result)
            else:
                results[model_name].append(result)

        # Print completion summary
        print(f"\nParallel evaluation completed!")
        for model_name, model_results in results.items():
            successful = len([r for r in model_results if not r.model_response.startswith("TASK_FAILURE")])
            total = len(model_results)
            print(f"  {model_name}: {successful}/{total} successful evaluations")

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
        print(f"Results saved to {output_dir}")

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
