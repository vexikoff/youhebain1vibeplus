import unittest

from case_journal import MAX_ENTRIES, append_entry, normalize_entries


class TestNormalizeEntries(unittest.TestCase):
    def test_non_list_value_becomes_empty_history(self):
        self.assertEqual(normalize_entries(None), [])
        self.assertEqual(normalize_entries({"entries": []}), [])

    def test_rejects_malformed_entries(self):
        entries = normalize_entries([
            None,
            {"day": True, "event_id": "bool-day", "description": "ignored"},
            {"day": -1, "event_id": "negative-day", "description": "ignored"},
            {"day": 1, "event_id": "", "description": "ignored"},
            {"day": 1, "event_id": "empty-text", "description": "  "},
            {"day": 1, "event_id": 2, "description": "ignored"},
            {"day": 1, "event_id": "missing-text"},
        ])
        self.assertEqual(entries, [])

    def test_normalizes_text_and_keeps_first_duplicate(self):
        entries = normalize_entries([
            {"day": 2, "event_id": " choice ", "description": "  Позвонили \n Толе. "},
            {"day": 4, "event_id": "choice", "description": "Повторная запись."},
        ])
        self.assertEqual(entries, [{
            "day": 2,
            "event_id": "choice",
            "description": "Позвонили Толе.",
        }])

    def test_limits_field_lengths(self):
        event_id = "e" * 150
        description = "запись " * 60
        entry = normalize_entries([{
            "day": 1,
            "event_id": event_id,
            "description": description,
        }])[0]
        self.assertEqual(len(entry["event_id"]), 100)
        self.assertEqual(len(entry["description"]), 180)

    def test_limits_history_to_most_recent_entries(self):
        entries = normalize_entries([
            {"day": day, "event_id": f"event-{day}", "description": f"Запись {day}"}
            for day in range(MAX_ENTRIES + 5)
        ])
        self.assertEqual(len(entries), MAX_ENTRIES)
        self.assertEqual(entries[0]["event_id"], "event-5")
        self.assertEqual(entries[-1]["event_id"], f"event-{MAX_ENTRIES + 4}")


class TestAppendEntry(unittest.TestCase):
    def test_appends_and_deduplicates_by_event_id(self):
        entries = append_entry([], 3, "police:denied", "Не признались полиции.")
        repeated = append_entry(entries, 3, "police:denied", "Повторная запись.")
        self.assertEqual(len(repeated), 1)
        self.assertEqual(repeated[0]["description"], "Не признались полиции.")

    def test_append_keeps_only_recent_entries(self):
        entries = []
        for day in range(MAX_ENTRIES + 2):
            entries = append_entry(entries, day, f"day-{day}", f"День {day}")
        self.assertEqual(len(entries), MAX_ENTRIES)
        self.assertEqual(entries[0]["event_id"], "day-2")

    def test_rejects_invalid_new_entry(self):
        with self.assertRaises(ValueError):
            append_entry([], True, "event", "Описание")
        with self.assertRaises(ValueError):
            append_entry([], 1, " ", "Описание")
        with self.assertRaises(ValueError):
            append_entry([], 1, "event", "")


if __name__ == "__main__":
    unittest.main()
