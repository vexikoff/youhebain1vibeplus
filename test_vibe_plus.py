import unittest
from unittest.mock import Mock, patch
from vibe_plus import default_state, normalize_state, CHAPTERS, run


class TestDefaultState(unittest.TestCase):
    def test_structure(self):
        state = default_state()
        expected_keys = {"version", "chapter", "route", "origin_route", "approach", "ending", "exam_progress", "side_quest", "trust_level", "evidence", "archive_policy"}
        self.assertEqual(set(state.keys()), expected_keys)

    def test_values(self):
        state = default_state()
        self.assertEqual(state["version"], 5)
        self.assertEqual(state["chapter"], 0)
        self.assertEqual(state["route"], "")
        self.assertEqual(state["origin_route"], "")
        self.assertEqual(state["approach"], "")
        self.assertEqual(state["ending"], "")
        self.assertEqual(state["exam_progress"], 0)
        self.assertIsNone(state["side_quest"])
        self.assertEqual(state["trust_level"], 0)
        self.assertEqual(state["evidence"], 0)
        self.assertIsNone(state["archive_policy"])


class TestNormalizeState(unittest.TestCase):
    def test_valid_full_state(self):
        state = {
            "version": 5,
            "chapter": 5,
            "route": "standard",
            "origin_route": "premium",
            "approach": "premium",
            "ending": "Test",
            "exam_progress": 2,
            "side_quest": "completed",
            "trust_level": 3,
            "evidence": 10,
            "archive_policy": "restricted",
        }
        normalized = normalize_state(state)
        self.assertEqual(normalized, state)

    def test_invalid_chapter_high(self):
        state = {"version": 1, "chapter": 99, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)

    def test_invalid_chapter_negative(self):
        state = {"version": 1, "chapter": -5, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)

    def test_invalid_type(self):
        self.assertEqual(normalize_state("invalid"), default_state())
        self.assertEqual(normalize_state(123), default_state())
        self.assertEqual(normalize_state(None), default_state())
        self.assertEqual(normalize_state([1, 2]), default_state())

    def test_missing_fields(self):
        state = {"chapter": 1}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 5)
        self.assertEqual(normalized["chapter"], 1)
        self.assertEqual(normalized["route"], "")
        self.assertEqual(normalized["origin_route"], "")
        self.assertEqual(normalized["approach"], "")
        self.assertEqual(normalized["ending"], "")
        self.assertEqual(normalized["exam_progress"], 0)
        self.assertIsNone(normalized["side_quest"])
        self.assertEqual(normalized["trust_level"], 0)
        self.assertEqual(normalized["evidence"], 0)
        self.assertIsNone(normalized["archive_policy"])


class TestChapterBounds(unittest.TestCase):
    def test_all_chapters_in_range(self):
        for i in range(len(CHAPTERS)):
            state = {"version": 5, "chapter": i, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
            normalized = normalize_state(state)
            self.assertEqual(normalized["chapter"], i)

    def test_chapter_boundary_0(self):
        state = {"version": 5, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)

    def test_chapter_boundary_max(self):
        max_chapter = len(CHAPTERS) - 1
        state = {"version": 5, "chapter": max_chapter, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], max_chapter)

    def test_chapter_above_max(self):
        state = {"version": 1, "chapter": 999, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)

    def test_chapter_negative(self):
        state = {"version": 1, "chapter": -1, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)


class TestVersionMigration(unittest.TestCase):
    def test_version_5_default(self):
        state = {"version": 5, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 5)

    def test_version_3_chapter_16_migration(self):
        state = {"version": 3, "chapter": 16, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 19)
        self.assertEqual(normalized["version"], 5)

    def test_version_3_chapter_17_migration(self):
        state = {"version": 3, "chapter": 17, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 19)
        self.assertEqual(normalized["version"], 5)

    def test_version_2_chapter_14_migration(self):
        state = {"version": 2, "chapter": 14, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 16)
        self.assertEqual(normalized["version"], 5)

    def test_version_2_chapter_15_migration(self):
        state = {"version": 2, "chapter": 15, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 19)
        self.assertEqual(normalized["version"], 5)

    def test_version_1_chapter_11_migration(self):
        state = {"version": 1, "chapter": 11, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 13)
        self.assertEqual(normalized["version"], 5)

    def test_version_4_chapter_16_stays_before_archive(self):
        state = {"version": 4, "chapter": 16, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 16)
        self.assertEqual(normalized["version"], 5)

    def test_version_4_response_chapter_moves_after_archive(self):
        state = {"version": 4, "chapter": 17, "route": "", "origin_route": "", "approach": "", "ending": "refund", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 18)
        self.assertEqual(normalized["ending"], "refund")

    def test_version_4_final_chapter_moves_after_archive(self):
        state = {"version": 4, "chapter": 18, "route": "", "origin_route": "", "approach": "", "ending": "company_accepted", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 19)
        self.assertEqual(normalized["ending"], "company_accepted")


