"""OpenAI abstraction with fallback mock mode."""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from openai import OpenAI

from config import DEFAULT_MODEL, get_api_key, get_mock_mode


class OpenAIService:
    """Handles key loading, client usage, validation, and mock behavior."""

    def __init__(self, model: Optional[str] = None) -> None:
        self.model = model or DEFAULT_MODEL
        self.api_key = get_api_key()
        self.mock_mode = get_mock_mode() if self.api_key is None else False
        self.client = OpenAI(api_key=self.api_key) if self.api_key else None

    def update_model(self, model: str) -> None:
        self.model = model

    def is_mock_mode(self) -> bool:
        return self.mock_mode

    def generate_json(
        self,
        prompt: str,
        schema_name: Optional[str] = None,
        expected_fields: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        if self.mock_mode:
            return self._mock_response(schema_name)

        if not self.client:
            return {"error": "OpenAI client not configured. Falling back to mock mode is recommended."}

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Return valid JSON only. No markdown, no prose outside JSON."},
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0.2,
            )
            content = response.choices[0].message.content or "{}"
            payload = json.loads(content)
        except Exception as exc:
            return {"error": f"OpenAI request failed: {exc}"}

        if expected_fields:
            missing = [field for field in expected_fields if field not in payload]
            if missing:
                return {"error": f"Malformed response missing fields: {', '.join(missing)}", "payload": payload}

        return payload

    @staticmethod
    def _mock_response(schema_name: Optional[str]) -> Dict[str, Any]:
        if schema_name == "scenario":
            return {
                "title": "Assembly Line Defect Escalation with Misaligned Capability",
                "pillar": "Measure Phase",
                "module": "Measurement Systems Analysis (MSA)",
                "primary_concepts": ["Gage R&R", "Cp", "Cpk"],
                "difficulty": "Intermediate",
                "scenario_text": "A high-volume assembly line producing actuator housings has seen defect escapes rise from 1.8% to 4.6% over six weeks. Leadership disputes whether the issue is measurement noise or process centering drift.",
                "background_context": "Three inspectors measure critical bore diameter across two shifts. Historical tolerance limits are 24.95mm to 25.05mm. The team launched overtime and speedups to meet demand.",
                "data_points": {
                    "gage_rr_total_variance_pct": 32,
                    "cp": 1.4,
                    "cpk": 0.82,
                    "sample_count": 120,
                    "defect_rate_pct": 4.6,
                    "shift_difference": "Night shift mean +0.03mm over day shift",
                },
                "question_to_user": "What is your prioritized diagnosis and next action plan? Explain how Gage R&R, Cp vs Cpk, and process centering should guide your recommendation.",
                "ideal_reasoning_targets": [
                    "Flag >30% Gage R&R as unacceptable and requiring measurement improvement",
                    "Explain Cp>1 but low Cpk as off-center process",
                    "Recommend containment plus centering correction before capability claims",
                    "Differentiate measurement variation from true process shift",
                ],
            }
        if schema_name == "evaluation":
            return {
                "overall_score": 74,
                "dimension_scores": {
                    "problem_diagnosis": 78,
                    "statistical_reasoning": 72,
                    "tool_application_correctness": 70,
                    "tradeoff_awareness": 76,
                    "communication_professionalism": 74,
                },
                "strengths": [
                    "Correctly identified that Cp and Cpk mismatch indicates centering issues",
                    "Recommended phased containment before full process changes",
                ],
                "weaknesses": [
                    "Did not treat 32% Gage R&R as a hard reliability barrier",
                    "Missing explicit check for appraiser-to-appraiser reproducibility",
                ],
                "missed_concepts": ["Gage R&R", "Reproducibility"],
                "incorrect_assumptions": ["Assumed capability data can be trusted before MSA correction"],
                "recommended_next_focus": "Interpretation thresholds for measurement system acceptability",
                "evaluator_notes": "Solid structure and professional tone. Increase rigor by quantifying MSA risk and sequencing decisions: validate measurement system first, then recalculate capability.",
            }
        if schema_name == "tutor":
            return {
                "teaching_summary": "A total Gage R&R contribution of 32% means measurement error is too large for reliable process decisions. Cp=1.4 with Cpk=0.82 indicates potential capability but poor centering or shift-specific drift.",
                "key_concepts": ["Gage R&R acceptance criteria", "Cp vs Cpk interpretation", "Process mean shift"],
                "model_answer": "First, contain quality risk and pause capability claims. Next, run focused MSA improvements to reduce total Gage R&R below 10% (or at least below 30% for provisional use). Then re-center the process by shift, verify mean alignment, and recompute Cpk to validate control.",
                "practical_rule_of_thumb": "If Cp is healthy but Cpk is weak, your spread may be okay but your process is not centered. If Gage R&R exceeds 30%, fix measurement first.",
                "next_study_prompt": "Practice building a decision tree for MSA-first vs capability-first actions using Cp/Cpk and variance contribution thresholds.",
            }
        return {"error": "Unsupported schema for mock mode."}
