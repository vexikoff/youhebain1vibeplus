import json
import unittest

import call_events


class CallEventTests(unittest.TestCase):
    def setUp(self):
        self.flags = {
            "dss": 1,
            "opencr": 1,
            "gamecorp": 1,
            "data_base": 1,
            "mearephone": 1,
        }

    def test_catalog_has_eight_distinct_calls_with_choices_and_effects(self):
        catalog = call_events.event_catalog()

        self.assertEqual(len(catalog), 8)
        self.assertEqual(len({event["id"] for event in catalog}), 8)
        for event in catalog:
            with self.subTest(event=event["id"]):
                self.assertTrue(event["caller"])
                self.assertTrue(event["opening"])
                self.assertGreaterEqual(len(event["choices"]), 2)
                self.assertTrue(
                    all(isinstance(choice["points_delta"], int) for choice in event["choices"])
                )

    def test_requirements_gate_events(self):
        for event in call_events.event_catalog():
            requirements = event["requirements"]
            if "day" in requirements:
                day = requirements["day"] - 1
                self.assertNotIn(
                    event["id"],
                    call_events.available_events(call_events.default_state(), day, self.flags),
                )
                day += 1
            else:
                day = 10
                key, value = next(iter(requirements.items()))
                flags = dict(self.flags)
                flags.pop(key, None)
                self.assertNotIn(
                    event["id"],
                    call_events.available_events(call_events.default_state(), day, flags),
                )
                flags[key] = value
                self.assertIn(
                    event["id"],
                    call_events.available_events(call_events.default_state(), day, flags),
                )
                continue

            self.assertIn(
                event["id"],
                call_events.available_events(call_events.default_state(), day, self.flags),
            )

    def test_selection_is_stable_and_rejects_invalid_indices(self):
        available = call_events.available_events(
            call_events.default_state(),
            10,
            self.flags,
        )

        self.assertEqual(call_events.select_event(call_events.default_state(), 10, self.flags), available[0])
        self.assertEqual(
            call_events.select_event(call_events.default_state(), 10, self.flags, len(available) - 1),
            available[-1],
        )
        self.assertIsNone(call_events.select_event(call_events.default_state(), 0, {}))
        with self.assertRaises(ValueError):
            call_events.select_event(call_events.default_state(), 10, self.flags, len(available))

    def test_each_choice_returns_effect_and_marks_event_seen(self):
        for event in call_events.event_catalog():
            for choice in event["choices"]:
                with self.subTest(event=event["id"], choice=choice["id"]):
                    state, effect = call_events.resolve_choice(
                        call_events.default_state(),
                        event["id"],
                        choice["id"],
                        10,
                        self.flags,
                    )

                    self.assertEqual(state["seen"][event["id"]], 10)
                    self.assertEqual(state["choices"][event["id"]], choice["id"])
                    self.assertEqual(effect["event_id"], event["id"])
                    self.assertEqual(effect["choice_id"], choice["id"])
                    self.assertEqual(effect["points_delta"], choice["points_delta"])
                    self.assertTrue(effect["reply"])

    def test_event_repeats_on_next_day_and_survives_serialization(self):
        event_id = "sunne_tariff"
        state, _ = call_events.resolve_choice(
            call_events.default_state(),
            event_id,
            "request_cancel",
            4,
            self.flags,
        )
        loaded = call_events.normalize_state(json.loads(json.dumps(state)))

        self.assertNotIn(event_id, call_events.available_events(loaded, 4, self.flags))
        self.assertIn(event_id, call_events.available_events(loaded, 5, self.flags))
        self.assertEqual(loaded, state)

    def test_legacy_and_damaged_states_normalize_without_unknown_viewed_ids(self):
        self.assertEqual(call_events.normalize_state(None), call_events.default_state())
        normalized = call_events.normalize_state(
            {
                "version": True,
                "seen": {
                    "sunne_tariff": 2,
                    "unknown_event": 4,
                    "opencreate_audit": True,
                    "gamecorp_license": -1,
                },
                "choices": {
                    "sunne_tariff": "request_cancel",
                    "unknown_event": "anything",
                    "opencreate_audit": "not-a-choice",
                },
            }
        )

        self.assertEqual(normalized["seen"], {"sunne_tariff": 2})
        self.assertEqual(normalized["choices"], {"sunne_tariff": "request_cancel"})
        self.assertEqual(
            call_events.normalize_state({"seen": [], "choices": None}),
            call_events.default_state(),
        )

    def test_unavailable_or_invalid_choices_are_rejected(self):
        with self.assertRaises(ValueError):
            call_events.resolve_choice(
                call_events.default_state(),
                "sunne_tariff",
                "request_cancel",
                10,
                {},
            )
        with self.assertRaises(ValueError):
            call_events.resolve_choice(
                call_events.default_state(),
                "missing_event",
                "anything",
                10,
                self.flags,
            )
        with self.assertRaises(ValueError):
            call_events.resolve_choice(
                call_events.default_state(),
                "sunne_tariff",
                "missing_choice",
                10,
                self.flags,
            )
        with self.assertRaises(ValueError):
            call_events.resolve_choice(
                call_events.default_state(),
                [],
                "request_cancel",
                10,
                self.flags,
            )


if __name__ == "__main__":
    unittest.main()
