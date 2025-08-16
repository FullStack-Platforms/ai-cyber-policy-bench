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
    STRUCTURAL_VALIDATION = "structural_validation"
    CITATION_VERIFICATION = "citation_verification"
    COMPOSITE_POLICY = "composite_policy"
    CONTEXTUAL_RELEVANCE = "contextual_relevance"
    COMPLETENESS = "completeness"


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

    def validate_response(self, model_response: str) -> tuple[bool, str]:
        """
        Validate model response for basic quality and completeness.
        
        Returns:
            tuple: (is_valid, failure_reason)
        """
        if not model_response or not isinstance(model_response, str):
            return False, "Empty or null response"
        
        response_stripped = model_response.strip()
        
        # Check for empty or whitespace-only responses
        if not response_stripped:
            return False, "Empty or whitespace-only response"
        
        # Check for error messages
        if (response_stripped.lower().startswith("error:") or 
            response_stripped.startswith("MODEL_FAILURE:")):
            return False, "Model returned error message"
        
        # Check for extremely short responses (likely incomplete)
        if len(response_stripped) < 10:
            return False, f"Response too short ({len(response_stripped)} chars)"
        
        # Check for non-substantive responses
        non_substantive_patterns = [
            r"^(i don't know|don't know|not sure|no idea|can't help|cannot help)[\.\!]?\s*$",
            r"^(n/a|na|none|null|undefined)[\.\!]?\s*$",
            r"^(sorry|apologize).*(cannot|can't|unable).*$",
            r"^(please|try).*contact.*$",
        ]
        
        for pattern in non_substantive_patterns:
            if re.match(pattern, response_stripped.lower()):
                return False, "Non-substantive response"
        
        # Check for generic/template responses that don't address cybersecurity
        generic_indicators = [
            "thank you for your question",
            "this is an interesting question", 
            "let me help you with that",
            "here are some general guidelines"
        ]
        
        response_lower = response_stripped.lower()
        if any(indicator in response_lower for indicator in generic_indicators):
            # Only flag as invalid if it's ONLY generic content
            words = response_lower.split()
            if len(words) < 50:  # Short and generic
                return False, "Generic template response"
        
        return True, ""

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
        """Extract control references like CC6.1, AC.L1-b.1.i, GDPR Article 32, etc."""
        # Pattern for various control reference formats
        patterns = [
            # SOC 2 Trust Services Criteria
            r"\b[A-Z]{1,2}\d+\.\d+\b",  # CC6.1, A1.3, P8.1
            r"\b[A-Z]{2,4}\d+\.\d+\b",  # Extended version for longer prefixes
            
            # CMMC Controls
            r"\b[A-Z]{2,4}\.L\d+-[a-z]\.\d+\.[a-z]+\b",  # AC.L1-b.1.i
            r"\b[A-Z]{2,4}\.L\d+-[a-z]\.\d+\.[ivx]+\b",  # Alternative roman numerals
            
            # NIST Standards
            r"\bNIST\.SP\.\d+-\d+r?\d*\b",  # NIST.SP.800-53r5, NIST.SP.800-171r3
            r"\bNIST\s+\d+-\d+\b",  # NIST 800-53
            r"\b[A-Z]{2,4}-\d+\b",  # SI-1, AC-2, AU-12
            r"\b[A-Z]{2,4}-\d+\(\d+\)\b",  # AC-2(1), SI-4(5)
            
            # GDPR References
            r"\bArticle\s+\d+\b",  # Article 32, Article 25
            r"\bArt\.\s*\d+\b",  # Art. 32, Art. 25
            r"\bGDPR\s+Article\s+\d+\b",  # GDPR Article 32
            r"\bGDPR\s+Art\.\s*\d+\b",  # GDPR Art. 32
            
            # HIPAA References
            r"\b\d+\.\d+\([a-z]\)\(\d+\)\([a-z]+\)\b",  # 164.312(a)(2)(iv)
            r"\b\d+\.\d+\([a-z]\)\b",  # 164.312(a)
            
            # ISO 27001 References
            r"\bA\.\d+\.\d+\.\d+\b",  # A.8.1.1, A.12.6.1
            r"\bA-\d+\.\d+\.\d+\b",  # Alternative format
            r"\bISO\s+27001\s+A\.\d+\.\d+\.\d+\b",  # ISO 27001 A.8.1.1
            
            # PCI DSS References
            r"\b\d+\.\d+\.\d+\b",  # 1.2.1, 3.4.1
            r"\bPCI\s+DSS\s+\d+\.\d+\.\d+\b",  # PCI DSS 1.2.1
            
            # NIST CSF References
            r"\b[A-Z]{2}\.[A-Z]{2}-\d+\b",  # ID.AM-1, PR.AC-3
            r"\bNIST\s+CSF\s+[A-Z]{2}\.[A-Z]{2}-\d+\b",  # NIST CSF ID.AM-1
            
            # FISMA/FedRAMP References
            r"\b[A-Z]{2,4}-\d+\s+\([A-Z]+\)\b",  # AC-2 (HIGH), SI-4 (MODERATE)
            
            # Generic framework references
            r"\b[A-Z]{2,6}-\d+\([A-Z]+\)\b",  # Generic with impact level
        ]

        controls = []
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Normalize case for consistency
            normalized_matches = [match.upper().strip() for match in matches]
            controls.extend(normalized_matches)

        return list(set(controls))  # Remove duplicates

    def control_reference_score(
        self, model_response: str, ideal_answer: str
    ) -> ScoringResult:
        """Score based on overlap of control references."""
        # First validate the response
        is_valid, failure_reason = self.validate_response(model_response)
        if not is_valid:
            return ScoringResult(
                accuracy_score=0.0,
                method=ScoringMethod.CONTROL_REFERENCE,
                explanation=f"Invalid response: {failure_reason}",
                details={
                    "model_controls": [],
                    "ideal_controls": list(self.extract_control_references(ideal_answer)),
                    "intersection": [],
                    "validation_failure": failure_reason,
                },
            )
        
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
                # Both have no controls - only give perfect score if response is substantive
                # This fixes the critical flaw where empty responses got perfect scores
                score = 1.0 if len(model_response.strip()) > 50 else 0.3

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

    def structural_validation_score(
        self, model_response: str, question: str
    ) -> ScoringResult:
        """Score based on structural adherence to requested format."""
        score = 1.0
        issues = []
        
        question_lower = question.lower()
        response_lower = model_response.lower()
        
        # Check for requested list format
        if "list" in question_lower or "enumerate" in question_lower:
            # Look for list indicators
            has_bullets = bool(re.search(r'^[\s]*[-*•]\s', model_response, re.MULTILINE))
            has_numbers = bool(re.search(r'^[\s]*\d+[\.\)]\s', model_response, re.MULTILINE))
            
            if not (has_bullets or has_numbers):
                score -= 0.3
                issues.append("Missing list format when requested")
        
        # Check for requested explanation/justification
        if "why" in question_lower or "explain" in question_lower or "because" in question_lower:
            # Look for explanatory keywords
            explanatory_keywords = ["because", "since", "as", "due to", "requires", "mandates", "specifies"]
            has_explanation = any(keyword in response_lower for keyword in explanatory_keywords)
            
            if not has_explanation:
                score -= 0.2
                issues.append("Missing explanation when requested")
        
        # Check for excessive verbosity (more than 3x expected length)
        expected_length = min(500, len(question) * 3)  # Reasonable response length
        if len(model_response) > expected_length * 3:
            score -= 0.1
            issues.append("Response may be too verbose")
        
        # Check for policy format compliance (short_prompt.md structure)
        if "policy" in question_lower or "short_prompt" in question_lower or "format" in question_lower:
            required_sections = [
                r'##\s*Purpose\s*&\s*Scope',
                r'##\s*Policy\s*Statements?',
                r'##\s*Roles?\s*&\s*Responsibilities',
                r'##\s*Compliance\s*&\s*Enforcement',
                r'##\s*Review\s*Cycle',
                r'##\s*Framework\s*Mappings?'
            ]
            
            section_score = 0
            missing_sections = []
            for section_pattern in required_sections:
                if re.search(section_pattern, model_response, re.IGNORECASE):
                    section_score += 1
                else:
                    section_name = section_pattern.replace(r'##\s*', '').replace(r'\s*', ' ').replace('?', '')
                    missing_sections.append(section_name)
            
            if section_score >= 5:  # Most sections present
                score += 0.1
                issues.append("Good policy structure compliance")
            elif section_score < 3:  # Many sections missing
                score -= 0.3
                issues.append(f"Missing policy sections: {', '.join(missing_sections[:3])}")
            
            # Check for framework mapping table
            if re.search(r'\|\s*Policy\s*\|\s*\w+\s*Control\s*\||\|\s*\w+\s*Control\s*\|\s*\w+', model_response, re.IGNORECASE):
                score += 0.1
                issues.append("Framework mapping table present")
            else:
                score -= 0.2
                issues.append("Missing framework mapping table")
        
        # Check for structured sections when multiple requirements requested
        elif "requirement" in question_lower and "requirements" in question_lower:
            # Look for section breaks or clear separation
            has_structure = bool(re.search(r'\n\n|---|\*\*|##|\d+\.|[A-Z]\)', model_response))
            if not has_structure and len(model_response) > 200:
                score -= 0.2
                issues.append("Missing clear structure for multiple requirements")
        
        score = max(0.0, score)  # Ensure non-negative
        
        explanation = f"Structural compliance: {score:.2f}"
        if issues:
            explanation += f" (Issues: {'; '.join(issues)})"
        else:
            explanation += " (No structural issues found)"
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.STRUCTURAL_VALIDATION,
            explanation=explanation,
            details={
                "issues": issues,
                "response_length": len(model_response),
                "question_indicators": {
                    "list_requested": "list" in question_lower or "enumerate" in question_lower,
                    "explanation_requested": "why" in question_lower or "explain" in question_lower,
                    "multiple_requirements": "requirement" in question_lower and "requirements" in question_lower,
                }
            },
        )

    def citation_verification_score(
        self, model_response: str, framework_context: str = None
    ) -> ScoringResult:
        """Verify that cited controls/articles actually exist in referenced frameworks."""
        # framework_context parameter reserved for future use with dynamic validation
        controls = self.extract_control_references(model_response)
        
        if not controls:
            return ScoringResult(
                accuracy_score=1.0,
                method=ScoringMethod.CITATION_VERIFICATION,
                explanation="No controls cited to verify",
                details={"verified_controls": [], "invalid_controls": []},
            )
        
        # Known valid control patterns for major frameworks
        valid_patterns = {
            "SOC2": {
                "CC1": [1, 2, 3, 4, 5],
                "CC2": [1, 2, 3],
                "CC3": [1, 2, 3, 4],
                "CC4": [1, 2],
                "CC5": [1, 2, 3],
                "CC6": [1, 2, 3, 4, 5, 6, 7, 8],
                "CC7": [1, 2, 3, 4, 5],
                "CC8": [1],
                "CC9": [1, 2],
                "A1": [1, 2, 3],
                "PI1": [1, 2, 3],
                "P1": [1, 2],
                "P2": [1, 2],
                "P3": [1, 2],
                "P4": [1, 2, 3],
                "P5": [1, 2],
                "P6": [1, 2, 3],
                "P7": [1],
                "P8": [1],
                "C1": [1, 2],
            },
            "NIST_CSF": {
                "ID": ["AM", "BE", "GV", "RA", "RM", "SC"],
                "PR": ["AC", "AT", "DS", "IP", "MA", "PT"],
                "DE": ["AE", "CM", "DP"],
                "RS": ["RP", "CO", "AN", "MI", "IM"],
                "RC": ["RP", "IM", "CO"],
            },
            "GDPR_ARTICLES": list(range(1, 100)),  # Articles 1-99
            "NIST_800_53": {
                "AC": list(range(1, 26)),
                "AT": list(range(1, 6)),
                "AU": list(range(1, 17)),
                "CA": list(range(1, 10)),
                "CM": list(range(1, 15)),
                "CP": list(range(1, 14)),
                "IA": list(range(1, 13)),
                "IR": list(range(1, 11)),
                "MA": list(range(1, 8)),
                "MP": list(range(1, 9)),
                "PE": list(range(1, 21)),
                "PL": list(range(1, 12)),
                "PS": list(range(1, 9)),
                "PT": list(range(1, 9)),
                "RA": list(range(1, 11)),
                "SA": list(range(1, 23)),
                "SC": list(range(1, 54)),
                "SI": list(range(1, 24)),
                "SR": list(range(1, 13)),
            }
        }
        
        verified_controls = []
        invalid_controls = []
        
        for control in controls:
            is_valid = False
            
            # Check SOC 2 controls
            soc2_match = re.match(r'([A-Z]{1,3})(\d+)\.(\d+)', control)
            if soc2_match:
                prefix, _, minor = soc2_match.groups()  # major not used in current logic
                if prefix in valid_patterns["SOC2"] and int(minor) in valid_patterns["SOC2"][prefix]:
                    is_valid = True
            
            # Check NIST CSF controls
            csf_match = re.match(r'([A-Z]{2})\.([A-Z]{2})-(\d+)', control)
            if csf_match:
                function, category, num = csf_match.groups()
                if function in valid_patterns["NIST_CSF"] and category in valid_patterns["NIST_CSF"][function]:
                    is_valid = True
            
            # Check GDPR Articles
            gdpr_match = re.search(r'ARTICLE\s+(\d+)', control.upper())
            if gdpr_match:
                article_num = int(gdpr_match.group(1))
                if article_num in valid_patterns["GDPR_ARTICLES"]:
                    is_valid = True
            
            # Check NIST 800-53 controls
            nist_match = re.match(r'([A-Z]{2,4})-(\d+)', control)
            if nist_match:
                family, num = nist_match.groups()
                if family in valid_patterns["NIST_800_53"] and int(num) in valid_patterns["NIST_800_53"][family]:
                    is_valid = True
            
            if is_valid:
                verified_controls.append(control)
            else:
                invalid_controls.append(control)
        
        # Calculate score based on verification rate
        if controls:
            score = len(verified_controls) / len(controls)
        else:
            score = 1.0
        
        explanation = f"Citation verification: {len(verified_controls)}/{len(controls)} controls verified"
        if invalid_controls:
            explanation += f" (Invalid: {', '.join(invalid_controls[:3])}{'...' if len(invalid_controls) > 3 else ''})"
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.CITATION_VERIFICATION,
            explanation=explanation,
            details={
                "verified_controls": verified_controls,
                "invalid_controls": invalid_controls,
                "total_controls": len(controls),
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
        
        # First validate the response
        is_valid, failure_reason = self.validate_response(model_response)
        if not is_valid:
            return ScoringResult(
                accuracy_score=0.0,
                method=ScoringMethod.LLM_JUDGE,
                explanation=f"Invalid response: {failure_reason}",
                details={"validation_failure": failure_reason, "judge_response": None},
            )

        judge_prompt = f"""You are evaluating the accuracy of a model's response to a cybersecurity compliance question.

Question: {question}

Model Response: {model_response}

Ground Truth Answer: {ideal_answer}

CRITICAL INSTRUCTIONS FOR SCORING:
- If the model response is empty, just error text, or completely irrelevant to cybersecurity, assign score 0.0
- If the model response is too short to be meaningful (<20 characters), assign maximum score 0.3
- If the model response doesn't attempt to address the question asked, assign maximum score 0.2

Please evaluate the model's response on the following criteria:
1. Correctness: Does the model identify the correct compliance requirement(s)?
2. Completeness: Does the model address all relevant aspects mentioned in the ground truth?
3. Specificity: Does the model provide specific control/requirement references when appropriate?
4. Relevance: Does the response actually address the cybersecurity question asked?

Rate the overall accuracy on a scale from 0.0 to 1.0, where:
- 1.0 = Perfect match with ground truth
- 0.8-0.9 = Minor differences but substantially correct
- 0.6-0.7 = Partially correct but missing key elements
- 0.4-0.5 = Some relevant information but significant errors
- 0.2-0.3 = Minimal relevance to the correct answer
- 0.0 = Completely incorrect, irrelevant, empty, or error response

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

    def conciseness_score(
        self, model_response: str, question: str = None
    ) -> ScoringResult:
        """Score response conciseness based on length optimization and clarity."""
        response_length = len(model_response)
        word_count = len(model_response.split())
        
        # Base score starts at 1.0
        score = 1.0
        issues = []
        
        # Penalize excessive length (more than 1500 characters or 250 words for policy)
        if response_length > 1500:
            score -= 0.3
            issues.append(f"Response too long ({response_length} chars, target <1500)")
        elif response_length > 1000:
            score -= 0.1
            issues.append(f"Response somewhat lengthy ({response_length} chars)")
            
        if word_count > 250:
            score -= 0.2
            issues.append(f"Word count high ({word_count} words, target <250)")
        
        # Check for unnecessary verbosity patterns
        verbose_patterns = [
            r'it is important to note that',
            r'it should be noted that',
            r'please be advised that',
            r'it is worth mentioning',
            r'as previously mentioned',
            r'furthermore, it is essential',
        ]
        
        verbose_count = sum(len(re.findall(pattern, model_response, re.IGNORECASE)) 
                           for pattern in verbose_patterns)
        if verbose_count > 0:
            score -= verbose_count * 0.1
            issues.append(f"Contains verbose phrases ({verbose_count} instances)")
        
        # Reward clear structure for policies (sections, bullet points)
        if question and ("policy" in question.lower() or "format" in question.lower()):
            structure_indicators = [
                r'##\s+\w+',  # Section headers
                r'\d+\.\s+',  # Numbered lists
                r'\*\*\w+\*\*',  # Bold headers
                r'\|\s*\w+\s*\|',  # Table structure
            ]
            
            structure_score = sum(min(3, len(re.findall(pattern, model_response))) 
                                for pattern in structure_indicators)
            if structure_score >= 8:  # Well-structured
                score += 0.1
                issues.append("Good structural organization")
            elif structure_score < 4:  # Poor structure
                score -= 0.2
                issues.append("Poor structural organization")
        
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        
        explanation = f"Conciseness score: {score:.2f}"
        if issues:
            explanation += f" (Issues: {'; '.join(issues)})"
        else:
            explanation += " (Clear and concise)"
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.STRUCTURAL_VALIDATION,  # Reusing enum for now
            explanation=explanation,
            details={
                "response_length": response_length,
                "word_count": word_count,
                "verbose_phrases": verbose_count,
                "issues": issues,
            },
        )

    def contextual_relevance_score(
        self, model_response: str, question: str, ideal_answer: str = None
    ) -> ScoringResult:
        """Score response based on contextual relevance to cybersecurity domain and question."""
        # First validate the response
        is_valid, failure_reason = self.validate_response(model_response)
        if not is_valid:
            return ScoringResult(
                accuracy_score=0.0,
                method=ScoringMethod.CONTEXTUAL_RELEVANCE,
                explanation=f"Invalid response: {failure_reason}",
                details={"validation_failure": failure_reason},
            )
        
        score = 1.0
        issues = []
        
        response_lower = model_response.lower()
        question_lower = question.lower()
        
        # Check for cybersecurity domain relevance
        cybersecurity_terms = [
            "security", "compliance", "control", "framework", "risk", "vulnerability",
            "threat", "policy", "governance", "audit", "incident", "breach", 
            "encryption", "access", "authentication", "authorization", "monitoring",
            "gdpr", "hipaa", "sox", "pci", "nist", "iso", "soc", "cmmc", "fedramp"
        ]
        
        cyber_term_count = sum(1 for term in cybersecurity_terms if term in response_lower)
        if cyber_term_count == 0:
            score -= 0.8  # Major penalty for no cybersecurity relevance
            issues.append("No cybersecurity terminology detected")
        elif cyber_term_count < 3:
            score -= 0.3  # Minor penalty for limited cybersecurity context
            issues.append("Limited cybersecurity terminology")
        else:
            issues.append(f"Good cybersecurity terminology usage ({cyber_term_count} terms)")
        
        # Check if response addresses the question type
        question_type_indicators = {
            "framework": ["framework", "standard", "regulation", "compliance"],
            "control": ["control", "requirement", "safeguard", "measure"],
            "implementation": ["implement", "deploy", "configure", "setup"],
            "risk": ["risk", "threat", "vulnerability", "assessment"],
            "policy": ["policy", "procedure", "guideline", "document"],
            "technical": ["technical", "system", "technology", "architecture"],
        }
        
        question_types_found = []
        for q_type, indicators in question_type_indicators.items():
            if any(indicator in question_lower for indicator in indicators):
                question_types_found.append(q_type)
        
        response_addresses_type = False
        for q_type in question_types_found:
            type_indicators = question_type_indicators[q_type]
            if any(indicator in response_lower for indicator in type_indicators):
                response_addresses_type = True
                break
        
        if not response_addresses_type and question_types_found:
            score -= 0.4
            issues.append(f"Does not address question type: {', '.join(question_types_found)}")
        
        # Check for framework alignment if question mentions specific frameworks
        mentioned_frameworks = []
        framework_patterns = {
            "nist": ["nist", "800-53", "800-171", "csf", "cybersecurity framework"],
            "gdpr": ["gdpr", "general data protection", "article"],
            "hipaa": ["hipaa", "health insurance", "164."],
            "sox": ["sox", "sarbanes", "sarbanes-oxley"],
            "pci": ["pci", "payment card", "pci-dss", "pci dss"],
            "iso": ["iso", "27001", "27002"],
            "soc": ["soc", "soc 2", "soc2", "trust services"],
            "cmmc": ["cmmc", "cybersecurity maturity"],
            "fedramp": ["fedramp", "federal risk"],
        }
        
        for framework, patterns in framework_patterns.items():
            if any(pattern in question_lower for pattern in patterns):
                mentioned_frameworks.append(framework)
                if not any(pattern in response_lower for pattern in patterns):
                    score -= 0.2
                    issues.append(f"Question mentions {framework.upper()} but response doesn't address it")
        
        # Check response depth and specificity
        word_count = len(model_response.split())
        if word_count < 20:
            score -= 0.3
            issues.append("Response too brief for complex cybersecurity topic")
        elif word_count > 500:
            score -= 0.1
            issues.append("Response may be too verbose")
        
        # Bonus for specific technical details
        technical_indicators = [
            "configuration", "implementation", "architecture", "deployment",
            "monitoring", "logging", "alerting", "incident response",
            "backup", "recovery", "encryption", "key management"
        ]
        
        technical_count = sum(1 for term in technical_indicators if term in response_lower)
        if technical_count >= 3:
            score += 0.1
            issues.append("Good technical specificity")
        
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        
        explanation = f"Contextual relevance score: {score:.3f}"
        if issues:
            explanation += f" (Issues: {'; '.join(issues)})"
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.CONTEXTUAL_RELEVANCE,
            explanation=explanation,
            details={
                "cybersecurity_terms_found": cyber_term_count,
                "question_types_detected": question_types_found,
                "frameworks_mentioned": mentioned_frameworks,
                "word_count": word_count,
                "technical_indicators_found": technical_count,
                "issues": issues,
            },
        )

    def completeness_score(
        self, model_response: str, question: str, ideal_answer: str
    ) -> ScoringResult:
        """Score response based on completeness and coverage of required elements."""
        # First validate the response
        is_valid, failure_reason = self.validate_response(model_response)
        if not is_valid:
            return ScoringResult(
                accuracy_score=0.0,
                method=ScoringMethod.COMPLETENESS,
                explanation=f"Invalid response: {failure_reason}",
                details={"validation_failure": failure_reason},
            )
        
        score = 1.0
        issues = []
        coverage_details = {}
        
        response_lower = model_response.lower()
        question_lower = question.lower()
        ideal_lower = ideal_answer.lower()
        
        # Extract key concepts from ideal answer
        ideal_controls = self.extract_control_references(ideal_answer)
        model_controls = self.extract_control_references(model_response)
        
        # Check control coverage
        if ideal_controls:
            covered_controls = set(model_controls) & set(ideal_controls)
            control_coverage = len(covered_controls) / len(ideal_controls) if ideal_controls else 1.0
            
            if control_coverage < 0.3:
                score -= 0.4
                issues.append(f"Poor control coverage ({control_coverage:.1%})")
            elif control_coverage < 0.7:
                score -= 0.2
                issues.append(f"Partial control coverage ({control_coverage:.1%})")
            else:
                issues.append(f"Good control coverage ({control_coverage:.1%})")
            
            coverage_details["control_coverage"] = control_coverage
            coverage_details["covered_controls"] = list(covered_controls)
            coverage_details["missing_controls"] = list(set(ideal_controls) - set(model_controls))
        
        # Check for key concept coverage from ideal answer
        # Extract important terms from ideal answer (excluding common words)
        stop_words = {"the", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by", "a", "an", "is", "are", "was", "were", "will", "would", "should", "must", "can", "could", "may", "might"}
        
        ideal_words = [word.strip(".,!?()[]{}") for word in ideal_lower.split() if len(word) > 3 and word not in stop_words]
        important_terms = [word for word in ideal_words if any(cyber in word for cyber in ["security", "compliance", "control", "policy", "risk", "framework", "audit", "governance"])]
        
        if important_terms:
            covered_terms = sum(1 for term in important_terms if term in response_lower)
            term_coverage = covered_terms / len(important_terms)
            
            if term_coverage < 0.4:
                score -= 0.3
                issues.append(f"Low key term coverage ({term_coverage:.1%})")
            elif term_coverage < 0.8:
                score -= 0.1
                issues.append(f"Moderate key term coverage ({term_coverage:.1%})")
            else:
                issues.append(f"High key term coverage ({term_coverage:.1%})")
            
            coverage_details["term_coverage"] = term_coverage
            coverage_details["important_terms_total"] = len(important_terms)
            coverage_details["covered_terms"] = covered_terms
        
        # Check for multi-part question coverage
        question_parts = []
        if " and " in question_lower:
            question_parts = [part.strip() for part in question_lower.split(" and ")]
        elif "list" in question_lower or "identify" in question_lower:
            # Look for numbered or bulleted lists in response
            has_list = bool(re.search(r'^\s*\d+[\.\)]\s|\s*[-*•]\s', model_response, re.MULTILINE))
            if not has_list:
                score -= 0.2
                issues.append("Question asks for list but response lacks structured format")
        
        if question_parts and len(question_parts) > 1:
            coverage_count = 0
            for part in question_parts:
                if any(key_word in response_lower for key_word in part.split() if len(key_word) > 3):
                    coverage_count += 1
            
            part_coverage = coverage_count / len(question_parts)
            if part_coverage < 0.5:
                score -= 0.3
                issues.append(f"Poor multi-part coverage ({part_coverage:.1%})")
            elif part_coverage < 1.0:
                score -= 0.1
                issues.append(f"Partial multi-part coverage ({part_coverage:.1%})")
            else:
                issues.append("Complete multi-part coverage")
            
            coverage_details["multi_part_coverage"] = part_coverage
        
        # Check for explanation depth when question asks "why" or "explain"
        if "why" in question_lower or "explain" in question_lower or "because" in question_lower:
            explanatory_indicators = ["because", "since", "due to", "as a result", "therefore", "consequently", "reason", "purpose"]
            explanation_count = sum(1 for indicator in explanatory_indicators if indicator in response_lower)
            
            if explanation_count == 0:
                score -= 0.3
                issues.append("Question asks for explanation but response lacks explanatory language")
            elif explanation_count < 2:
                score -= 0.1
                issues.append("Limited explanatory depth")
            else:
                issues.append("Good explanatory depth")
            
            coverage_details["explanatory_indicators"] = explanation_count
        
        # Check for implementation details when appropriate
        if "implement" in question_lower or "how to" in question_lower:
            implementation_terms = ["configure", "setup", "deploy", "install", "enable", "create", "establish", "develop"]
            implementation_count = sum(1 for term in implementation_terms if term in response_lower)
            
            if implementation_count == 0:
                score -= 0.2
                issues.append("Question asks for implementation but response lacks actionable details")
            else:
                issues.append("Contains implementation details")
            
            coverage_details["implementation_terms"] = implementation_count
        
        score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
        
        explanation = f"Completeness score: {score:.3f}"
        if issues:
            explanation += f" (Issues: {'; '.join(issues)})"
        
        return ScoringResult(
            accuracy_score=score,
            method=ScoringMethod.COMPLETENESS,
            explanation=explanation,
            details=coverage_details,
        )

    async def composite_policy_score(
        self, question: str, model_response: str, ideal_answer: str
    ) -> ScoringResult:
        """
        Enhanced composite scoring with response validation and improved rubrics:
        - Validation (10%): Must pass basic quality checks
        - Structure (25%): Adherence to short_prompt.md format
        - Technical Accuracy (40%): Control citations and factual correctness  
        - Completeness (15%): Coverage of key requirements
        - Conciseness (10%): Clear, focused communication
        """
        # First validate the response - CRITICAL: this prevents empty responses from getting high scores
        is_valid, failure_reason = self.validate_response(model_response)
        if not is_valid:
            return ScoringResult(
                accuracy_score=0.0,
                method=ScoringMethod.COMPOSITE_POLICY,
                explanation=f"Response validation failed: {failure_reason}",
                details={"validation_failure": failure_reason, "component_scores": {}},
            )
        
        # Check if this is a policy generation question
        metadata_indicators = [
            "short_prompt" in question.lower(),
            "policy" in question.lower(),
            "format" in question.lower(),
            "create" in question.lower() and ("compliance" in question.lower() or "compliant" in question.lower())
        ]
        
        if not any(metadata_indicators):
            # Enhanced scoring for non-policy questions
            accuracy_result = await self.llm_judge_score(question, model_response, ideal_answer)
            relevance_result = self.contextual_relevance_score(model_response, question, ideal_answer)
            completeness_result = self.completeness_score(model_response, question, ideal_answer)
            
            # Weights for general cybersecurity questions
            accuracy_weight = 0.50
            relevance_weight = 0.30
            completeness_weight = 0.20
            
            composite_score = (
                accuracy_result.accuracy_score * accuracy_weight +
                relevance_result.accuracy_score * relevance_weight +
                completeness_result.accuracy_score * completeness_weight
            )
            
            explanation = f"Enhanced scoring: {composite_score:.3f}\n"
            explanation += f"Accuracy ({accuracy_weight:.0%}): {accuracy_result.accuracy_score:.3f}\n"
            explanation += f"Relevance ({relevance_weight:.0%}): {relevance_result.accuracy_score:.3f}\n"
            explanation += f"Completeness ({completeness_weight:.0%}): {completeness_result.accuracy_score:.3f}"
            
            return ScoringResult(
                accuracy_score=composite_score,
                method=ScoringMethod.COMPOSITE_POLICY,
                explanation=explanation,
                details={
                    "component_scores": {
                        "accuracy": accuracy_result.accuracy_score,
                        "relevance": relevance_result.accuracy_score,
                        "completeness": completeness_result.accuracy_score,
                    },
                    "weights": {
                        "accuracy": accuracy_weight,
                        "relevance": relevance_weight,
                        "completeness": completeness_weight,
                    },
                },
            )
        
        # Get component scores for policy questions
        structure_result = self.structural_validation_score(model_response, question)
        accuracy_result = await self.llm_judge_score(question, model_response, ideal_answer)
        completeness_result = self.completeness_score(model_response, question, ideal_answer)
        conciseness_result = self.conciseness_score(model_response, question)
        
        # Enhanced weights with validation gate and completeness
        validation_weight = 0.10  # Already passed, so contributes 1.0
        structure_weight = 0.25
        accuracy_weight = 0.40
        completeness_weight = 0.15
        conciseness_weight = 0.10
        
        composite_score = (
            1.0 * validation_weight +  # Validation passed
            structure_result.accuracy_score * structure_weight +
            accuracy_result.accuracy_score * accuracy_weight +
            completeness_result.accuracy_score * completeness_weight +
            conciseness_result.accuracy_score * conciseness_weight
        )
        
        # Create detailed explanation
        explanation = f"Enhanced policy score: {composite_score:.3f}\n"
        explanation += f"Validation ({validation_weight:.0%}): 1.0 - Response passed validation\n"
        explanation += f"Structure ({structure_weight:.0%}): {structure_result.accuracy_score:.3f} - {structure_result.explanation}\n"
        explanation += f"Accuracy ({accuracy_weight:.0%}): {accuracy_result.accuracy_score:.3f} - {accuracy_result.explanation}\n"
        explanation += f"Completeness ({completeness_weight:.0%}): {completeness_result.accuracy_score:.3f} - {completeness_result.explanation}\n"
        explanation += f"Conciseness ({conciseness_weight:.0%}): {conciseness_result.accuracy_score:.3f} - {conciseness_result.explanation}"
        
        return ScoringResult(
            accuracy_score=composite_score,
            method=ScoringMethod.COMPOSITE_POLICY,
            explanation=explanation,
            details={
                "validation_passed": True,
                "component_scores": {
                    "validation": 1.0,
                    "structure": structure_result.accuracy_score,
                    "accuracy": accuracy_result.accuracy_score,
                    "completeness": completeness_result.accuracy_score,
                    "conciseness": conciseness_result.accuracy_score,
                },
                "weights": {
                    "validation": validation_weight,
                    "structure": structure_weight,
                    "accuracy": accuracy_weight,
                    "completeness": completeness_weight,
                    "conciseness": conciseness_weight,
                },
                "component_details": {
                    "structure": structure_result.details,
                    "accuracy": accuracy_result.details,
                    "completeness": completeness_result.details,
                    "conciseness": conciseness_result.details,
                }
            },
        )

    async def score_response(
        self,
        question: str,
        model_response: str,
        ideal_answer: str,
        methods: List[ScoringMethod] = None,
    ) -> Dict[ScoringMethod, ScoringResult]:
        """Score a model response using multiple methods."""
        if methods is None:
            methods = [
                ScoringMethod.CONTROL_REFERENCE, 
                ScoringMethod.LLM_JUDGE,
                ScoringMethod.STRUCTURAL_VALIDATION,
                ScoringMethod.CITATION_VERIFICATION
            ]

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
            elif method == ScoringMethod.STRUCTURAL_VALIDATION:
                results[method] = self.structural_validation_score(
                    model_response, question
                )
            elif method == ScoringMethod.CITATION_VERIFICATION:
                results[method] = self.citation_verification_score(
                    model_response
                )
            elif method == ScoringMethod.COMPOSITE_POLICY:
                results[method] = await self.composite_policy_score(
                    question, model_response, ideal_answer
                )
            elif method == ScoringMethod.CONTEXTUAL_RELEVANCE:
                results[method] = self.contextual_relevance_score(
                    model_response, question, ideal_answer
                )
            elif method == ScoringMethod.COMPLETENESS:
                results[method] = self.completeness_score(
                    model_response, question, ideal_answer
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
            return "google/gemini-2.5-flash"

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
            methods = [
                ScoringMethod.CONTROL_REFERENCE, 
                ScoringMethod.LLM_JUDGE,
                ScoringMethod.STRUCTURAL_VALIDATION,
                ScoringMethod.CITATION_VERIFICATION
            ]

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
            elif method == ScoringMethod.STRUCTURAL_VALIDATION:
                results[method] = self.single_scorer_1.structural_validation_score(
                    model_response, question
                )
            elif method == ScoringMethod.CITATION_VERIFICATION:
                results[method] = self.single_scorer_1.citation_verification_score(
                    model_response
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
