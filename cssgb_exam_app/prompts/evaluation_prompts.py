"""Prompt builder for answer evaluation."""

from __future__ import annotations

from core.models import Scenario


def build_evaluation_prompt(scenario: Scenario, user_response: str) -> str:
    return f"""
Evaluate the learner response for ASQ CSSGB rigor.
Reward:
- deep technical application
- proper statistical sequencing
- correct distinction between common and special cause variation
- consideration of measurement system errors
Penalize unsupported claims or tool misuse.

Scenario:
Title: {scenario.title}
Pillar: {scenario.pillar}
Module: {scenario.module}
Concepts: {", ".join(scenario.primary_concepts)}
Scenario Text: {scenario.scenario_text}
Background: {scenario.background_context}
Data Points: {scenario.data_points}
Question: {scenario.question_to_user}
Ideal Reasoning Targets: {scenario.ideal_reasoning_targets}

User Response:
{user_response}

Return JSON with exact fields:
{{
  "overall_score": int,
  "dimension_scores": {{
    "problem_diagnosis": int,
    "statistical_reasoning": int,
    "tool_application_correctness": int,
    "tradeoff_awareness": int,
    "communication_professionalism": int
  }},
  "strengths": [str],
  "weaknesses": [str],
  "missed_concepts": [str],
  "incorrect_assumptions": [str],
  "recommended_next_focus": str,
  "evaluator_notes": str
}}
""".strip()
