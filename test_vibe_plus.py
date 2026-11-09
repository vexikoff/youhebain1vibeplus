import json
import unittest
from unittest.mock import Mock, patch
from vibe_plus import (
    CHAPTERS,
    CONTINUATION_ENDINGS,
    CONTINUATION_OPTIONS,
    EPILOGUE_OPTIONS,
    EPILOGUE_RESULT_TEXT,
    default_state,
    normalize_state,
    run,
)


class TestDefaultState(unittest.TestCase):
    def test_structure(self):
        state = default_state()
        expected_keys = {
            "version", "chapter", "route", "origin_route", "approach", "ending",
            "exam_progress", "side_quest", "trust_level", "evidence", "archive_policy",
            "previous_ending", "continuation", "continuation_result",
            "continuation_ending",
            "epilogue", "epilogue_progress", "epilogue_active",
            "epilogue_result",
        }
        self.assertEqual(set(state.keys()), expected_keys)

    def test_values(self):
        state = default_state()
        self.assertEqual(state["version"], 8)
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
        self.assertEqual(state["previous_ending"], "")
        self.assertEqual(
            state["continuation"],
            {name: None for name in CONTINUATION_OPTIONS},
        )
        self.assertEqual(state["continuation_result"], "")
        self.assertEqual(state["continuation_ending"], "")
        self.assertEqual(state["epilogue"], {name: None for name in EPILOGUE_OPTIONS})
        self.assertEqual(state["epilogue_progress"], 0)
        self.assertFalse(state["epilogue_active"])
        self.assertEqual(state["epilogue_result"], "")


