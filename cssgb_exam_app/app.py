"""Streamlit entrypoint for CSSGB daily scenario app."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from config import DEFAULT_MODEL, get_api_key
from core.adaptive_engine import AdaptiveEngine
from core.curriculum import CurriculumManager
from core.database import DatabaseManager
from core.evaluator import ResponseEvaluator
from core.openai_service import OpenAIService
from core.scenario_generator import ScenarioGenerator
from core.session_manager import LearningSession
from core.tutor import Tutor

st.set_page_config(page_title="CSSGB Scenario Coach", layout="wide")


@st.cache_resource
def bootstrap() -> dict:
    curriculum = CurriculumManager()
    database = DatabaseManager()
    openai_service = OpenAIService()
    scenario_generator = ScenarioGenerator(openai_service)
    evaluator = ResponseEvaluator(openai_service)
    tutor = Tutor(openai_service)
    adaptive = AdaptiveEngine(database, curriculum)
    session = LearningSession(database, scenario_generator, evaluator, tutor, adaptive)
    return {
        "curriculum": curriculum,
        "database": database,
        "openai": openai_service,
        "adaptive": adaptive,
        "session": session,
    }


services = bootstrap()
curriculum: CurriculumManager = services["curriculum"]
database: DatabaseManager = services["database"]
openai_service: OpenAIService = services["openai"]
adaptive: AdaptiveEngine = services["adaptive"]
learning_session: LearningSession = services["session"]

st.title("ASQ CSSGB Scenario Coach")
st.caption("Daily DMAIC case-based practice for decision quality and statistical reasoning.")

section = st.sidebar.radio("Navigate", ["Dashboard", "Practice", "Review History", "Curriculum", "Settings"])

if section == "Dashboard":
    st.subheader("Dashboard")
    recommendation = adaptive.recommend_today_practice()
    st.info(
        f"Today's recommendation: **{recommendation['concept_name']}**"
        f" ({recommendation['pillar_name']} → {recommendation['module_name']})\n\n"
        f"Reason: {recommendation['reason']}"
    )

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Practice Attempts", database.get_total_practice_count())
    with col2:
        st.metric("Streak", "TODO")  # TODO: implement true streak based on date continuity.

    avg_scores = database.get_average_scores_by_pillar()
    st.write("### Average Score by DMAIC Pillar")
    if avg_scores:
        st.dataframe(pd.DataFrame(avg_scores), use_container_width=True)
    else:
        st.caption("No attempts yet.")

    weak = database.get_weak_concepts(limit=3)
    st.write("### Top 3 Weak Concepts")
    if weak:
        st.dataframe(pd.DataFrame(weak), use_container_width=True)
    else:
        st.caption("No mastery data yet.")

    recent = database.get_recent_attempts(limit=5)
    st.write("### Recent Attempts")
    if recent:
        display_cols = ["attempted_at", "pillar_name", "module_name", "title", "overall_score"]
        st.dataframe(pd.DataFrame(recent)[display_cols], use_container_width=True)
    else:
        st.caption("No recent attempts yet.")

elif section == "Practice":
    st.subheader("Practice")

    selected_pillar = st.selectbox("Pillar", curriculum.get_pillars())
    selected_module = st.selectbox("Module", curriculum.get_modules_by_pillar(selected_pillar))
    selected_concept = st.selectbox("Concept", curriculum.get_concepts_by_module(selected_pillar, selected_module))
    difficulty = st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"])

    if st.button("Generate Scenario", type="primary"):
        with st.spinner("Generating scenario..."):
            scenario = learning_session.generate_scenario(selected_pillar, selected_module, selected_concept, difficulty)
        st.success(f"Scenario generated: {scenario.title}")

    scenario = st.session_state.get("current_scenario")
    if scenario:
        st.write(f"### {scenario.title}")
        st.write(f"**Pillar / Module:** {scenario.pillar} / {scenario.module}")
        st.write(f"**Primary Concepts:** {', '.join(scenario.primary_concepts)}")
        st.write(f"**Difficulty:** {scenario.difficulty}")
        st.write("#### Scenario")
        st.write(scenario.scenario_text)
        st.write("#### Background")
        st.write(scenario.background_context)
        st.write("#### Data Points")
        st.json(scenario.data_points)
        st.write("#### Question")
        st.write(scenario.question_to_user)

    user_response = st.text_area("Your response", height=220)
    if st.button("Submit Answer"):
        if not user_response.strip():
            st.error("Please provide a response before submitting.")
        else:
            with st.spinner("Evaluating response..."):
                evaluation, feedback = learning_session.submit_response(user_response.strip())
            if not evaluation or not feedback:
                st.error("Please generate a scenario first.")
            else:
                st.success("Evaluation complete.")

    evaluation = st.session_state.get("latest_evaluation")
    feedback = st.session_state.get("latest_tutor_feedback")

    if evaluation:
        st.write("### Evaluation")
        st.metric("Overall Score", evaluation.overall_score)
        st.write("#### Rubric Breakdown")
        st.dataframe(pd.DataFrame([{"dimension": k, "score": v} for k, v in evaluation.dimension_scores.items()]), use_container_width=True)
        st.write("#### Strengths")
        st.write(evaluation.strengths)
        st.write("#### Weaknesses")
        st.write(evaluation.weaknesses)
        st.write("#### Missed Concepts")
        st.write(evaluation.missed_concepts)
        st.write("#### Incorrect Assumptions")
        st.write(evaluation.incorrect_assumptions)
        st.write("#### Recommended Next Focus")
        st.write(evaluation.recommended_next_focus)
        st.write("#### Evaluator Notes")
        st.write(evaluation.evaluator_notes)

    if feedback:
        st.write("### Tutor Feedback")
        st.write("#### Teaching Summary")
        st.write(feedback.teaching_summary)
        st.write("#### Key Concepts")
        st.write(feedback.key_concepts)
        st.write("#### Model Answer")
        st.write(feedback.model_answer)
        st.write("#### Practical Rule of Thumb")
        st.write(feedback.practical_rule_of_thumb)
        st.write("#### Next Study Prompt")
        st.write(feedback.next_study_prompt)

elif section == "Review History":
    st.subheader("Review History")
    filter_pillar = st.selectbox("Filter by pillar", ["All"] + curriculum.get_pillars())
    attempts = database.get_recent_attempts(limit=50, pillar_name=filter_pillar)
    if not attempts:
        st.caption("No history found yet.")
    else:
        table_cols = ["response_id", "attempted_at", "pillar_name", "module_name", "title", "overall_score"]
        st.dataframe(pd.DataFrame(attempts)[table_cols], use_container_width=True)
        labels = [f"#{a['response_id']} | {a['attempted_at']} | {a['title']} | Score: {a.get('overall_score', 'N/A')}" for a in attempts]
        selected = attempts[labels.index(st.selectbox("Select attempt", labels))]

        st.write("### Attempt Detail")
        st.write("#### Scenario")
        st.write(selected["scenario_text"])
        st.write("#### Background")
        st.write(selected["background_context"])
        st.write("#### Data")
        st.json(selected["data_points_json"])
        st.write("#### User Response")
        st.write(selected["user_response"])
        st.write("#### Scores")
        st.write({
            "overall": selected.get("overall_score"),
            "problem_diagnosis": selected.get("problem_diagnosis"),
            "statistical_reasoning": selected.get("statistical_reasoning"),
            "tool_application_correctness": selected.get("tool_application_correctness"),
            "tradeoff_awareness": selected.get("tradeoff_awareness"),
            "communication_professionalism": selected.get("communication_professionalism"),
        })
        st.write("#### Evaluator")
        st.write({
            "strengths": selected.get("strengths_json"),
            "weaknesses": selected.get("weaknesses_json"),
            "missed_concepts": selected.get("missed_concepts_json"),
            "incorrect_assumptions": selected.get("incorrect_assumptions_json"),
            "recommended_next_focus": selected.get("recommended_next_focus"),
            "evaluator_notes": selected.get("evaluator_notes"),
        })
        st.write("#### Tutor")
        st.write({
            "teaching_summary": selected.get("teaching_summary"),
            "key_concepts": selected.get("key_concepts_json"),
            "model_answer": selected.get("model_answer"),
            "practical_rule_of_thumb": selected.get("practical_rule_of_thumb"),
            "next_study_prompt": selected.get("next_study_prompt"),
        })

elif section == "Curriculum":
    st.subheader("Curriculum")
    mastery_lookup = {item["concept_name"]: item for item in database.get_weak_concepts(limit=500)}
    for pillar in curriculum.get_all_curriculum():
        st.write(f"## {pillar['pillar']}")
        st.caption(pillar["description"])
        for module in pillar["modules"]:
            st.write(f"### {module['module']}")
            st.caption(module["description"])
            for concept in module["concepts"]:
                record = mastery_lookup.get(concept)
                score = float(record["mastery_score"]) if record else 50.0
                st.write(concept)
                st.progress(int(score), text=f"Mastery: {score:.1f}")

else:
    st.subheader("Settings")
    st.write(f"**API Key Detected:** {'Yes' if get_api_key() else 'No'}")
    st.write(f"**Mock Mode:** {'Enabled' if openai_service.is_mock_mode() else 'Disabled'}")

    model_name = st.text_input("Model name", value=openai_service.model or DEFAULT_MODEL)
    if st.button("Apply Model Override"):
        openai_service.update_model(model_name.strip() or DEFAULT_MODEL)
        st.success(f"Using model: {openai_service.model}")

    st.divider()
    st.write("### Reset Local Database")
    confirm = st.checkbox("I understand this will permanently delete local learning history.")
    if st.button("Reset Database", disabled=not confirm):
        ok = database.reset_database(confirmed=confirm)
        if ok:
            st.cache_resource.clear()
            st.success("Database reset complete. Reloading app state...")
            st.rerun()
        else:
            st.error("Reset aborted. Please confirm first.")
