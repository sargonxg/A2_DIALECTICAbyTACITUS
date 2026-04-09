"""Tests for benchmark question library."""

from dialectica_ontology.benchmark_questions import (
    ALL_QUESTIONS,
    CONFLICT_WARFARE_QUESTIONS,
    CROSS_DOMAIN_QUESTIONS,
    HUMAN_FRICTION_QUESTIONS,
    QUESTION_BY_ID,
    TOTAL_QUESTIONS,
    get_minimum_coverage_questions,
    get_questions_by_difficulty,
    get_questions_by_mode,
    get_questions_by_theory,
    get_questions_for_domain,
)


class TestQuestionLibrary:
    def test_total_questions(self):
        assert TOTAL_QUESTIONS == len(ALL_QUESTIONS)
        assert TOTAL_QUESTIONS >= 30  # At least 30 questions

    def test_cross_domain_questions_exist(self):
        assert len(CROSS_DOMAIN_QUESTIONS) >= 12

    def test_human_friction_questions_exist(self):
        assert len(HUMAN_FRICTION_QUESTIONS) >= 8

    def test_conflict_warfare_questions_exist(self):
        assert len(CONFLICT_WARFARE_QUESTIONS) >= 10

    def test_all_questions_have_unique_ids(self):
        ids = [q.id for q in ALL_QUESTIONS]
        assert len(ids) == len(set(ids))

    def test_question_by_id_lookup(self):
        q = QUESTION_BY_ID.get("cd-esc-01")
        assert q is not None
        assert "Glasl" in q.text

    def test_all_questions_have_required_fields(self):
        for q in ALL_QUESTIONS:
            assert q.id, f"Question missing id"
            assert q.text, f"Question {q.id} missing text"
            assert q.domain, f"Question {q.id} missing domain"
            assert q.mode, f"Question {q.id} missing mode"
            assert q.difficulty, f"Question {q.id} missing difficulty"
            assert q.answer_type, f"Question {q.id} missing answer_type"
            assert q.scoring_rubric, f"Question {q.id} missing scoring_rubric"


class TestQuestionFiltering:
    def test_get_questions_for_human_friction(self):
        questions = get_questions_for_domain("human_friction")
        assert len(questions) > len(CROSS_DOMAIN_QUESTIONS)
        domains = {q.domain for q in questions}
        assert "conflict_warfare" not in domains

    def test_get_questions_for_conflict_warfare(self):
        questions = get_questions_for_domain("conflict_warfare")
        assert len(questions) > len(CROSS_DOMAIN_QUESTIONS)
        domains = {q.domain for q in questions}
        assert "human_friction" not in domains

    def test_get_questions_by_mode(self):
        esc = get_questions_by_mode("escalation")
        assert len(esc) >= 2
        assert all(q.mode == "escalation" for q in esc)

    def test_get_questions_by_theory(self):
        glasl = get_questions_by_theory("glasl")
        assert len(glasl) >= 2
        assert all(q.theory == "glasl" for q in glasl)

    def test_get_questions_by_difficulty(self):
        basic = get_questions_by_difficulty("basic")
        expert = get_questions_by_difficulty("expert")
        assert len(basic) >= 2
        assert len(expert) >= 2

    def test_minimum_coverage_questions(self):
        minimum = get_minimum_coverage_questions()
        assert len(minimum) == 9  # The quality gate set
        modes = {q.mode for q in minimum}
        assert "escalation" in modes
        assert "ripeness" in modes
        assert "trust" in modes
        assert "power" in modes
