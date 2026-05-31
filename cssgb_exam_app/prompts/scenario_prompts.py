"""Prompt builder for scenario generation."""

from __future__ import annotations

from typing import List


def build_scenario_prompt(pillar: str, module: str, concept: str, difficulty: str, weak_concepts: List[str]) -> str:
    weak_text = ", ".join(weak_concepts) if weak_concepts else "None"
    return f"""
You are generating a realistic ASQ CSSGB scenario.
Create one case aligned to:
- Pillar: {pillar}
- Module: {module}
- Primary concept: {concept}
- Difficulty: {difficulty}
- Historical weak concepts to optionally reinforce: {weak_text}

Difficulty rules:
- Beginner: straightforward scenario and obvious tool fit
- Intermediate: conflicting indicators and mild missing parameters
- Advanced: ambiguous priorities, noise, and uncertain assumptions

Use realistic operational, manufacturing, transactional, or healthcare context.
Include concrete numbers (sample size, defects, capability, rates).
Do NOT make the answer obvious.

Return JSON with these exact fields:
{{
  "title": str,
  "pillar": str,
  "module": str,
  "primary_concepts": [str],
  "difficulty": str,
  "scenario_text": str,
  "background_context": str,
  "data_points": object,
  "question_to_user": str,
  "ideal_reasoning_targets": [str]
}}
""".strip()
