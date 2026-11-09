MAX_ENTRIES = 50
MAX_EVENT_ID_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 180


def normalize_entries(value):
    if not isinstance(value, list):
        return []

    entries = []
    seen = set()
    for item in value:
        if not isinstance(item, dict):
            continue

        day = item.get("day")
        event_id = item.get("event_id")
        description = item.get("description")
        if not isinstance(day, int) or isinstance(day, bool) or day < 0:
            continue
        if not isinstance(event_id, str) or not isinstance(description, str):
            continue

        event_id = event_id.strip()[:MAX_EVENT_ID_LENGTH]
        description = " ".join(description.split())[:MAX_DESCRIPTION_LENGTH]
        if not event_id or not description or event_id in seen:
            continue

        entries.append({
            "day": day,
            "event_id": event_id,
            "description": description,
        })
        seen.add(event_id)

    return entries[-MAX_ENTRIES:]


def append_entry(entries, day, event_id, description):
    if not isinstance(day, int) or isinstance(day, bool) or day < 0:
        raise ValueError("day must be a non-negative integer")
    if not isinstance(event_id, str) or not event_id.strip():
        raise ValueError("event_id must be a non-empty string")
    if not isinstance(description, str) or not description.strip():
        raise ValueError("description must be a non-empty string")

    normalized = normalize_entries(entries)
    event_id = event_id.strip()[:MAX_EVENT_ID_LENGTH]
    if any(entry["event_id"] == event_id for entry in normalized):
        return normalized

    return normalize_entries(normalized + [{
        "day": day,
        "event_id": event_id,
        "description": description,
    }])
