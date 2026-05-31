"""Adaptive progression rules for practice personalization."""

from __future__ import annotations

from datetime import datetime
from typing import Dict

from core.curriculum import CurriculumManager
from core.database import DatabaseManager
from core.models import Evaluation, Scenario


class AdaptiveEngine:
    """Simple mastery updater and recommendation engine."""

    def __init__(self, database: DatabaseManager, curriculum: CurriculumManager) -> None:
        self.database = database
        self.curriculum = curriculum

    @staticmethod
    def _clamp_score(value: float) -> float:
        return max(0.0, min(100.0, value))

    def process_outcome(self, scenario: Scenario, evaluation: Evaluation) -> None:
        now = datetime.utcnow().isoformat()
        for concept in scenario.primary_concepts:
            record = self.database.get_concept_mastery_record(concept)
            if not record:
                continue
            current = float(record["mastery_score"])
            recent = self.database.get_recent_scores_for_concept(concept, limit=2)

            if evaluation.overall_score >= 85 and len(recent) >= 1 and recent[0] >= 85:
                delta = 8.0
            elif evaluation.overall_score < 70:
                delta = -10.0
            else:
                delta = 2.0

            self.database.update_concept_mastery(concept, self._clamp_score(current + delta), now)

        for missed in evaluation.missed_concepts:
            record = self.database.get_concept_mastery_record(missed)
            if not record:
                continue
            lowered = self._clamp_score(float(record["mastery_score"]) - 5.0)
            self.database.update_concept_mastery(missed, lowered, now, attempts_inc=0)

    def recommend_today_practice(self) -> Dict[str, str]:
        existing = self.database.get_daily_recommendation()
        if existing:
            return existing

        weak = self.database.get_weak_concepts(limit=5)
        for item in weak:
            recommendation = {
                "pillar_name": item["pillar_name"],
                "module_name": item["module_name"],
                "concept_name": item["concept_name"],
                "reason": "Weak concept priority with spaced repetition.",
            }
            self.database.save_daily_recommendation(**recommendation)
            return recommendation

        first_pillar = self.curriculum.get_all_curriculum()[0]
        first_module = first_pillar["modules"][0]
        recommendation = {
            "pillar_name": first_pillar["pillar"],
            "module_name": first_module["module"],
            "concept_name": first_module["concepts"][0],
            "reason": "Starting next available curriculum concept.",
        }
        self.database.save_daily_recommendation(**recommendation)
        return recommendation
