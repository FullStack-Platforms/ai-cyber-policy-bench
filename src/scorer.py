import openai
import asyncio
import json
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import configparser

from .benchmark import client

# Load configuration
config = configparser.ConfigParser()
config.read('config.cfg')

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
            judge_model = config.get('Cyber Policy Benchmark', 'judge_model', fallback='anthropic/claude-sonnet-4')
        self.judge_model = judge_model
        self.client = client
    
    def exact_match_score(self, model_response: str, ideal_answer: str) -> ScoringResult:
        """Simple exact match scoring (case-insensitive)."""
        model_clean = model_response.strip().lower()
        ideal_clean = ideal_answer.strip().lower()
        
        score = 1.0 if model_clean == ideal_clean else 0.0
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.EXACT_MATCH,
            details={"model_clean": model_clean, "ideal_clean": ideal_clean}
        )
    
    def extract_control_references(self, text: str) -> List[str]:
        """Extract control references like CC6.1, AC.L1-b.1.i, etc."""
        # Pattern for various control reference formats
        patterns = [
            r'\b[A-Z]{2,4}\d+\.\d+\b',  # SOC 2: CC6.1, A1.3
            r'\b[A-Z]{2,4}\.L\d+-[a-z]\.\d+\.[a-z]+\b',  # CMMC: AC.L1-b.1.i
            r'\bNIST\.SP\.\d+-\d+\b',  # NIST: NIST.SP.800-53
            r'\b[A-Z]{2,4}-\d+\b'  # Generic: SI-1, AC-2
        ]
        
        controls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            controls.extend(matches)
        
        return list(set(controls))  # Remove duplicates
    
    def control_reference_score(self, model_response: str, ideal_answer: str) -> ScoringResult:
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
                precision = len(intersection) / len(model_controls) if model_controls else 0
                recall = len(intersection) / len(ideal_controls) if ideal_controls else 0
                f1_score = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
                score = f1_score
            else:
                score = 1.0  # Both empty
            
            explanation = f"Model controls: {model_controls}, Ideal controls: {ideal_controls}"
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.CONTROL_REFERENCE,
            explanation=explanation,
            details={
                "model_controls": list(model_controls),
                "ideal_controls": list(ideal_controls),
                "intersection": list(model_controls & ideal_controls)
            }
        )
    
    async def llm_judge_score(self, question: str, model_response: str, 
                            ideal_answer: str, max_retries: int = 3) -> ScoringResult:
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
                    temperature=0.1
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
                        details={"judge_response": judge_response}
                    )
                except json.JSONDecodeError:
                    # Try to extract score from text
                    import re
                    score_match = re.search(r'score["\']?\s*:\s*([0-9.]+)', judge_response, re.IGNORECASE)
                    if score_match:
                        score = float(score_match.group(1))
                        return ScoringResult(
                            accuracy_score=score,
                            method=ScoringMethod.LLM_JUDGE,
                            explanation="Extracted from non-JSON response",
                            details={"judge_response": judge_response}
                        )
                    else:
                        raise ValueError("Could not parse score from response")
                        
            except Exception as e:
                if attempt == max_retries - 1:
                    return ScoringResult(
                        accuracy_score=0.0,
                        method=ScoringMethod.LLM_JUDGE,
                        explanation=f"Error in LLM judge: {str(e)}",
                        details={"error": str(e)}
                    )
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
    
    async def score_response(self, question: str, model_response: str, ideal_answer: str,
                           methods: List[ScoringMethod] = None) -> Dict[ScoringMethod, ScoringResult]:
        """Score a model response using multiple methods."""
        if methods is None:
            methods = [ScoringMethod.CONTROL_REFERENCE, ScoringMethod.LLM_JUDGE]
        
        results = {}
        
        for method in methods:
            if method == ScoringMethod.EXACT_MATCH:
                results[method] = self.exact_match_score(model_response, ideal_answer)
            elif method == ScoringMethod.CONTROL_REFERENCE:
                results[method] = self.control_reference_score(model_response, ideal_answer)
            elif method == ScoringMethod.LLM_JUDGE:
                results[method] = await self.llm_judge_score(question, model_response, ideal_answer)
        
        return results
    
    async def score_evaluation_results(self, evaluation_results: Dict[str, List], 
                                     scoring_methods: List[ScoringMethod] = None) -> Dict[str, List]:
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
                        result['question'],
                        result['model_response'],
                        result['ideal_answer'],
                        scoring_methods
                    )
                    
                    # Add scores to result
                    result_with_scores = result.copy()
                    result_with_scores['scores'] = {
                        method.value: {
                            'score': scoring_result.accuracy_score,
                            'explanation': scoring_result.explanation,
                            'details': scoring_result.details
                        }
                        for method, scoring_result in scores.items()
                    }
                    
                    # Set primary accuracy score (use LLM judge if available, otherwise control reference)
                    if ScoringMethod.LLM_JUDGE in scores:
                        result_with_scores['accuracy_score'] = scores[ScoringMethod.LLM_JUDGE].accuracy_score
                    elif ScoringMethod.CONTROL_REFERENCE in scores:
                        result_with_scores['accuracy_score'] = scores[ScoringMethod.CONTROL_REFERENCE].accuracy_score
                    else:
                        result_with_scores['accuracy_score'] = 0.0
                    
                    scored_model_results.append(result_with_scores)
                    
                    if (i + 1) % 5 == 0:
                        print(f"  Scored {i + 1}/{len(results)} results")
                    
                    # Small delay to avoid rate limiting
                    await asyncio.sleep(0.2)
                    
                except Exception as e:
                    print(f"  Error scoring result {i + 1}: {e}")
                    # Add result with zero score
                    result_with_scores = result.copy()
                    result_with_scores['accuracy_score'] = 0.0
                    result_with_scores['scores'] = {'error': str(e)}
                    scored_model_results.append(result_with_scores)
            
            scored_results[model_name] = scored_model_results
            print(f"  Completed scoring for {model_name}")
        
        return scored_results

