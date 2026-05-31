"""SQLite persistence layer for CSSGB app."""

from __future__ import annotations

import json
import sqlite3
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from config import DATABASE_PATH
from core.curriculum import CurriculumManager
from core.models import Evaluation, Scenario, TutorFeedback


class DatabaseManager:
    """Encapsulates all local persistence behavior."""

    def __init__(self, db_path: Path = DATABASE_PATH) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _now_iso() -> str:
        return datetime.utcnow().isoformat()

    @staticmethod
    def _json_dump(value: Any) -> str:
        return json.dumps(value or [])

    @staticmethod
    def _json_load(value: Optional[str], default: Any) -> Any:
        if value is None:
            return default
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return default

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS pillars (id INTEGER PRIMARY KEY, name TEXT, description TEXT);
                CREATE TABLE IF NOT EXISTS modules (id INTEGER PRIMARY KEY, pillar_name TEXT, module_name TEXT, description TEXT);
                CREATE TABLE IF NOT EXISTS concept_mastery (
                    id INTEGER PRIMARY KEY, pillar_name TEXT, module_name TEXT, concept_name TEXT,
                    mastery_score REAL, attempts INTEGER, last_seen TEXT, created_at TEXT, updated_at TEXT
                );
                CREATE TABLE IF NOT EXISTS scenarios (
                    id INTEGER PRIMARY KEY, pillar_name TEXT, module_name TEXT, difficulty TEXT, title TEXT,
                    scenario_text TEXT, background_context TEXT, data_points_json TEXT, primary_concepts_json TEXT,
                    ideal_reasoning_targets_json TEXT, created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY, scenario_id INTEGER, user_response TEXT, created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS evaluations (
                    id INTEGER PRIMARY KEY, response_id INTEGER, overall_score INTEGER, problem_diagnosis INTEGER,
                    statistical_reasoning INTEGER, tool_application_correctness INTEGER, tradeoff_awareness INTEGER,
                    communication_professionalism INTEGER, strengths_json TEXT, weaknesses_json TEXT,
                    missed_concepts_json TEXT, incorrect_assumptions_json TEXT, recommended_next_focus TEXT,
                    evaluator_notes TEXT, created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS tutor_feedback (
                    id INTEGER PRIMARY KEY, response_id INTEGER, teaching_summary TEXT, key_concepts_json TEXT,
                    model_answer TEXT, practical_rule_of_thumb TEXT, next_study_prompt TEXT, created_at TEXT
                );
                CREATE TABLE IF NOT EXISTS daily_recommendations (
                    id INTEGER PRIMARY KEY, date TEXT, pillar_name TEXT, module_name TEXT, concept_name TEXT,
                    reason TEXT, created_at TEXT
                );
                """
            )
            conn.commit()
        self.seed_curriculum_if_empty(CurriculumManager())

    def seed_curriculum_if_empty(self, curriculum: CurriculumManager) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(1) AS c FROM pillars")
            if cur.fetchone()["c"] > 0:
                return
            for pillar in curriculum.get_all_curriculum():
                cur.execute("INSERT INTO pillars(name, description) VALUES (?, ?)", (pillar["pillar"], pillar["description"]))
                for module in pillar["modules"]:
                    cur.execute(
                        "INSERT INTO modules(pillar_name, module_name, description) VALUES (?, ?, ?)",
                        (pillar["pillar"], module["module"], module["description"]),
                    )
                    for concept in module["concepts"]:
                        ts = self._now_iso()
                        cur.execute(
                            """
                            INSERT INTO concept_mastery(
                                pillar_name, module_name, concept_name, mastery_score,
                                attempts, last_seen, created_at, updated_at
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (pillar["pillar"], module["module"], concept, 50.0, 0, "", ts, ts),
                        )
            conn.commit()

    def save_scenario(self, scenario: Scenario) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO scenarios(
                    pillar_name, module_name, difficulty, title, scenario_text, background_context,
                    data_points_json, primary_concepts_json, ideal_reasoning_targets_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    scenario.pillar,
                    scenario.module,
                    scenario.difficulty,
                    scenario.title,
                    scenario.scenario_text,
                    scenario.background_context,
                    self._json_dump(scenario.data_points),
                    self._json_dump(scenario.primary_concepts),
                    self._json_dump(scenario.ideal_reasoning_targets),
                    self._now_iso(),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def save_response(self, scenario_id: int, user_response: str) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO responses(scenario_id, user_response, created_at) VALUES (?, ?, ?)", (scenario_id, user_response, self._now_iso()))
            conn.commit()
            return int(cur.lastrowid)

    def save_evaluation(self, response_id: int, evaluation: Evaluation) -> int:
        scores = evaluation.dimension_scores
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO evaluations(
                    response_id, overall_score, problem_diagnosis, statistical_reasoning,
                    tool_application_correctness, tradeoff_awareness, communication_professionalism,
                    strengths_json, weaknesses_json, missed_concepts_json, incorrect_assumptions_json,
                    recommended_next_focus, evaluator_notes, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response_id,
                    evaluation.overall_score,
                    int(scores.get("problem_diagnosis", 0)),
                    int(scores.get("statistical_reasoning", 0)),
                    int(scores.get("tool_application_correctness", 0)),
                    int(scores.get("tradeoff_awareness", 0)),
                    int(scores.get("communication_professionalism", 0)),
                    self._json_dump(evaluation.strengths),
                    self._json_dump(evaluation.weaknesses),
                    self._json_dump(evaluation.missed_concepts),
                    self._json_dump(evaluation.incorrect_assumptions),
                    evaluation.recommended_next_focus,
                    evaluation.evaluator_notes,
                    self._now_iso(),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def save_tutor_feedback(self, response_id: int, feedback: TutorFeedback) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                INSERT INTO tutor_feedback(
                    response_id, teaching_summary, key_concepts_json, model_answer,
                    practical_rule_of_thumb, next_study_prompt, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    response_id,
                    feedback.teaching_summary,
                    self._json_dump(feedback.key_concepts),
                    feedback.model_answer,
                    feedback.practical_rule_of_thumb,
                    feedback.next_study_prompt,
                    self._now_iso(),
                ),
            )
            conn.commit()
            return int(cur.lastrowid)

    def get_recent_scores_for_concept(self, concept_name: str, limit: int = 2) -> List[int]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT e.overall_score
                FROM evaluations e
                JOIN responses r ON r.id = e.response_id
                JOIN scenarios s ON s.id = r.scenario_id
                WHERE s.primary_concepts_json LIKE ?
                ORDER BY e.id DESC
                LIMIT ?
                """,
                (f'%"{concept_name}"%', limit),
            )
            return [int(row["overall_score"]) for row in cur.fetchall()]

    def get_concept_mastery_record(self, concept_name: str) -> Optional[sqlite3.Row]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM concept_mastery WHERE concept_name = ? LIMIT 1", (concept_name,))
            return cur.fetchone()

    def update_concept_mastery(self, concept_name: str, new_score: float, last_seen: str, attempts_inc: int = 1) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                UPDATE concept_mastery
                SET mastery_score = ?, attempts = attempts + ?, last_seen = ?, updated_at = ?
                WHERE concept_name = ?
                """,
                (float(new_score), attempts_inc, last_seen, self._now_iso(), concept_name),
            )
            conn.commit()

    def get_weak_concepts(self, limit: int = 5) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT pillar_name, module_name, concept_name, mastery_score, attempts
                FROM concept_mastery
                ORDER BY mastery_score ASC, attempts DESC
                LIMIT ?
                """,
                (limit,),
            )
            return [dict(row) for row in cur.fetchall()]

    def get_average_scores_by_pillar(self) -> List[Dict[str, Any]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT s.pillar_name, AVG(e.overall_score) AS avg_score
                FROM evaluations e
                JOIN responses r ON r.id = e.response_id
                JOIN scenarios s ON s.id = r.scenario_id
                GROUP BY s.pillar_name
                ORDER BY s.pillar_name
                """
            )
            return [{"pillar_name": row["pillar_name"], "avg_score": round(float(row["avg_score"] or 0), 2)} for row in cur.fetchall()]

    def get_total_practice_count(self) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT COUNT(1) AS c FROM responses")
            return int(cur.fetchone()["c"])

    def get_recent_attempts(self, limit: int = 10, pillar_name: Optional[str] = None) -> List[Dict[str, Any]]:
        query = """
            SELECT r.id AS response_id, r.created_at AS attempted_at, s.title, s.pillar_name, s.module_name,
                   e.overall_score, e.problem_diagnosis, e.statistical_reasoning,
                   e.tool_application_correctness, e.tradeoff_awareness, e.communication_professionalism,
                   r.user_response, s.scenario_text, s.background_context, s.data_points_json,
                   e.strengths_json, e.weaknesses_json, e.missed_concepts_json,
                   e.incorrect_assumptions_json, e.recommended_next_focus, e.evaluator_notes,
                   t.teaching_summary, t.key_concepts_json, t.model_answer, t.practical_rule_of_thumb, t.next_study_prompt
            FROM responses r
            JOIN scenarios s ON s.id = r.scenario_id
            LEFT JOIN evaluations e ON e.response_id = r.id
            LEFT JOIN tutor_feedback t ON t.response_id = r.id
        """
        params: List[Any] = []
        if pillar_name and pillar_name != "All":
            query += " WHERE s.pillar_name = ?"
            params.append(pillar_name)
        query += " ORDER BY r.id DESC LIMIT ?"
        params.append(limit)

        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(query, params)
            items = []
            for row in cur.fetchall():
                item = dict(row)
                for key, default in [
                    ("data_points_json", {}),
                    ("strengths_json", []),
                    ("weaknesses_json", []),
                    ("missed_concepts_json", []),
                    ("incorrect_assumptions_json", []),
                    ("key_concepts_json", []),
                ]:
                    item[key] = self._json_load(item.get(key), default)
                items.append(item)
            return items

    def get_daily_recommendation(self, for_date: Optional[str] = None) -> Optional[Dict[str, Any]]:
        target_date = for_date or date.today().isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT pillar_name, module_name, concept_name, reason FROM daily_recommendations WHERE date = ? ORDER BY id DESC LIMIT 1",
                (target_date,),
            )
            row = cur.fetchone()
            return dict(row) if row else None

    def save_daily_recommendation(self, pillar_name: str, module_name: str, concept_name: str, reason: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO daily_recommendations(date, pillar_name, module_name, concept_name, reason, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                (date.today().isoformat(), pillar_name, module_name, concept_name, reason, self._now_iso()),
            )
            conn.commit()

    def reset_database(self, confirmed: bool) -> bool:
        if not confirmed:
            return False
        if self.db_path.exists():
            self.db_path.unlink()
        self._init_db()
        return True