class TestNormalizeState(unittest.TestCase):
    def test_valid_full_state(self):
        state = {
            "version": 8,
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
            "previous_ending": "company_accepted",
            "continuation": default_state()["continuation"],
            "continuation_result": "",
            "continuation_ending": "",
            "epilogue": default_state()["epilogue"],
            "epilogue_progress": 0,
            "epilogue_active": False,
            "epilogue_result": "",
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
        self.assertEqual(normalized["version"], 8)
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
        self.assertEqual(normalized["previous_ending"], "")
        self.assertEqual(normalized["continuation_result"], "")
        self.assertEqual(normalized["continuation_ending"], "")
        self.assertEqual(normalized["epilogue"], {name: None for name in EPILOGUE_OPTIONS})
        self.assertEqual(normalized["epilogue_progress"], 0)
        self.assertFalse(normalized["epilogue_active"])
        self.assertEqual(normalized["epilogue_result"], "")

    def test_invalid_continuation_values_are_discarded(self):
        state = default_state()
        state.update(
            previous_ending=["not", "text"],
            continuation={"letter": ["not", "an", "option"]},
            continuation_result=["not", "a", "result"],
            continuation_ending=["not", "an", "ending"],
            epilogue=["not", "a", "dictionary"],
            epilogue_progress=True,
            epilogue_active="yes",
            epilogue_result=["not", "a", "result"],
        )
        normalized = normalize_state(state)
        self.assertEqual(normalized["previous_ending"], "")
        self.assertIsNone(normalized["continuation"]["letter"])
        self.assertEqual(normalized["continuation_result"], "")
        self.assertEqual(normalized["continuation_ending"], "")
        self.assertEqual(normalized["epilogue"], {name: None for name in EPILOGUE_OPTIONS})
        self.assertEqual(normalized["epilogue_progress"], 0)
        self.assertFalse(normalized["epilogue_active"])
        self.assertEqual(normalized["epilogue_result"], "")


class TestChapterBounds(unittest.TestCase):
    def test_all_chapters_in_range(self):
        for i in range(len(CHAPTERS)):
            state = {"version": 8, "chapter": i, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
            normalized = normalize_state(state)
            self.assertEqual(normalized["chapter"], i)

    def test_chapter_boundary_0(self):
        state = {"version": 8, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)

    def test_chapter_boundary_max(self):
        max_chapter = len(CHAPTERS) - 1
        state = {"version": 8, "chapter": max_chapter, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], max_chapter)

    def test_chapter_above_max(self):
        state = {"version": 1, "chapter": 999, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)

    def test_chapter_negative(self):
        state = {"version": 1, "chapter": -1, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        self.assertEqual(normalize_state(state)["chapter"], 0)


class TestVersionMigration(unittest.TestCase):
    def test_version_6_unfinished_state_migrates(self):
        state = {"version": 6, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 8)
        self.assertEqual(normalized["chapter"], 0)

    def test_version_6_completed_chatgpt_state_moves_to_final_screen(self):
        state = {
            "version": 6,
            "chapter": CHAPTERS.index("План последствий") + 1,
            "route": "bank",
            "origin_route": "bank",
            "approach": "standard",
            "ending": "company_accepted",
            "exam_progress": 0,
            "side_quest": "subscriber_testimony",
            "trust_level": 3,
            "evidence": 4,
            "archive_policy": "public_consented",
            "previous_ending": "company_accepted",
            "continuation": default_state()["continuation"],
            "continuation_result": "compliance_monitored",
        }
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        for field in (
            "ending",
            "route",
            "origin_route",
            "side_quest",
            "trust_level",
            "evidence",
            "archive_policy",
            "previous_ending",
            "continuation_result",
        ):
            self.assertEqual(normalized[field], state[field])

    def test_version_7_mistral_final_and_progress_survive_migration(self):
        state = default_state()
        state.update(
            version=7,
            chapter=CHAPTERS.index("Досье закрыто"),
            ending="company_accepted",
            previous_ending="company_accepted",
            continuation_ending="independent_oversight",
            epilogue={
                "flash_drive": "returned",
                "last_payment": "reconciled",
                "former_agent": "testimony",
                "fix_check": None,
                "paper_box": None,
            },
            epilogue_progress=3,
            epilogue_active=True,
        )
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(normalized["version"], 8)
        self.assertEqual(normalized["ending"], "company_accepted")
        self.assertEqual(normalized["previous_ending"], "company_accepted")
        self.assertEqual(normalized["continuation_ending"], "independent_oversight")
        self.assertEqual(normalized["epilogue"], state["epilogue"])
        self.assertEqual(normalized["epilogue_progress"], 3)
        self.assertTrue(normalized["epilogue_active"])

    def test_version_3_chapter_16_migration(self):
        state = {"version": 3, "chapter": 16, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(normalized["version"], 8)

    def test_version_3_chapter_17_migration(self):
        state = {"version": 3, "chapter": 17, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(normalized["version"], 8)

    def test_version_2_chapter_14_migration(self):
        state = {"version": 2, "chapter": 14, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 16)
        self.assertEqual(normalized["version"], 8)

    def test_version_2_chapter_15_migration(self):
        state = {"version": 2, "chapter": 15, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(normalized["version"], 8)

    def test_version_1_chapter_11_migration(self):
        state = {"version": 1, "chapter": 11, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 13)
        self.assertEqual(normalized["version"], 8)

    def test_version_4_chapter_16_stays_before_archive(self):
        state = {"version": 4, "chapter": 16, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 16)
        self.assertEqual(normalized["version"], 8)

    def test_version_4_response_chapter_moves_after_archive(self):
        state = {"version": 4, "chapter": 17, "route": "", "origin_route": "", "approach": "", "ending": "refund", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 18)
        self.assertEqual(normalized["ending"], "refund")

    def test_version_4_final_chapter_stays_complete_after_continuation(self):
        state = {"version": 4, "chapter": 18, "route": "", "origin_route": "", "approach": "", "ending": "company_accepted", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(normalized["ending"], "company_accepted")
        self.assertEqual(normalized["previous_ending"], "company_accepted")

    def test_version_5_completed_state_stays_complete(self):
        state = {"version": 5, "chapter": 19, "route": "", "origin_route": "", "approach": "", "ending": "company_accepted", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(normalized["ending"], "company_accepted")
        self.assertEqual(normalized["previous_ending"], "company_accepted")
        console = Mock()
        with patch("vibe_plus.Prompt.ask", return_value="2"):
            _, result = run(console, 200, 10, normalized)
        self.assertEqual(result["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(result["ending"], "company_accepted")
        final_panel = next(
            call.args[0]
            for call in console.print.call_args_list
            if "Ответ принят." in str(getattr(call.args[0], "renderable", ""))
        )
        self.assertIn("Ответ принят.", final_panel.renderable)

    def test_version_5_unfinished_response_stays_playable(self):
        state = {"version": 5, "chapter": 18, "route": "bank", "origin_route": "", "approach": "", "ending": "refund", "exam_progress": 0, "side_quest": None, "trust_level": 2, "evidence": 3}
        normalized = normalize_state(state)
        self.assertEqual(normalized["chapter"], 18)
        self.assertEqual(normalized["ending"], "refund")
        self.assertEqual(normalized["previous_ending"], "")
        with patch("vibe_plus.Prompt.ask", return_value="1"):
            _, result = run(Mock(), 200, 10, normalized)
        self.assertEqual(result["chapter"], 19)
        self.assertEqual(result["ending"], "company_accepted")
        self.assertEqual(result["previous_ending"], "company_accepted")


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
    def test_version_normalized_to_8(self):
        state = {"version": 1, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 8)

    def test_version_4_upgraded_to_8(self):
        state = {"version": 4, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 8)

    def test_version_8_preserved(self):
        state = {"version": 8, "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 8)

    def test_version_invalid_type(self):
        state = {"version": "invalid", "chapter": 0, "route": "", "origin_route": "", "approach": "", "ending": "", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
        normalized = normalize_state(state)
        self.assertEqual(normalized["version"], 8)


class TestMigrationFromOldFormat(unittest.TestCase):
    def test_old_format_with_main_fields(self):
        old = {"chapter": 2, "route": "exam", "ending": "test"}
        new = normalize_state(old)
        self.assertEqual(new["version"], 8)
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
        self.assertEqual(new["version"], 8)
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
    def test_continuation_chapter_order(self):
        self.assertEqual(
            CHAPTERS[19:28],
            (
                "Письмо, которое всё-таки пришло",
                "Реестр обещаний",
                "Сверка с банком",
                "Совет подписчиков",
                "Аудит без печати",
                "Проверка исполнения",
                "Апелляция на апелляцию",
                "Общественный отчёт",
                "План последствий",
            ),
        )
        mistral_start = CHAPTERS.index("План последствий") + 1
        self.assertEqual(
            CHAPTERS[mistral_start:mistral_start + 10],
            (
                "Реестр с человеческим лицом",
                "Повторная сверка обещаний",
                "День без списаний",
                "Комиссия по кнопке",
                "Акт исполнения",
                "Свидетели процедуры",
                "Повторное слушание",
                "Публичный протокол",
                "Последний компромисс",
                "Кому достанется последнее слово",
            ),
        )
        self.assertEqual(CHAPTERS[-1], "Досье закрыто")

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

    def test_chapter_19_starts_continuation(self):
        state = {"version": 8, "chapter": 19, "route": "", "origin_route": "", "approach": "", "ending": "company_accepted", "exam_progress": 0, "side_quest": None, "trust_level": 0, "evidence": 0}
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

    def test_skipping_archive_without_side_quest_reaches_continuation(self):
        state = default_state()
        state.update(chapter=17, evidence=0, trust_level=0)
        points, state = self.play(state, "5")
        self.assertIsNone(state["side_quest"])
        self.assertEqual(state["chapter"], 18)
        self.assertEqual(state["archive_policy"], "skipped")

        points, result = self.play(state, "1", points)
        self.assertEqual(result["chapter"], 19)
        self.assertEqual(result["ending"], "company_accepted")
        self.assertEqual(result["previous_ending"], "company_accepted")
        self.assertEqual(points, 200)


class TestContinuationChapters(unittest.TestCase):
    def play(self, state, choice, points=200):
        with patch("vibe_plus.Prompt.ask", return_value=choice):
            return run(Mock(), points, 10, state)

    def state_for(self, chapter, **continuation):
        state = default_state()
        state.update(
            chapter=chapter,
            route="bank",
            ending="refund",
            previous_ending="refund",
            evidence=3,
            trust_level=3,
            archive_policy="public_consented",
        )
        state["continuation"].update({
            "letter": "opened",
            "promises": "deadlines",
            "bank_check": "reconciled",
            "council": "collective",
            "audit": "certified",
            "verification": "documented",
            "appeal": "regulator",
            "report": "public",
        })
        state["continuation"].update(continuation)
        return state

    def test_each_chapter_choice_advances_and_stores_its_result(self):
        cases = (
            (19, "letter", ("opened", "delegated"), {}),
            (20, "promises", ("deadlines", "wording"), {}),
            (21, "bank_check", ("reconciled", "statement_requested"), {}),
            (22, "council", ("collective", "delegates"), {}),
            (23, "audit", ("certified", "internal"), {}),
            (24, "verification", ("documented", "spot_check"), {}),
            (25, "appeal", ("regulator", "ombudsman"), {}),
            (26, "report", ("public", "sealed"), {}),
        )
        for chapter, field, expected_values, prerequisites in cases:
            for choice, expected in zip(("1", "2"), expected_values):
                with self.subTest(chapter=chapter, choice=choice):
                    state = self.state_for(chapter, **prerequisites)
                    points, result = self.play(state, choice)
                    self.assertEqual(result["chapter"], chapter + 1)
                    self.assertEqual(result["continuation"][field], expected)
                    self.assertEqual(result["ending"], "refund")
                    self.assertEqual(points, 200)

        plan_results = (
            ("1", "monitoring", "compliance_monitored"),
            ("2", "appeal", "appeal_reopened"),
            ("3", "settlement", "supervised_settlement"),
        )
        for choice, plan, outcome in plan_results:
            with self.subTest(chapter=27, choice=choice):
                points, result = self.play(self.state_for(27), choice)
                self.assertEqual(
                    result["chapter"],
                    CHAPTERS.index("Реестр с человеческим лицом"),
                )
                self.assertEqual(result["continuation"]["plan"], plan)
                self.assertEqual(result["continuation_result"], outcome)
                self.assertEqual(result["ending"], "refund")
                self.assertEqual(result["previous_ending"], "refund")
                self.assertEqual(points, 200)

    def test_eligibility_gates_prevent_unverified_outcomes(self):
        state = self.state_for(21, letter="delegated", promises="wording")
        _, state = self.play(state, "1")
        self.assertEqual(state["continuation"]["bank_check"], "unverified")

        state = self.state_for(23, bank_check="statement_requested", council="delegates")
        _, state = self.play(state, "1")
        self.assertEqual(state["continuation"]["audit"], "pending")

        state = self.state_for(24, audit="pending")
        _, state = self.play(state, "1")
        self.assertEqual(state["continuation"]["verification"], "discrepancies")

        state = self.state_for(26)
        state.update(archive_policy="restricted", evidence=1, trust_level=1)
        _, state = self.play(state, "1")
        self.assertEqual(state["continuation"]["report"], "held")

        state = self.state_for(
            27,
            bank_check="statement_requested",
            audit="pending",
            verification="discrepancies",
            report="held",
        )
        for choice, expected in (("1", "monitoring_pending"), ("2", "appeal_pending"), ("3", "settlement_pending")):
            _, result = self.play(state, choice)
            self.assertEqual(result["continuation_result"], expected)

    def test_continuation_survives_save_round_trips_and_preserves_old_ending(self):
        state = self.state_for(18)
        state["previous_ending"] = ""
        state.update(ending="refund", chapter=18)
        points, state = self.play(state, "1")
        self.assertEqual(state["chapter"], 19)
        self.assertEqual(state["ending"], "consented_archive")
        self.assertEqual(state["previous_ending"], "consented_archive")

        for chapter in range(19, 28):
            choice = "1"
            if chapter == 27:
                choice = "1"
            points, state = self.play(state, choice, points)
            state = normalize_state(json.loads(json.dumps(state)))
            self.assertEqual(state["chapter"], chapter + 1)

        self.assertEqual(state["continuation"]["letter"], "opened")
        self.assertEqual(state["continuation"]["promises"], "deadlines")
        self.assertEqual(state["continuation"]["bank_check"], "reconciled")
        self.assertEqual(state["continuation"]["audit"], "certified")
        self.assertEqual(state["continuation"]["verification"], "documented")
        self.assertEqual(state["continuation_result"], "compliance_monitored")
        self.assertEqual(state["ending"], "consented_archive")
        self.assertEqual(state["previous_ending"], "consented_archive")
        self.assertEqual(points, 200)


class TestMistralContinuation(unittest.TestCase):
    chapter_titles = (
        "Реестр с человеческим лицом",
        "Повторная сверка обещаний",
        "День без списаний",
        "Комиссия по кнопке",
        "Акт исполнения",
        "Свидетели процедуры",
        "Повторное слушание",
        "Публичный протокол",
        "Последний компромисс",
        "Кому достанется последнее слово",
    )

    def play(self, state, choice, points=200):
        with patch("vibe_plus.Prompt.ask", return_value=choice):
            return run(Mock(), points, 10, state)

    def state_for(self, chapter_title, decisions=None, **state_values):
        state = default_state()
        state.update(
            chapter=CHAPTERS.index(chapter_title),
            route="bank",
            origin_route="bank",
            ending="company_accepted",
            previous_ending="company_accepted",
            evidence=5,
            trust_level=3,
            side_quest="subscriber_testimony",
            archive_policy="public_consented",
            continuation_result="compliance_monitored",
        )
        state["continuation"].update({
            "letter": "opened",
            "promises": "deadlines",
            "bank_check": "reconciled",
            "council": "collective",
            "audit": "certified",
            "verification": "documented",
            "appeal": "regulator",
            "report": "public",
            "plan": "monitoring",
            "registry": "transparent",
            "reconciliation": "matched",
            "no_charges": "confirmed",
            "commission": "independent",
            "act": "verified",
            "witnesses": "corroborated",
            "hearing": "accepted",
            "protocol": "published",
            "compromise": "fair",
        })
        state["continuation"].update(decisions or {})
        state.update(state_values)
        return state

    def complete_path(
        self,
        expected_ending,
        registry_choice="1",
        commission_choice="1",
        protocol_choice="1",
        final_choice="1",
        archive_policy="public_consented",
    ):
        state = self.state_for(
            self.chapter_titles[0],
            archive_policy=archive_policy,
        )
        choices = (
            registry_choice,
            "1",
            "1",
            commission_choice,
            "1",
            "1",
            "1",
            protocol_choice,
            "1",
            final_choice,
        )
        points = 200
        for title, choice in zip(self.chapter_titles, choices):
            with self.subTest(chapter=title, choice=choice):
                self.assertEqual(state["chapter"], CHAPTERS.index(title))
                points, state = self.play(state, choice, points)
                state = normalize_state(json.loads(json.dumps(state)))
        self.assertEqual(state["chapter"], CHAPTERS.index("Досье закрыто"))
        self.assertEqual(state["continuation_ending"], expected_ending)
        self.assertEqual(state["ending"], "company_accepted")
        self.assertEqual(state["previous_ending"], "company_accepted")
        self.assertEqual(points, 200)
        return state

    def test_all_ten_chapters_offer_choices_and_store_consequences(self):
        cases = (
            (
                "Реестр с человеческим лицом",
                "registry",
                (("1", "transparent", {}), ("2", "restricted", {})),
            ),
            (
                "Повторная сверка обещаний",
                "reconciliation",
                (("1", "matched", {}), ("2", "spot_checked", {})),
            ),
            (
                "День без списаний",
                "no_charges",
                (("1", "confirmed", {}), ("2", "monitored", {})),
            ),
            (
                "Комиссия по кнопке",
                "commission",
                (("1", "independent", {}), ("2", "subscribers", {})),
            ),
            (
                "Акт исполнения",
                "act",
                (("1", "verified", {}), ("2", "remedy", {})),
            ),
            (
                "Свидетели процедуры",
                "witnesses",
                (("1", "corroborated", {}), ("2", "protected", {})),
            ),
            (
                "Повторное слушание",
                "hearing",
                (
                    ("1", "accepted", {}),
                    ("2", "closed", {"archive_policy": "restricted"}),
                ),
            ),
            (
                "Публичный протокол",
                "protocol",
                (("1", "published", {}), ("2", "sealed", {})),
            ),
            (
                "Последний компромисс",
                "compromise",
                (("1", "fair", {}), ("2", "refused", {})),
            ),
        )
        for title, field, choices in cases:
            for choice, expected, state_values in choices:
                with self.subTest(chapter=title, choice=choice):
                    state = self.state_for(title, **state_values)
                    points, result = self.play(state, choice)
                    self.assertEqual(
                        result["chapter"],
                        CHAPTERS.index(title) + 1,
                    )
                    self.assertEqual(result["continuation"][field], expected)
                    self.assertEqual(result["ending"], "company_accepted")
                    self.assertEqual(points, 200)

        final_choices = (
            ("1", "registry", "registry_enforced"),
            ("2", "control", "independent_oversight"),
            ("3", "community", "public_commitment"),
        )
        for choice, stored_choice, ending in final_choices:
            with self.subTest(chapter=self.chapter_titles[-1], choice=choice):
                state = self.state_for(self.chapter_titles[-1])
                state["continuation"].update({
                    "registry": "transparent",
                    "no_charges": "confirmed",
                    "commission": "independent",
                    "act": "verified",
                    "witnesses": "corroborated",
                    "hearing": "accepted",
                    "protocol": "published",
                    "compromise": "fair",
                })
                points, result = self.play(state, choice)
                self.assertEqual(result["chapter"], CHAPTERS.index("Досье закрыто"))
                self.assertEqual(result["continuation"]["last_word"], stored_choice)
                self.assertEqual(result["continuation_ending"], ending)
                self.assertEqual(result["ending"], "company_accepted")
                self.assertEqual(points, 200)

    def test_six_new_endings_are_reachable_through_distinct_paths(self):
        ending_paths = (
            ("registry_enforced", "1", "1", "1", "1", "public_consented"),
            ("protected_register", "2", "1", "2", "1", "restricted"),
            ("independent_oversight", "1", "1", "1", "2", "public_consented"),
            ("subscriber_oversight", "1", "2", "1", "2", "public_consented"),
            ("public_commitment", "1", "1", "1", "3", "public_consented"),
            ("quiet_reform", "2", "1", "2", "3", "restricted"),
        )
        for path in ending_paths:
            with self.subTest(ending=path[0]):
                state = self.complete_path(*path)
                self.assertIn(state["continuation_ending"], CONTINUATION_ENDINGS)

    def test_ineligible_final_choices_remain_distinct_and_nonfatal(self):
        expected = (
            ("1", "registry_pending"),
            ("2", "oversight_pending"),
            ("3", "agreement_pending"),
        )
        for choice, ending in expected:
            state = self.state_for(
                self.chapter_titles[-1],
                {
                    "registry": "transparent",
                    "no_charges": "failed",
                    "commission": "advisory",
                    "act": "disputed",
                    "witnesses": "partial",
                    "hearing": "continued",
                    "protocol": "withheld",
                    "compromise": "partial",
                },
                evidence=1,
                trust_level=0,
            )
            _, result = self.play(state, choice)
            self.assertEqual(result["continuation_ending"], ending)
            self.assertEqual(result["chapter"], CHAPTERS.index("Досье закрыто"))

    def test_completed_screen_repeats_credits_without_changing_state(self):
        state = self.state_for(
            "Досье закрыто",
            {"registry": "transparent", "no_charges": "confirmed"},
            continuation_ending="registry_enforced",
        )
        for _ in range(2):
            console = Mock()
            with patch("vibe_plus.Prompt.ask", return_value="2"):
                points, result = run(console, 200, 10, state)
            self.assertEqual(points, 200)
            self.assertEqual(result, state)
            self.assertTrue(any(
                "ТИТРЫ" in str(getattr(call.args[0], "title", ""))
                for call in console.print.call_args_list
            ))
        console = Mock()
        with patch("vibe_plus.Prompt.ask", return_value="1"):
            _, restarted = run(console, 200, 10, state)
        self.assertEqual(restarted, default_state())


class TestPostCreditsEpilogue(unittest.TestCase):
    def play(self, state, choice, points=200):
        with patch("vibe_plus.Prompt.ask", return_value=choice):
            return run(Mock(), points, 10, state)

    def state_for(self, progress=0, active=True, decisions=None, **state_values):
        state = default_state()
        state.update(
            chapter=CHAPTERS.index("Досье закрыто"),
            route="bank",
            ending="company_accepted",
            previous_ending="company_accepted",
            evidence=4,
            trust_level=3,
            side_quest="subscriber_testimony",
            archive_policy="public_consented",
            continuation_result="compliance_monitored",
            continuation_ending="registry_enforced",
            epilogue_progress=progress,
            epilogue_active=active,
        )
        state["continuation"].update({
            "bank_check": "reconciled",
            "no_charges": "confirmed",
            "act": "verified",
            "protocol": "published",
        })
        state["epilogue"].update(decisions or {})
        state.update(state_values)
        return state

    def play_path(self, choices, **state_values):
        state = self.state_for(active=False, **state_values)
        with patch(
            "vibe_plus.Prompt.ask",
            side_effect=("3", choices[0]),
        ):
            points, state = run(Mock(), 200, 10, state)
        self.assertTrue(state["epilogue_active"])
        self.assertEqual(state["epilogue_progress"], 1)
        state = normalize_state(json.loads(json.dumps(state)))
        for choice in choices[1:]:
            points, state = self.play(state, choice, points)
            state = normalize_state(json.loads(json.dumps(state)))
        return points, state

    def test_epilogue_is_optional_and_resumes_after_serialization(self):
        state = self.state_for(active=False)
        with patch("vibe_plus.Prompt.ask", return_value="2"):
            points, exited = run(Mock(), 200, 10, state)
        self.assertEqual(exited, state)
        self.assertEqual(points, 200)

        with patch(
            "vibe_plus.Prompt.ask",
            side_effect=("3", "1"),
        ):
            points, active = run(Mock(), points, 10, state)
        self.assertTrue(active["epilogue_active"])
        self.assertEqual(active["epilogue_progress"], 1)
        self.assertEqual(active["epilogue"]["flash_drive"], "returned")
        self.assertEqual(active["ending"], "company_accepted")
        self.assertEqual(active["continuation_ending"], "registry_enforced")

        active = normalize_state(json.loads(json.dumps(active)))
        points, active = self.play(active, "1", points)
        self.assertEqual(active["epilogue"]["last_payment"], "reconciled")
        self.assertEqual(active["epilogue_progress"], 2)
        self.assertEqual(active["ending"], "company_accepted")
        self.assertEqual(active["previous_ending"], "company_accepted")
        self.assertEqual(points, 200)

    def test_each_episode_choice_persists_and_advances(self):
        cases = (
            (
                0,
                {},
                (("1", "flash_drive", "returned"), ("2", "flash_drive", "sealed")),
            ),
            (
                1,
                {"flash_drive": "returned"},
                (("1", "last_payment", "reconciled"), ("2", "last_payment", "escrow")),
            ),
            (
                2,
                {"flash_drive": "returned", "last_payment": "reconciled"},
                (("1", "former_agent", "testimony"), ("2", "former_agent", "anonymous")),
            ),
            (
                3,
                {"last_payment": "reconciled", "former_agent": "testimony"},
                (("1", "fix_check", "verified"), ("2", "fix_check", "monitored")),
            ),
        )
        for progress, decisions, options in cases:
            for choice, field, expected in options:
                with self.subTest(progress=progress, choice=choice):
                    state = self.state_for(progress, decisions=decisions)
                    points, result = self.play(state, choice)
                    self.assertEqual(result["epilogue"][field], expected)
                    self.assertEqual(result["epilogue_progress"], progress + 1)
                    self.assertTrue(result["epilogue_active"])
                    self.assertEqual(result["ending"], "company_accepted")
                    self.assertEqual(result["continuation_ending"], "registry_enforced")
                    self.assertEqual(points, 200)

        paper_box_choices = (
            ("1", {"paper_box": "sealed"}, "documented_reform"),
            ("2", {"paper_box": "returned"}, "followup_required"),
            ("3", {"paper_box": "public"}, "public_accountability"),
        )
        for choice, stored_value, expected_result in paper_box_choices:
            with self.subTest(progress=4, choice=choice):
                decisions = {
                    "flash_drive": "returned",
                    "last_payment": "reconciled",
                    "former_agent": "testimony",
                    "fix_check": "verified",
                }
                state = self.state_for(4, decisions=decisions)
                points, result = self.play(state, choice)
                self.assertEqual(result["epilogue"], {
                    **state["epilogue"],
                    **stored_value,
                })
                self.assertEqual(result["epilogue_result"], expected_result)
                self.assertEqual(result["epilogue_progress"], 5)
                self.assertFalse(result["epilogue_active"])
                self.assertEqual(points, 200)

    def test_all_epilogue_outcomes_follow_saved_choices(self):
        paths = (
            (("1", "1", "1", "1", "1"), "documented_reform", {}),
            (("2", "2", "2", "2", "2"), "privacy_preserved", {}),
            (("1", "1", "1", "1", "3"), "public_accountability", {}),
            (
                ("1", "1", "1", "1", "2"),
                "followup_required",
                {
                    "continuation_ending": "registry_pending",
                    "archive_policy": "restricted",
                    "continuation": {
                        "no_charges": "failed",
                        "act": "disputed",
                        "protocol": "withheld",
                    },
                },
            ),
        )
        for choices, expected, state_values in paths:
            with self.subTest(result=expected):
                points, state = self.play_path(choices, **state_values)
                self.assertEqual(state["epilogue_result"], expected)
                self.assertIn(state["epilogue_result"], EPILOGUE_RESULT_TEXT)
                self.assertEqual(state["epilogue_progress"], 5)
                self.assertFalse(state["epilogue_active"])
                self.assertEqual(state["ending"], "company_accepted")
                self.assertEqual(state["previous_ending"], "company_accepted")
                self.assertEqual(state["continuation_ending"], state_values.get(
                    "continuation_ending", "registry_enforced"
                ))
                self.assertEqual(points, 200)

    def test_corrupted_or_inconsistent_epilogue_state_is_normalized(self):
        state = self.state_for(
            progress=[],
            epilogue=["invalid"],
            epilogue_active=1,
            epilogue_result=["invalid"],
        )
        normalized = normalize_state(state)
        self.assertEqual(normalized["epilogue"], {name: None for name in EPILOGUE_OPTIONS})
        self.assertEqual(normalized["epilogue_progress"], 0)
        self.assertFalse(normalized["epilogue_active"])
        self.assertEqual(normalized["epilogue_result"], "")

        state = self.state_for(progress=3, active=False)
        normalized = normalize_state(state)
        self.assertTrue(normalized["epilogue_active"])

    def test_completed_screen_shows_both_story_results_and_epilogue_result(self):
        state = self.state_for(
            progress=5,
            active=False,
            epilogue_result="documented_reform",
            continuation_ending="registry_enforced",
        )
        console = Mock()
        with patch("vibe_plus.Prompt.ask", return_value="2"):
            points, result = run(console, 200, 10, state)
        final_panel = next(
            call.args[0]
            for call in console.print.call_args_list
            if "Ответ принят." in str(getattr(call.args[0], "renderable", ""))
        )
        self.assertIn("Реестр заработал", final_panel.renderable)
        self.assertIn("Послесловие: Исправление подтверждено", final_panel.renderable)
        self.assertEqual(result["ending"], "company_accepted")
        self.assertEqual(result["continuation_ending"], "registry_enforced")
        self.assertEqual(result["epilogue_result"], "documented_reform")
        self.assertEqual(points, 200)


if __name__ == "__main__":
    unittest.main()
