"""Learning session orchestration for Streamlit state."""

from __future__ import annotations

from typing import Optional, Tuple

import streamlit as st

from core.adaptive_engine import AdaptiveEngine
from core.database import DatabaseManager
from core.evaluator import ResponseEvaluator
from core.models import Evaluation, Scenario, TutorFeedback
from core.scenario_generator import ScenarioGenerator
from core.tutor import Tutor


class LearningSession:
    """Coordinates scenario generation, evaluation, teaching, and persistence."""

    STATE_KEYS = ["current_scenario", "current_scenario_id", "current_response_text", "latest_evaluation", "latest_tutor_feedback"]

    def __init__(self, database: DatabaseManager, scenario_generator: ScenarioGenerator, evaluator: ResponseEvaluator, tutor: Tutor, adaptive_engine: AdaptiveEngine) -> None:
        self.database = database
        self.scenario_generator = scenario_generator
        self.evaluator = evaluator
        self.tutor = tutor
        self.adaptive_engine = adaptive_engine
        self.ensure_state()

    def ensure_state(self) -> None:
        for key in self.STATE_KEYS:
            if key not in st.session_state:
                st.session_state[key] = None

    def generate_scenario(self, pillar: str, module: str, concept: str, difficulty: str) -> Scenario:
        weak = [item["concept_name"] for item in self.database.get_weak_concepts(limit=5)]
        scenario = self.scenario_generator.generate(pillar, module, concept, difficulty, weak)
        scenario_id = self.database.save_scenario(scenario)
        st.session_state["current_scenario"] = scenario
        st.session_state["current_scenario_id"] = scenario_id
        st.session_state["latest_evaluation"] = None
        st.session_state["latest_tutor_feedback"] = None
        return scenario

    def submit_response(self, user_response: str) -> Tuple[Optional[Evaluation], Optional[TutorFeedback]]:
        scenario: Optional[Scenario] = st.session_state.get("current_scenario")
        scenario_id: Optional[int] = st.session_state.get("current_scenario_id")
        if not scenario or not scenario_id:
            return None, None

        response_id = self.database.save_response(scenario_id, user_response)
        evaluation = self.evaluator.evaluate(scenario, user_response)
        self.database.save_evaluation(response_id, evaluation)

        feedback = self.tutor.teach(scenario, evaluation)
        self.database.save_tutor_feedback(response_id, feedback)

        self.adaptive_engine.process_outcome(scenario, evaluation)

        st.session_state["current_response_text"] = user_response
        st.session_state["latest_evaluation"] = evaluation
        st.session_state["latest_tutor_feedback"] = feedback
        return evaluation, feedback
