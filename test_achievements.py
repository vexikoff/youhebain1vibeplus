import io
import unittest

from rich.console import Console

import achievements


NEW_DLC_IDS = (
    "dlc_archive_consent",
    "dlc_archive_restricted",
    "dlc_archive_summary",
    "dlc_archive_declined",
    "dlc_consent_pending",
    "dlc_trusted_evidence",
    "dlc_private_evidence",
    "dlc_sidequest_documents",
    "dlc_testimony_route",
    "dlc_ending_consented",
    "dlc_ending_protected",
    "dlc_ending_summary",
    "dlc_ending_counterclaim",
    "dlc_ending_independent",
    "dlc_press_route",
)


class AchievementStateTests(unittest.TestCase):
    def test_default_and_legacy_save_state(self):
        old_save = {"day": 7, "ochko": 120, "vibe_plus": {"chapter": 2}}
        state = achievements.normalize_state(old_save.get("achievements"))

        self.assertEqual(state, achievements.default_state())
        self.assertGreaterEqual(len(achievements.ACHIEVEMENTS), 12)

    def test_normalization_discards_unknown_ids_and_invalid_values(self):
        state = achievements.normalize_state(
            {
                "version": True,
                "stats": {
                    "days": 7,
                    "calls_answered": -2,
                    "fishing_catches": True,
                    "not_a_stat": 99,
                },
                "unlocked": {
                    "week_survivor": 7,
                    "missing_achievement": 2,
                    "first_light": True,
                },
            }
        )

        self.assertEqual(state["version"], achievements.ACHIEVEMENT_VERSION)
        self.assertEqual(state["stats"]["days"], 7)
        self.assertEqual(state["stats"]["calls_answered"], 0)
        self.assertEqual(state["stats"]["fishing_catches"], 0)
        self.assertNotIn("not_a_stat", state["stats"])
        self.assertEqual(state["unlocked"], {"week_survivor": 7})

    def test_conditions_cover_flags_and_statistics(self):
        context = {
            "dss": 1,
            "days": 7,
            "ochko": 3100,
            "opencr": 1,
            "data_base": 1,
            "path_tolya": 2,
            "stats": {
                "days": 7,
                "max_points": 3100,
                "chores_dishes": 1,
                "chores_floor": 1,
                "chores_trash": 1,
                "chores_games": 5,
                "fishing_sessions": 3,
                "fishing_catches": 6,
                "calls_answered": 15,
            },
        }

        unlocked = set(achievements.check(context))

        self.assertTrue(
            {
                "first_light",
                "week_survivor",
                "clean_freak",
                "gamer_soul",
                "fisherman",
                "golden_perch",
                "privacy_paid",
                "bargain_found",
                "partner_in_crime",
                "phone_addict",
                "rich_man",
            }.issubset(unlocked)
        )

    def test_check_handles_invalid_context_and_missing_condition_values(self):
        self.assertEqual(achievements.check(None), [])
        self.assertEqual(achievements.check({"dss": "wrong-type"}), [])

    def test_update_tracks_actions_points_and_unlocks_once(self):
        state = achievements.default_state()
        context = {"day": 7, "ochko": 3100, "dss": 1}
        state = achievements.update(state, context, {"activity": "pomit"})
        state = achievements.update(state, context, {"activity": "pomitp"})
        state = achievements.update(state, context, {"activity": "musor"})
        state = achievements.update(state, context, {"points_delta": 28})

        self.assertEqual(state["stats"]["chores_dishes"], 1)
        self.assertEqual(state["stats"]["chores_floor"], 1)
        self.assertEqual(state["stats"]["chores_trash"], 1)
        self.assertEqual(state["stats"]["points_earned"], 28)
        self.assertEqual(state["stats"]["days"], 7)
        self.assertEqual(state["stats"]["max_points"], 3100)
        self.assertEqual(state["unlocked"]["first_light"], 7)
        self.assertEqual(state["unlocked"]["week_survivor"], 7)
        self.assertIn("clean_freak", state["unlocked"])
        self.assertIs(achievements.update(state, context), state)

    def test_update_records_fishing_calls_and_dlc_events(self):
        events = (
            {"event": "fishing_start"},
            {"event": "fishing_catch"},
            {"event": "call_answered"},
            {"event": "vibe_plus_visit"},
        )
        state = achievements.default_state()
        for event in events:
            state = achievements.update(state, {"day": 1, "ochko": 0}, event)

        self.assertEqual(state["stats"]["fishing_sessions"], 1)
        self.assertEqual(state["stats"]["fishing_catches"], 1)
        self.assertEqual(state["stats"]["calls_answered"], 1)
        self.assertEqual(state["stats"]["vibe_plus_visits"], 1)

    def test_build_context_uses_current_dlc_state(self):
        context = achievements.build_context(
            {"day": 1, "ochko": 100},
            {
                "chapter": 17,
                "evidence": 4,
                "side_quest": "completed",
                "trust_level": 2,
            },
        )

        self.assertEqual(context["vibe_chapter"], 17)
        self.assertEqual(context["vibe_evidence"], 4)
        self.assertEqual(context["vibe_side_quest"], "completed")
        self.assertEqual(context["vibe_trust"], 2)

    def test_completed_side_quest_achievement_matches_current_state_values(self):
        context = achievements.build_context(
            {},
            {"chapter": 8, "side_quest": "subscriber_testimony"},
        )

        self.assertIn("dlc_side_business", achievements.check(context))

    def test_build_context_normalizes_stable_dlc_fields(self):
        context = achievements.build_context(
            {"day": 5, "ochko": 300},
            {
                "chapter": 38,
                "route": "union",
                "origin_route": "press",
                "ending": "consented_archive",
                "evidence": 4,
                "trust_level": 3,
                "side_quest": "subscriber_testimony",
                "archive_policy": "public_consented",
            },
        )

        self.assertEqual(context["vibe_route"], "union")
        self.assertEqual(context["vibe_origin_route"], "press")
        self.assertEqual(context["vibe_ending"], "consented_archive")
        self.assertEqual(context["vibe_evidence"], 4)
        self.assertEqual(context["vibe_trust"], 3)
        self.assertEqual(context["vibe_side_quest"], "subscriber_testimony")
        self.assertEqual(context["vibe_archive_policy"], "public_consented")
        self.assertTrue(context["vibe_case_completed"])

    def test_each_new_dlc_achievement_has_a_reachable_condition(self):
        final = {"ending": "company_accepted"}
        cases = {
            "dlc_archive_consent": {**final, "archive_policy": "public_consented"},
            "dlc_archive_restricted": {**final, "archive_policy": "restricted"},
            "dlc_archive_summary": {**final, "archive_policy": "summary_only"},
            "dlc_archive_declined": {**final, "archive_policy": "skipped"},
            "dlc_consent_pending": {**final, "archive_policy": "consent_pending"},
            "dlc_trusted_evidence": {**final, "trust_level": 3, "evidence": 4},
            "dlc_private_evidence": {
                **final,
                "trust_level": 2,
                "evidence": 2,
                "archive_policy": "restricted",
            },
            "dlc_sidequest_documents": {
                **final,
                "side_quest": "billing_records",
                "evidence": 4,
            },
            "dlc_testimony_route": {
                **final,
                "side_quest": "subscriber_testimony",
                "route": "union",
            },
            "dlc_ending_consented": {"ending": "consented_archive"},
            "dlc_ending_protected": {"ending": "protected_archive"},
            "dlc_ending_summary": {"ending": "anonymous_summary"},
            "dlc_ending_counterclaim": {"ending": "counter_claim"},
            "dlc_ending_independent": {"ending": "third_party"},
            "dlc_press_route": {**final, "origin_route": "press"},
        }

        self.assertEqual(set(cases), set(NEW_DLC_IDS))
        for achievement_id, vibe_state in cases.items():
            with self.subTest(achievement_id=achievement_id):
                context = achievements.build_context({}, vibe_state)
                self.assertIn(achievement_id, achievements.check(context))

    def test_missing_or_damaged_dlc_fields_do_not_unlock_new_achievements(self):
        context = achievements.build_context(
            {
                "vibe_case_completed": 1,
                "vibe_ending": "consented_archive",
                "vibe_archive_policy": "public_consented",
            },
            {
                "route": ["union"],
                "origin_route": "forged",
                "ending": ["consented_archive"],
                "evidence": -1,
                "trust_level": 99,
                "side_quest": "not-a-side-quest",
                "archive_policy": "forged",
            },
        )

        self.assertNotIn("vibe_case_completed", context)
        self.assertNotIn("vibe_ending", context)
        self.assertNotIn("vibe_route", context)
        self.assertNotIn("vibe_origin_route", context)
        self.assertNotIn("vibe_evidence", context)
        self.assertNotIn("vibe_trust", context)
        self.assertNotIn("vibe_side_quest", context)
        self.assertNotIn("vibe_archive_policy", context)
        self.assertFalse(set(NEW_DLC_IDS) & set(achievements.check(context)))

    def test_archive_achievements_require_a_recognized_final_ending(self):
        for policy in (
            "public_consented",
            "restricted",
            "summary_only",
            "skipped",
            "consent_pending",
        ):
            with self.subTest(policy=policy):
                context = achievements.build_context(
                    {},
                    {"ending": "not-a-final-ending", "archive_policy": policy},
                )
                self.assertFalse(set(NEW_DLC_IDS) & set(achievements.check(context)))

    def test_new_unlocks_survive_repeated_updates(self):
        context = achievements.build_context(
            {"day": 5, "ochko": 100},
            {
                "ending": "company_accepted",
                "archive_policy": "restricted",
                "trust_level": 3,
                "evidence": 4,
                "side_quest": "billing_records",
            },
        )
        state = achievements.update(achievements.default_state(), context)

        self.assertTrue(
            {
                "dlc_archive_restricted",
                "dlc_trusted_evidence",
                "dlc_private_evidence",
                "dlc_sidequest_documents",
            }.issubset(state["unlocked"])
        )
        self.assertIs(achievements.update(state, context), state)

        updated = achievements.update(state, {"day": 6, "ochko": 100})
        self.assertTrue(set(NEW_DLC_IDS).intersection(updated["unlocked"]))
        self.assertEqual(
            updated["unlocked"]["dlc_archive_restricted"],
            state["unlocked"]["dlc_archive_restricted"],
        )

    def test_render_shows_achievements_and_stats(self):
        output = io.StringIO()
        console = Console(file=output, force_terminal=False, color_system=None)

        achievements.render(
            console,
            achievements.default_state(),
            {"day": 3, "ochko": 120},
            {},
        )

        rendered = output.getvalue()
        self.assertIn("Достижения и статистика прохождения", rendered)
        self.assertIn("Прожито дней", rendered)
        self.assertIn("ещё нет", rendered)

    def test_render_shows_new_records_and_full_count(self):
        output = io.StringIO()
        console = Console(file=output, force_terminal=False, color_system=None)
        state = achievements.default_state()
        state["unlocked"]["dlc_ending_consented"] = 2

        achievements.render(console, state, {}, {})

        rendered = output.getvalue()
        self.assertIn("Согласие в приложении", rendered)
        self.assertIn("получено", rendered)
        self.assertIn(f"1 из {len(achievements.ACHIEVEMENTS)}", rendered)
        for achievement_id in NEW_DLC_IDS:
            achievement = next(
                item for item in achievements.ACHIEVEMENTS if item["id"] == achievement_id
            )
            self.assertIn(achievement["title"], rendered)


if __name__ == "__main__":
    unittest.main()
