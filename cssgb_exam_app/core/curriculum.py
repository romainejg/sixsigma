"""ASQ CSSGB curriculum manager."""

from __future__ import annotations

from typing import Dict, List


class CurriculumManager:
    """Provides structured access to CSSGB curriculum data."""

    def __init__(self) -> None:
        self._curriculum: List[Dict[str, object]] = [
            {
                "pillar": "Define Phase",
                "description": "Project framing, VOC translation, and governance.",
                "modules": [
                    {
                        "module": "Project Charter & Metrics",
                        "description": "Defines project intent and measurable success.",
                        "concepts": ["Problem Statement", "Business Case", "Goal Statement", "Project Scope", "Milestones", "Primary Metrics"],
                    },
                    {
                        "module": "Voice of the Customer (VOC)",
                        "description": "Converts customer needs into CTQs.",
                        "concepts": ["Customer Identification", "VOC Data Collection", "Critical to Quality [CTQ] Flowdown", "Kano Model"],
                    },
                    {
                        "module": "Project Management Tools",
                        "description": "Execution planning and stakeholder alignment.",
                        "concepts": ["Gantt Charts", "RACI Matrix", "Risk Analysis", "Stakeholder Analysis", "Communication Plans"],
                    },
                ],
            },
            {
                "pillar": "Measure Phase",
                "description": "Measurement planning and baseline capability analysis.",
                "modules": [
                    {
                        "module": "Process Metrics & Analysis",
                        "description": "Maps value flow and process behavior.",
                        "concepts": ["Process Mapping", "SIPOC", "Value Stream Mapping", "Flowcharts", "Spaghetti Diagrams"],
                    },
                    {
                        "module": "Data Collection & Statistics",
                        "description": "Data foundations and descriptive statistics.",
                        "concepts": ["Sampling Plans", "Data Types", "Central Tendency", "Dispersion", "Graphical Tools"],
                    },
                    {
                        "module": "Measurement Systems Analysis (MSA)",
                        "description": "Ensures measurement system reliability.",
                        "concepts": ["Gage R&R", "Repeatability", "Reproducibility", "Bias", "Linearity", "Stability", "Attribute MSA"],
                    },
                    {
                        "module": "Process Capability",
                        "description": "Quantifies process performance against specs.",
                        "concepts": ["Cp", "Cpk", "Pp", "Ppk", "Process Performance Metrics", "DPMO", "Sigma Level Calculation"],
                    },
                ],
            },
            {
                "pillar": "Analyze Phase",
                "description": "Root cause identification and statistical validation.",
                "modules": [
                    {
                        "module": "Exploratory Data Analysis",
                        "description": "Trend and relationship exploration.",
                        "concepts": ["Multi-Vari Studies", "Correlation Coefficients", "Simple Linear Regression"],
                    },
                    {
                        "module": "Hypothesis Testing",
                        "description": "Inferential statistics for decision making.",
                        "concepts": ["Type I & II Errors", "p-values", "t-tests", "ANOVA", "Chi-Square Tests", "Non-parametric testing parameters"],
                    },
                    {
                        "module": "Root Cause Analysis",
                        "description": "Structured RCA for verified causes.",
                        "concepts": ["5 Whys", "Fishbone [Ishikawa] Diagram", "Failure Mode and Effects Analysis [FMEA]", "Pareto Analysis"],
                    },
                ],
            },
            {
                "pillar": "Improve Phase",
                "description": "Solution development and implementation.",
                "modules": [
                    {
                        "module": "Lean Tools & Waste Elimination",
                        "description": "Flow and waste reduction methods.",
                        "concepts": ["5S", "Poka-Yoke [Mistake Proofing]", "Kaizen", "SMED", "Kanban", "Jidoka"],
                    },
                    {
                        "module": "Solution Selection & Implementation",
                        "description": "Selecting and deploying robust solutions.",
                        "concepts": ["Prioritization Matrix", "Pugh Matrix", "Pilot Testing", "Change Management"],
                    },
                ],
            },
            {
                "pillar": "Control Phase",
                "description": "Sustain gains using controls and standards.",
                "modules": [
                    {
                        "module": "Statistical Process Control (SPC)",
                        "description": "Control charting and reaction planning.",
                        "concepts": ["Common vs. Special Cause Variation", "Control Chart Selection [X-bar R, X-bar S, I-MR, p, c, u, np]", "Control Plan Development"],
                    },
                    {
                        "module": "Sustainment & Documentation",
                        "description": "Operationalization and knowledge retention.",
                        "concepts": ["Standard Operating Procedures [SOPs]", "Visual Factory", "Lesson Learned Capture"],
                    },
                ],
            },
        ]

    def get_pillars(self) -> List[str]:
        return [item["pillar"] for item in self._curriculum]

    def get_modules_by_pillar(self, pillar_name: str) -> List[str]:
        for pillar in self._curriculum:
            if pillar["pillar"] == pillar_name:
                return [mod["module"] for mod in pillar["modules"]]
        return []

    def get_concepts_by_module(self, pillar_name: str, module_name: str) -> List[str]:
        for pillar in self._curriculum:
            if pillar["pillar"] != pillar_name:
                continue
            for module in pillar["modules"]:
                if module["module"] == module_name:
                    return list(module["concepts"])
        return []

    def get_all_curriculum(self) -> List[Dict[str, object]]:
        return self._curriculum
