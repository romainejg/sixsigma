"""Prompt builder for tutor feedback."""

from __future__ import annotations

from core.models import Evaluation, Scenario


def build_tutor_prompt(scenario: Scenario, evaluation: Evaluation) -> str:
    return f"""
You are a concise peer tutor for ASQ CSSGB candidates.
Explain missed ideas with mathematically grounded clarity and professional tone.

Scenario context:
- Title: {scenario.title}
- Pillar: {scenario.pillar}
- Module: {scenario.module}
- Concepts: {scenario.primary_concepts}
- Data points: {scenario.data_points}

Evaluation summary:
- Overall score: {evaluation.overall_score}
- Dimension scores: {evaluation.dimension_scores}
- Weaknesses: {evaluation.weaknesses}
- Missed concepts: {evaluation.missed_concepts}
- Incorrect assumptions: {evaluation.incorrect_assumptions}

Return JSON with exact fields:
{{
  "teaching_summary": str,
  "key_concepts": [str],
  "model_answer": str,
  "practical_rule_of_thumb": str,
  "next_study_prompt": str
}}
""".strip()
