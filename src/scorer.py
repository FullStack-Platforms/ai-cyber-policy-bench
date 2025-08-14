import asyncio
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import re
import configparser

from .benchmark import client

# Load configuration
config = configparser.ConfigParser()
config.read("config.cfg")


class ScoringMethod(Enum):
    EXACT_MATCH = "exact_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    LLM_JUDGE = "llm_judge"
    CONTROL_REFERENCE = "control_reference"


@dataclass
class ScoringResult:
    accuracy_score: float
    method: ScoringMethod
    explanation: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class AccuracyScorer:
    """Scorer for evaluating model responses against ground truth answers."""

    def __init__(self, judge_model: str = None):
        """Initialize scorer with judge model."""
        if judge_model is None:
            # Try to get from main config first, then from Models section default
            judge_model = config.get(
                "Cyber Policy Benchmark",
                "judge_model",
                fallback=None,
            )
            if not judge_model:
                # Use first model from default judge models in config
                default_judges = config.get(
                    "Models", "default_judge_models", fallback=""
                )
                if default_judges:
                    judge_model = default_judges.split(",")[0].strip()
                else:
                    judge_model = "anthropic/claude-sonnet-4"
        self.judge_model = judge_model
        self.client = client

    def exact_match_score(
        self, model_response: str, ideal_answer: str
    ) -> ScoringResult:
        """Simple exact match scoring (case-insensitive)."""
        model_clean = model_response.strip().lower()
        ideal_clean = ideal_answer.strip().lower()

        score = 1.0 if model_clean == ideal_clean else 0.0

        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.EXACT_MATCH,
            details={"model_clean": model_clean, "ideal_clean": ideal_clean},
        )

    def extract_control_references(self, text: str) -> List[str]:
        """Extract control references like CC6.1, AC.L1-b.1.i, etc."""
        # Pattern for various control reference formats
        patterns = [
            r"\b[A-Z]{2,4}\d+\.\d+\b",  # SOC 2: CC6.1, A1.3
            r"\b[A-Z]{2,4}\.L\d+-[a-z]\.\d+\.[a-z]+\b",  # CMMC: AC.L1-b.1.i
            r"\bNIST\.SP\.\d+-\d+\b",  # NIST: NIST.SP.800-53
            r"\b[A-Z]{2,4}-\d+\b",  # Generic: SI-1, AC-2
        ]

        controls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            controls.extend(matches)

        return list(set(controls))  # Remove duplicates

    def control_reference_score(
        self, model_response: str, ideal_answer: str
    ) -> ScoringResult:
        """Score based on overlap of control references."""
        model_controls = set(self.extract_control_references(model_response))
        ideal_controls = set(self.extract_control_references(ideal_answer))

        if not ideal_controls:
            # No controls in ideal answer, check if model incorrectly identified controls
            score = 1.0 if not model_controls else 0.5
            explanation = "No control references expected"
        else:
            # Calculate overlap
            intersection = model_controls & ideal_controls
            union = model_controls | ideal_controls

            # Jaccard similarity with penalty for false positives
            if union:
                precision = (
                    len(intersection) / len(model_controls) if model_controls else 0
                )
                recall = (
                    len(intersection) / len(ideal_controls) if ideal_controls else 0
                )
                f1_score = (
                    2 * precision * recall / (precision + recall)
                    if (precision + recall) > 0
                    else 0
                )
                score = f1_score
            else:
                score = 1.0  # Both empty

            explanation = (
                f"Model controls: {model_controls}, Ideal controls: {ideal_controls}"
            )

        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.CONTROL_REFERENCE,
            explanation=explanation,
            details={
                "model_controls": list(model_controls),
                "ideal_controls": list(ideal_controls),
                "intersection": list(model_controls & ideal_controls),
            },
        )

    async def llm_judge_score(
        self,
        question: str,
        model_response: str,
        ideal_answer: str,
        max_retries: int = 3,
    ) -> ScoringResult:
        """Use LLM as a judge to score the response."""

        judge_prompt = f"""You are evaluating the accuracy of a model's response to a cybersecurity compliance question.

Question: {question}

Model Response: {model_response}

Ground Truth Answer: {ideal_answer}

Please evaluate the model's response on the following criteria:
1. Correctness: Does the model identify the correct compliance requirement(s)?
2. Completeness: Does the model address all relevant aspects mentioned in the ground truth?
3. Specificity: Does the model provide specific control/requirement references when appropriate?

Rate the overall accuracy on a scale from 0.0 to 1.0, where:
- 1.0 = Perfect match with ground truth
- 0.8-0.9 = Minor differences but substantially correct
- 0.6-0.7 = Partially correct but missing key elements
- 0.4-0.5 = Some relevant information but significant errors
- 0.2-0.3 = Minimal relevance to the correct answer
- 0.0 = Completely incorrect or irrelevant

Respond with JSON in this format:
{{"score": 0.8, "explanation": "Brief explanation of the scoring rationale"}}"""

        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    self.client.chat.completions.create,
                    model=self.judge_model,
                    messages=[{"role": "user", "content": judge_prompt}],
                    max_tokens=300,
                    temperature=0.1,
                )

                judge_response = response.choices[0].message.content.strip()

                # Parse JSON response
                try:
                    parsed = json.loads(judge_response)
                    score = float(parsed.get("score", 0.0))
                    explanation = parsed.get("explanation", "No explanation provided")

                    return ScoringResult(
                        accuracy_score=score,
                        method=ScoringMethod.LLM_JUDGE,
                        explanation=explanation,
                        details={"judge_response": judge_response},
                    )
                except json.JSONDecodeError:
                    # Try to extract score from text
                    import re

                    score_match = re.search(
                        r'score["\']?\s*:\s*([0-9.]+)', judge_response, re.IGNORECASE
                    )
                    if score_match:
                        score = float(score_match.group(1))
                        return ScoringResult(
                            accuracy_score=score,
                            method=ScoringMethod.LLM_JUDGE,
                            explanation="Extracted from non-JSON response",
                            details={"judge_response": judge_response},
                        )
                    else:
                        raise ValueError("Could not parse score from response")

            except Exception as e:
                if attempt == max_retries - 1:
                    return ScoringResult(
                        accuracy_score=0.0,
                        method=ScoringMethod.LLM_JUDGE,
                        explanation=f"Error in LLM judge: {str(e)}",
                        details={"error": str(e)},
                    )
                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def score_response(
        self,
        question: str,
        model_response: str,
        ideal_answer: str,
        methods: List[ScoringMethod] = None,
    ) -> Dict[ScoringMethod, ScoringResult]:
        """Score a model response using multiple methods."""
        if methods is None:
            methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]

        results = {}

        for method in methods:
            if method == ScoringMethod.EXACT_MATCH:
                results[method] = self.exact_match_score(model_response, ideal_answer)
            elif method == ScoringMethod.CONTROL_REFERENCE:
                results[method] = self.control_reference_score(
                    model_response, ideal_answer
                )
            elif method == ScoringMethod.LLM_JUDGE:
                results[method] = await self.llm_judge_score(
                    question, model_response, ideal_answer
                )

        return results

    async def score_evaluation_results(
        self,
        evaluation_results: Dict[str, List],
        scoring_methods: List[ScoringMethod] = None,
    ) -> Dict[str, List]:
        """Score all evaluation results."""
        if scoring_methods is None:
            scoring_methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]

        scored_results = {}

        for model_name, results in evaluation_results.items():
            print(f"Scoring results for {model_name}...")
            scored_model_results = []

            for i, result in enumerate(results):
                try:
                    # Score the response
                    scores = await self.score_response(
                        result["question"],
                        result["model_response"],
                        result["ideal_answer"],
                        scoring_methods,
                    )

                    # Add scores to result (create a copy of the dict)
                    result_with_scores = dict(result)
                    result_with_scores["scores"] = {
                        method.value: {
                            "score": scoring_result.accuracy_score,
                            "explanation": scoring_result.explanation,
                            "details": scoring_result.details,
                        }
                        for method, scoring_result in scores.items()
                    }

                    # Set primary accuracy score (use LLM judge if available, otherwise control reference)
                    if ScoringMethod.LLM_JUDGE in scores:
                        result_with_scores["accuracy_score"] = scores[
                            ScoringMethod.LLM_JUDGE
                        ].accuracy_score
                    elif ScoringMethod.CONTROL_REFERENCE in scores:
                        result_with_scores["accuracy_score"] = scores[
                            ScoringMethod.CONTROL_REFERENCE
                        ].accuracy_score
                    else:
                        result_with_scores["accuracy_score"] = 0.0

                    scored_model_results.append(result_with_scores)

                    if (i + 1) % 5 == 0:
                        print(f"  Scored {i + 1}/{len(results)} results")

                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.2)

                except Exception as e:
                    print(f"  Error scoring result {i + 1}: {e}")
                    # Add result with zero score (create a copy of the dict)
                    result_with_scores = dict(result)
                    result_with_scores["accuracy_score"] = 0.0
                    result_with_scores["scores"] = {"error": str(e)}
                    scored_model_results.append(result_with_scores)

            scored_results[model_name] = scored_model_results
            print(f"  Completed scoring for {model_name}")

        return scored_results


