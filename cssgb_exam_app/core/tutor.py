"""Tutor feedback service."""

from __future__ import annotations

from core.models import Evaluation, Scenario, TutorFeedback
from core.openai_service import OpenAIService
from prompts.tutor_prompts import build_tutor_prompt


class Tutor:
    """Generates tutor guidance based on evaluation."""

    def __init__(self, openai_service: OpenAIService) -> None:
        self.openai_service = openai_service

    def teach(self, scenario: Scenario, evaluation: Evaluation) -> TutorFeedback:
        prompt = build_tutor_prompt(scenario, evaluation)
        payload = self.openai_service.generate_json(
            prompt,
            schema_name="tutor",
            expected_fields=[
                "teaching_summary",
                "key_concepts",
                "model_answer",
                "practical_rule_of_thumb",
                "next_study_prompt",
            ],
        )
        if "error" in payload:
            payload = self.openai_service.generate_json("", schema_name="tutor")
        return TutorFeedback.from_dict(payload)
