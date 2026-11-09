import io
import unittest

from rich.console import Console

import achievements


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


if __name__ == "__main__":
    unittest.main()