class TwoJudgeScorer:
    """Dual judge scorer with graceful fallback handling."""

    def __init__(
        self,
        judge_model_1: str = None,
        judge_model_2: str = None,
        judge_weight_1: float = 0.5,
        judge_weight_2: float = 0.5,
    ):
        """Initialize dual judge scorer."""
        # Load judge models from config with fallbacks
        self.judge_model_1 = judge_model_1 or config.get(
            "Scoring",
            "judge_model_1",
            fallback=self._get_fallback_judge_model(1),
        )
        self.judge_model_2 = judge_model_2 or config.get(
            "Scoring", "judge_model_2", fallback=self._get_fallback_judge_model(2)
        )

        # Load weights from config
        self.judge_weight_1 = float(
            config.get("Scoring", "judge_weight_1", fallback=str(judge_weight_1))
        )
        self.judge_weight_2 = float(
            config.get("Scoring", "judge_weight_2", fallback=str(judge_weight_2))
        )

        # Normalize weights
        total_weight = self.judge_weight_1 + self.judge_weight_2
        if total_weight > 0:
            self.judge_weight_1 /= total_weight
            self.judge_weight_2 /= total_weight
        else:
            self.judge_weight_1 = self.judge_weight_2 = 0.5

        self.client = client
        self.single_scorer_1 = AccuracyScorer(self.judge_model_1)
        self.single_scorer_2 = AccuracyScorer(self.judge_model_2)

        # Statistics tracking
        self.judge_1_success_count = 0
        self.judge_2_success_count = 0
        self.judge_1_failure_count = 0
        self.judge_2_failure_count = 0
        self.dual_success_count = 0
        self.fallback_used_count = 0

    def _get_fallback_judge_model(self, judge_num: int) -> str:
        """Get fallback judge model from centralized config."""
        # Try to get from default judge models in config
        default_judges = config.get("Models", "default_judge_models", fallback="")
        if default_judges:
            judges_list = [
                model.strip() for model in default_judges.split(",") if model.strip()
            ]
            if judge_num == 1 and len(judges_list) > 0:
                return judges_list[0]
            elif judge_num == 2 and len(judges_list) > 1:
                return judges_list[1]
            elif judge_num == 2 and len(judges_list) > 0:
                return judges_list[0]  # Use same as judge 1 if only one available

        # Final hardcoded fallbacks
        if judge_num == 1:
            # Try main config first, then hardcoded fallback
            return config.get(
                "Cyber Policy Benchmark",
                "judge_model",
                fallback="anthropic/claude-sonnet-4",
            )
        else:
            return "openai/gpt-4o"

    def exact_match_score(
        self, model_response: str, ideal_answer: str
    ) -> ScoringResult:
        """Simple exact match scoring (case-insensitive)."""
        return self.single_scorer_1.exact_match_score(model_response, ideal_answer)

    def control_reference_score(
        self, model_response: str, ideal_answer: str
    ) -> ScoringResult:
        """Score based on overlap of control references."""
        return self.single_scorer_1.control_reference_score(
            model_response, ideal_answer
        )

    async def dual_llm_judge_score(
        self,
        question: str,
        model_response: str,
        ideal_answer: str,
        max_retries: int = 2,
    ) -> ScoringResult:
        """Use two LLMs as judges with graceful fallback handling."""

        # Try both judges in parallel
        judge_1_task = asyncio.create_task(
            self._safe_judge_score(
                self.single_scorer_1,
                question,
                model_response,
                ideal_answer,
                "Judge 1",
                max_retries,
            )
        )
        judge_2_task = asyncio.create_task(
            self._safe_judge_score(
                self.single_scorer_2,
                question,
                model_response,
                ideal_answer,
                "Judge 2",
                max_retries,
            )
        )

        # Wait for both to complete
        judge_1_result, judge_2_result = await asyncio.gather(
            judge_1_task, judge_2_task, return_exceptions=True
        )

        # Handle results and exceptions
        judge_1_score = None
        judge_2_score = None

        if (
            isinstance(judge_1_result, ScoringResult)
            and judge_1_result.accuracy_score > 0
        ):
            judge_1_score = judge_1_result.accuracy_score
            self.judge_1_success_count += 1
        else:
            self.judge_1_failure_count += 1
            if isinstance(judge_1_result, Exception):
                print(f"Judge 1 ({self.judge_model_1}) failed: {judge_1_result}")
            elif isinstance(judge_1_result, ScoringResult):
                print(
                    f"Judge 1 ({self.judge_model_1}) returned score 0: {judge_1_result.explanation}"
                )

        if (
            isinstance(judge_2_result, ScoringResult)
            and judge_2_result.accuracy_score > 0
        ):
            judge_2_score = judge_2_result.accuracy_score
            self.judge_2_success_count += 1
        else:
            self.judge_2_failure_count += 1
            if isinstance(judge_2_result, Exception):
                print(f"Judge 2 ({self.judge_model_2}) failed: {judge_2_result}")
            elif isinstance(judge_2_result, ScoringResult):
                print(
                    f"Judge 2 ({self.judge_model_2}) returned score 0: {judge_2_result.explanation}"
                )

        # Determine final score using graceful fallback logic
        final_score, explanation, scoring_details = self._compute_final_score(
            judge_1_score, judge_2_score, judge_1_result, judge_2_result
        )

        return ScoringResult(
            accuracy_score=final_score,
            method=ScoringMethod.LLM_JUDGE,
            explanation=explanation,
            details=scoring_details,
        )

    async def _safe_judge_score(
        self,
        scorer: AccuracyScorer,
        question: str,
        model_response: str,
        ideal_answer: str,
        judge_name: str,
        max_retries: int,
    ) -> ScoringResult:
        """Safely call a judge scorer with error handling."""
        try:
            # Truncate inputs if they're too long to prevent context window issues
            max_input_length = 8000  # Conservative limit
            if len(question + model_response + ideal_answer) > max_input_length:
                # Truncate model response first, then question if needed
                available_length = max_input_length - len(ideal_answer) - 100  # Buffer
                if len(question) + len(model_response) > available_length:
                    if len(model_response) > available_length // 2:
                        model_response = (
                            model_response[: available_length // 2] + "...[truncated]"
                        )
                    if len(question) > available_length // 2:
                        question = question[: available_length // 2] + "...[truncated]"

            return await scorer.llm_judge_score(
                question, model_response, ideal_answer, max_retries
            )
        except Exception as e:
            print(f"{judge_name} scoring failed: {e}")
            return ScoringResult(
                accuracy_score=0.0,
                method=ScoringMethod.LLM_JUDGE,
                explanation=f"{judge_name} failed: {str(e)}",
                details={"error": str(e), "judge": judge_name},
            )

    def _compute_final_score(
        self,
        judge_1_score: Optional[float],
        judge_2_score: Optional[float],
        judge_1_result,
        judge_2_result,
    ) -> tuple:
        """Compute final score with fallback logic."""

        if judge_1_score is not None and judge_2_score is not None:
            # Both judges succeeded - use weighted average
            final_score = (
                judge_1_score * self.judge_weight_1
                + judge_2_score * self.judge_weight_2
            )
            self.dual_success_count += 1

            # Check for significant discrepancy
            discrepancy = abs(judge_1_score - judge_2_score)
            explanation = (
                f"Dual judge average: {final_score:.3f} "
                f"(Judge 1: {judge_1_score:.3f}, Judge 2: {judge_2_score:.3f})"
            )
            if discrepancy > 0.3:
                explanation += f" [HIGH DISCREPANCY: {discrepancy:.3f}]"

            scoring_details = {
                "judge_1_score": judge_1_score,
                "judge_2_score": judge_2_score,
                "discrepancy": discrepancy,
                "weight_1": self.judge_weight_1,
                "weight_2": self.judge_weight_2,
                "both_judges_succeeded": True,
            }

        elif judge_1_score is not None:
            # Only judge 1 succeeded
            final_score = judge_1_score
            self.fallback_used_count += 1
            explanation = f"Judge 1 only: {final_score:.3f} (Judge 2 failed)"
            scoring_details = {
                "judge_1_score": judge_1_score,
                "judge_2_score": None,
                "fallback_to": "judge_1",
                "judge_2_error": getattr(
                    judge_2_result, "explanation", "Unknown error"
                ),
            }

        elif judge_2_score is not None:
            # Only judge 2 succeeded
            final_score = judge_2_score
            self.fallback_used_count += 1
            explanation = f"Judge 2 only: {final_score:.3f} (Judge 1 failed)"
            scoring_details = {
                "judge_1_score": None,
                "judge_2_score": judge_2_score,
                "fallback_to": "judge_2",
                "judge_1_error": getattr(
                    judge_1_result, "explanation", "Unknown error"
                ),
            }

        else:
            # Both judges failed - return 0
            final_score = 0.0
            explanation = "Both judges failed"
            scoring_details = {
                "judge_1_score": None,
                "judge_2_score": None,
                "both_judges_failed": True,
                "judge_1_error": getattr(
                    judge_1_result, "explanation", "Unknown error"
                ),
                "judge_2_error": getattr(
                    judge_2_result, "explanation", "Unknown error"
                ),
            }

        return final_score, explanation, scoring_details

    async def score_response(
        self,
        question: str,
        model_response: str,
        ideal_answer: str,
        methods: List[ScoringMethod] = None,
    ) -> Dict[ScoringMethod, ScoringResult]:
        """Score a model response using multiple methods with dual judge support."""
        if methods is None:
            methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]

        results = {}

        for method in methods:
            if method == ScoringMethod.EXACT_MATCH:
                results[method] = self.exact_match_score(model_response, ideal_answer)
            elif method == ScoringMethod.CONTROL_REFERENCE:
                results[method] = self.control_reference_score(
                    model_response, ideal_answer
                )
            elif method == ScoringMethod.LLM_JUDGE:
                results[method] = await self.dual_llm_judge_score(
                    question, model_response, ideal_answer
                )

        return results

    async def score_evaluation_results(
        self,
        evaluation_results: Dict[str, List],
        scoring_methods: List[ScoringMethod] = None,
    ) -> Dict[str, List]:
        """Score all evaluation results with dual judge system."""
        if scoring_methods is None:
            scoring_methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]

        scored_results = {}

        for model_name, results in evaluation_results.items():
            print(f"Scoring results for {model_name} using dual judge system...")
            scored_model_results = []

            for i, result in enumerate(results):
                try:
                    # Score the response
                    scores = await self.score_response(
                        result["question"],
                        result["model_response"],
                        result["ideal_answer"],
                        scoring_methods,
                    )

                    # Add scores to result
                    result_with_scores = dict(result)
                    result_with_scores["scores"] = {
                        method.value: {
                            "score": scoring_result.accuracy_score,
                            "explanation": scoring_result.explanation,
                            "details": scoring_result.details,
                        }
                        for method, scoring_result in scores.items()
                    }

                    # Set primary accuracy score (use LLM judge if available, otherwise control reference)
                    if ScoringMethod.LLM_JUDGE in scores:
                        result_with_scores["accuracy_score"] = scores[
                            ScoringMethod.LLM_JUDGE
                        ].accuracy_score
                    elif ScoringMethod.CONTROL_REFERENCE in scores:
                        result_with_scores["accuracy_score"] = scores[
                            ScoringMethod.CONTROL_REFERENCE
                        ].accuracy_score
                    else:
                        result_with_scores["accuracy_score"] = 0.0

                    scored_model_results.append(result_with_scores)

                    if (i + 1) % 5 == 0:
                        print(f"  Scored {i + 1}/{len(results)} results")

                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.2)

                except Exception as e:
                    print(f"  Error scoring result {i + 1}: {e}")
                    # Add result with zero score
                    result_with_scores = dict(result)
                    result_with_scores["accuracy_score"] = 0.0
                    result_with_scores["scores"] = {"error": str(e)}
                    scored_model_results.append(result_with_scores)

            scored_results[model_name] = scored_model_results
            print(f"  Completed scoring for {model_name}")
            print(
                f"  Judge statistics: J1 success: {self.judge_1_success_count}, "
                f"J1 failures: {self.judge_1_failure_count}, "
                f"J2 success: {self.judge_2_success_count}, "
                f"J2 failures: {self.judge_2_failure_count}, "
                f"Dual success: {self.dual_success_count}, "
                f"Fallbacks used: {self.fallback_used_count}"
            )

        return scored_results

    def get_judge_statistics(self) -> Dict[str, Any]:
        """Get statistics about judge performance."""
        total_attempts = (
            self.judge_1_success_count
            + self.judge_1_failure_count
            + self.judge_2_success_count
            + self.judge_2_failure_count
        ) // 2

        return {
            "total_scoring_attempts": total_attempts,
            "judge_1": {
                "model": self.judge_model_1,
                "success_count": self.judge_1_success_count,
                "failure_count": self.judge_1_failure_count,
                "success_rate": self.judge_1_success_count
                / max(1, self.judge_1_success_count + self.judge_1_failure_count),
            },
            "judge_2": {
                "model": self.judge_model_2,
                "success_count": self.judge_2_success_count,
                "failure_count": self.judge_2_failure_count,
                "success_rate": self.judge_2_success_count
                / max(1, self.judge_2_success_count + self.judge_2_failure_count),
            },
            "dual_success_count": self.dual_success_count,
            "fallback_used_count": self.fallback_used_count,
            "dual_success_rate": self.dual_success_count / max(1, total_attempts),
        }