class TestArchivePolicy(unittest.TestCase):
    def test_allowed_policies_are_preserved(self):
        policies = (
            "public_consented",
            "consent_pending",
            "restricted",
            "summary_only",
            "skipped",
        )
        for policy in policies:
            state = default_state()
            state["archive_policy"] = policy
            self.assertEqual(normalize_state(state)["archive_policy"], policy)

    def test_invalid_policy_is_cleared(self):
        state = default_state()
        state["archive_policy"] = "public_without_consent"
        self.assertIsNone(normalize_state(state)["archive_policy"])


class TestExamProgressBounds(unittest.TestCase):
    def test_all_progress_in_range(self):
        for i in range(4):
            state = {"version": 1, "chapter": 3, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": i, "side_quest": None, "trust_level": 0, "evidence": 0}
            normalized = normalize_state(state)
            self.assertEqual(normalized["exam_progress"], i)

    def test_progress_above_max(self):
        state = {"version": 1, "chapter": 3, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 10, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["exam_progress"], 0)

    def test_progress_negative(self):
        state = {"version": 1, "chapter": 3, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": -1, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["exam_progress"], 0)


class TestTrustLevelBounds(unittest.TestCase):
    def test_all_levels_in_range(self):
        for i in range(5):
            state = {"version": 1, "chapter": 1, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": i, "evidence": 0}
            normalized = normalize_state(state)
            self.assertEqual(normalized["trust_level"], i)

    def test_trust_above_max(self):
        state = {"version": 1, "chapter": 1, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 10, "evidence": 0}
        self.assertEqual(normalize_state(state)["trust_level"], 0)

    def test_trust_negative(self):
        state = {"version": 1, "chapter": 1, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": -1, "evidence": 0}
        self.assertEqual(normalize_state(state)["trust_level"], 0)


class TestSideQuest(unittest.TestCase):
    def test_none_value(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertIsNone(normalize_state(state)["side_quest"])

    def test_completed_value(self):
        state = {"version": 1, "chapter": 7, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": "completed", "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["side_quest"], "completed")

    def test_invalid_type(self):
        state = {"version": 1, "chapter": 7, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": 123, "trust_level": 0, "evidence": 0}
        self.assertIsNone(normalize_state(state)["side_quest"])

    def test_string_value(self):
        state = {"version": 1, "chapter": 7, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": "any_string", "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["side_quest"], "any_string")


class TestEvidenceField(unittest.TestCase):
    def test_valid_evidence(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 42}
        normalized = normalize_state(state)
        self.assertEqual(normalized["evidence"], 42)

    def test_evidence_zero(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["evidence"], 0)

    def test_evidence_negative(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": -10}
        normalized = normalize_state(state)
        self.assertEqual(normalized["evidence"], 0)

    def test_evidence_invalid_type(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": "not_a_number"}
        normalized = normalize_state(state)
        self.assertEqual(normalized["evidence"], 0)

    def test_evidence_boolean(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": True}
        normalized = normalize_state(state)
        self.assertEqual(normalized["evidence"], 0)


class TestOriginRoute(unittest.TestCase):
    def test_valid_origin_route(self):
        state = {"version": 1, "chapter": 0, "route": "standard", "origin_route": "premium", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["origin_route"], "premium")

    def test_invalid_origin_route_type(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": 123, "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["origin_route"], "")


class TestApproach(unittest.TestCase):
    def test_valid_approach(self):
        state = {"version": 1, "chapter": 0, "route": "standard", "origin_route": "", "approach": "premium", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["approach"], "premium")

    def test_invalid_approach_type(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": 123, "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["approach"], "")


class TestRouteVariants(unittest.TestCase):
    def test_all_existing_routes(self):
        existing_routes = ["", "standard", "premium", "exam", "blind_sign", "exam_passed", "full_text", "honest", "blame", "refuse", "appeal", "settlement", "bank", "regulator", "union", "press", "exploit", "refund"]
        for route in existing_routes:
            state = {"version": 1, "chapter": 1, "route": route, "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
            normalized = normalize_state(state)
            self.assertEqual(normalized["route"], route)

    def test_invalid_route_type(self):
        state = {"version": 1, "chapter": 1, "route": 123, "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["route"], "")


class TestEnding(unittest.TestCase):
    def test_empty_ending(self):
        state = {"version": 1, "chapter": 1, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["ending"], "")

    def test_ending_with_text(self):
        state = {"version": 1, "chapter": 11, "route": "", "origin_route": "", "approach": "", "ending": "Подписка оформлена", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["ending"], "Подписка оформлена")

    def test_invalid_ending_type(self):
        state = {"version": 1, "chapter": 11, "route": "", "origin_route": "", "approach": "", "ending": 123, "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["ending"], "")


class TestVersionField(unittest.TestCase):
    def test_version_normalized_to_5(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 5)

    def test_version_4_upgraded_to_5(self):
        state = {"version": 4, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 5)

    def test_version_5_preserved(self):
        state = {"version": 5, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 5)

    def test_version_invalid_type(self):
        state = {"version": "invalid", "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 5)


class TestMigrationFromOldFormat(unittest.TestCase):
    def test_old_format_with_main_fields(self):
        old = {"chapter": 2, "route": "exam", "ending": "test"}
        new = normalize_state(old)
        self.assertEqual(new["version"], 5)
        self.assertEqual(new["chapter"], 2)
        self.assertEqual(new["route"], "exam")
        self.assertEqual(new["origin_route"], "")
        self.assertEqual(new["approach"], "")
        self.assertEqual(new["ending"], "test")
        self.assertEqual(new["exam_progress"], 0)
        self.assertIsNone(new["side_quest"])
        self.assertEqual(new["trust_level"], 0)
        self.assertEqual(new["evidence"], 0)
        self.assertIsNone(new["archive_policy"])

    def test_old_format_minimal(self):
        old = {"chapter": 1}
        new = normalize_state(old)
        self.assertEqual(new["version"], 5)
        self.assertEqual(new["chapter"], 1)
        self.assertEqual(new["route"], "")
        self.assertEqual(new["origin_route"], "")
        self.assertEqual(new["approach"], "")
        self.assertEqual(new["ending"], "")
        self.assertEqual(new["exam_progress"], 0)
        self.assertIsNone(new["side_quest"])
        self.assertEqual(new["trust_level"], 0)
        self.assertEqual(new["evidence"], 0)
        self.assertIsNone(new["archive_policy"])


class TestNewChapters(unittest.TestCase):
    def test_chapter_14_interrogation(self):
        state = {"version": 5, "chapter": 14, "route": "bank", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 5}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 14)

    def test_chapter_15_preparation(self):
        state = {"version": 5, "chapter": 15, "route": "bank", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 5}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 15)

    def test_chapter_16_hearing(self):
        state = {"version": 5, "chapter": 16, "route": "bank", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 5}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 16)

    def test_chapter_17_archive(self):
        state = {"version": 5, "chapter": 17, "route": "", "origin_route": "", "approach": "", "ending": "refund", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 5}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 17)

    def test_chapter_18_response(self):
        state = {"version": 5, "chapter": 18, "route": "", "origin_route": "", "approach": "", "ending": "refund", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 18)

    def test_chapter_19_closed(self):
        state = {"version": 5, "chapter": 19, "route": "", "origin_route": "", "approach": "", "ending": "Вы закрыли досье", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 19)


class TestArchiveChapter(unittest.TestCase):
    def play(self, state, choice, points=200):
        with patch("vibe_plus.Prompt.ask", return_value=choice):
            return run(Mock(), points, 10, state)

    def test_archive_choices_store_distinct_policies(self):
        expected_policies = {
            "1": "public_consented",
            "2": "consent_pending",
            "3": "restricted",
            "4": "summary_only",
            "5": "skipped",
        }
        for choice, policy in expected_policies.items():
            state = default_state()
            state.update(chapter=17, evidence=2, trust_level=2)
            points, result = self.play(state, choice)
            self.assertEqual(result["chapter"], 18)
            self.assertEqual(result["archive_policy"], policy)
            self.assertEqual(result["evidence"], 2)
            self.assertEqual(result["trust_level"], 2)
            self.assertEqual(points, 200)

    def test_publication_waits_for_evidence_and_trust(self):
        state = default_state()
        state.update(chapter=17, evidence=3, trust_level=1)
        _, result = self.play(state, "1")
        self.assertEqual(result["archive_policy"], "consent_pending")

    def test_archive_policies_unlock_distinct_late_endings(self):
        cases = (
            ("public_consented", 2, "1", "consented_archive"),
            ("restricted", 2, "2", "protected_archive"),
            ("summary_only", 1, "3", "anonymous_summary"),
        )
        for policy, trust, choice, ending in cases:
            state = default_state()
            state.update(
                chapter=18,
                ending="refund",
                evidence=2,
                trust_level=trust,
                archive_policy=policy,
            )
            points, result = self.play(state, choice)
            self.assertEqual(result["chapter"], 19)
            self.assertEqual(result["ending"], ending)
            self.assertEqual(points, 200)

    def test_low_evidence_or_trust_keeps_existing_outcome(self):
        state = default_state()
        state.update(
            chapter=18,
            ending="refund",
            evidence=1,
            trust_level=1,
            archive_policy="public_consented",
        )
        _, result = self.play(state, "1")
        self.assertEqual(result["ending"], "company_accepted")

    def test_skipping_archive_without_side_quest_still_closes_dlc(self):
        state = default_state()
        state.update(chapter=17, evidence=0, trust_level=0)
        points, state = self.play(state, "5")
        self.assertIsNone(state["side_quest"])
        self.assertEqual(state["chapter"], 18)
        self.assertEqual(state["archive_policy"], "skipped")

        points, result = self.play(state, "1", points)
        self.assertEqual(result["chapter"], 19)
        self.assertEqual(result["ending"], "company_accepted")
        self.assertEqual(points, 200)


if __name__ == "__main__":
    unittest.main()
