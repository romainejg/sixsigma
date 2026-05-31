"""Response evaluator service."""

from __future__ import annotations

from core.models import Evaluation, Scenario
from core.openai_service import OpenAIService
from prompts.evaluation_prompts import build_evaluation_prompt


class ResponseEvaluator:
    """Evaluates learner responses using OpenAIService."""

    def __init__(self, openai_service: OpenAIService) -> None:
        self.openai_service = openai_service

    def evaluate(self, scenario: Scenario, user_response: str) -> Evaluation:
        prompt = build_evaluation_prompt(scenario, user_response)
        payload = self.openai_service.generate_json(
            prompt,
            schema_name="evaluation",
            expected_fields=[
                "overall_score",
                "dimension_scores",
                "strengths",
                "weaknesses",
                "missed_concepts",
                "incorrect_assumptions",
                "recommended_next_focus",
                "evaluator_notes",
            ],
        )
        if "error" in payload:
            payload = self.openai_service.generate_json("", schema_name="evaluation")
        return Evaluation.from_dict(payload)
