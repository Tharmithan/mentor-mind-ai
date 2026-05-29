"""Question database loader (Week 5 · Day 1)."""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from app.interview.types import InterviewType

DATA_PATH = Path(__file__).resolve().parent / "data" / "questions.json"


@dataclass
class InterviewQuestion:
    id: str
    text: str
    category: str
    difficulty: str
    tips: str
    interview_type: str
    expected_keywords: list[str] | None = None
    ideal_answer: str = ""

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "text": self.text,
            "category": self.category,
            "difficulty": self.difficulty,
            "tips": self.tips,
            "interview_type": self.interview_type,
            "expected_keywords": self.expected_keywords or [],
            "ideal_answer": self.ideal_answer,
        }


class QuestionBank:
    def __init__(self, path: Path = DATA_PATH) -> None:
        raw = json.loads(path.read_text(encoding="utf-8"))
        self._by_type: dict[str, list[InterviewQuestion]] = {}
        for itype, items in raw.items():
            self._by_type[itype] = []
            for q in items:
                self._by_type[itype].append(
                    InterviewQuestion(
                        id=q["id"],
                        text=q["text"],
                        category=q["category"],
                        difficulty=q["difficulty"],
                        tips=q["tips"],
                        interview_type=itype,
                        expected_keywords=q.get("expected_keywords"),
                        ideal_answer=q.get("ideal_answer", ""),
                    )
                )

    def list_types(self) -> list[str]:
        return list(self._by_type.keys())

    def count(self, interview_type: str) -> int:
        return len(self._by_type.get(interview_type, []))

    def pick(self, interview_type: str, n: int) -> list[InterviewQuestion]:
        pool = self._by_type.get(interview_type, [])
        if not pool:
            raise ValueError(f"Unknown interview type: {interview_type}")
        return random.sample(pool, min(n, len(pool)))

    def get_by_id(self, question_id: str) -> InterviewQuestion | None:
        for questions in self._by_type.values():
            for q in questions:
                if q.id == question_id:
                    return q
        return None

    def all_for_type(self, interview_type: str) -> list[InterviewQuestion]:
        return list(self._by_type.get(interview_type, []))


_bank: QuestionBank | None = None


def get_question_bank() -> QuestionBank:
    global _bank
    if _bank is None:
        _bank = QuestionBank()
    return _bank
