"""Dataclass models for scenario learning flow."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Dict, List


@dataclass
class Scenario:
    title: str
    pillar: str
    module: str
    primary_concepts: List[str]
    difficulty: str
    scenario_text: str
    background_context: str
    data_points: Dict[str, Any]
    question_to_user: str
    ideal_reasoning_targets: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Scenario":
        return cls(**payload)


@dataclass
class Evaluation:
    overall_score: int
    dimension_scores: Dict[str, int]
    strengths: List[str]
    weaknesses: List[str]
    missed_concepts: List[str]
    incorrect_assumptions: List[str]
    recommended_next_focus: str
    evaluator_notes: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "Evaluation":
        return cls(**payload)


@dataclass
class TutorFeedback:
    teaching_summary: str
    key_concepts: List[str]
    model_answer: str
    practical_rule_of_thumb: str
    next_study_prompt: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "TutorFeedback":
        return cls(**payload)


@dataclass
class ConceptMastery:
    pillar_name: str
    module_name: str
    concept_name: str
    mastery_score: float = 50.0
    attempts: int = 0
    last_seen: str = ""
    created_at: str = ""
    updated_at: str = ""
    recent_scores: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, payload: Dict[str, Any]) -> "ConceptMastery":
        return cls(**payload)
