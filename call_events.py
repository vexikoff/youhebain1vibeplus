from copy import deepcopy


EVENT_SLOT_BASE = 26

_EVENTS = (
    {
        "id": "sunne_tariff",
        "caller": "Sunne CL",
        "title": "Тариф без конца",
        "opening": "Компания предлагает продлить услугу, срок которой закончился вчера и, по их словам, никогда.",
        "requirements": {"dss": 1},
        "choices": (
            {
                "id": "request_cancel",
                "label": "Попросить отмену и вернуть комиссию",
                "reply": "Отмену приняли. Комиссию назвали платой за знакомство с кнопкой.",
                "points_delta": 15,
            },
            {
                "id": "accept_extension",
                "label": "Согласиться на продление",
                "reply": "Продление оформлено. Срок снова закончится вчера.",
                "points_delta": -10,
            },
        ),
    },
    {
        "id": "opencreate_audit",
        "caller": "OpenCreate",
        "title": "Аудит пароля",
        "opening": "Оператор проверяет, не слишком ли надёжный у вас пароль для их платной проверки.",
        "requirements": {"opencr": 1},
        "choices": (
            {
                "id": "request_report",
                "label": "Попросить отчёт без персональных данных",
                "reply": "Отчёт прислали. В нём нет данных, зато есть слово «отчёт».",
                "points_delta": 5,
            },
            {
                "id": "buy_certificate",
                "label": "Купить сертификат безопасности",
                "reply": "Сертификат выдан. Камера всё ещё просит пароль от сертификата.",
                "points_delta": -15,
            },
        ),
    },
    {
        "id": "gamecorp_license",
        "caller": "Gamecorp o ration",
        "title": "Лицензия на паузу",
        "opening": "Юрист компании предлагает оформить лицензию на перерыв между двумя проектами.",
        "requirements": {"gamecorp": 1},
        "choices": (
            {
                "id": "keep_rights",
                "label": "Оставить права у себя",
                "reply": "Права остались у вас. Компания попросила прислать их копию.",
                "points_delta": 0,
            },
            {
                "id": "sell_demo",
                "label": "Продать демонстрацию проекта",
                "reply": "Оплата пришла. Демонстрацию теперь показывают как окончательный продукт.",
                "points_delta": 20,
            },
        ),
    },
    {
        "id": "bank_fee",
        "caller": "Банк «Не дозвонишься»",
        "title": "Комиссия за возврат",
        "opening": "Банк нашёл комиссию, которую раньше искал в другом отделе.",
        "requirements": {"day": 5},
        "choices": (
            {
                "id": "dispute_fee",
                "label": "Оспорить комиссию",
                "reply": "Комиссию сняли. Оспаривание осталось бесплатным до следующего звонка.",
                "points_delta": 25,
            },
            {
                "id": "pay_for_review",
                "label": "Оплатить ускоренную проверку",
                "reply": "Проверка ускорилась. Банк сообщил об этом в обычный срок.",
                "points_delta": -10,
            },
        ),
    },
    {
        "id": "subscriber_billing",
        "caller": "Совет подписчиков",
        "title": "Выписка на всех",
        "opening": "Подписчики нашли ещё одну строку списания и три разных объяснения к ней.",
        "requirements": {"day": 3},
        "choices": (
            {
                "id": "share_receipt",
                "label": "Сверить обезличенные чеки",
                "reply": "Совпадения подтвердились. Чеки попросили больше не пересылать в общий чат.",
                "points_delta": 10,
            },
            {
                "id": "print_everything",
                "label": "Распечатать все выписки",
                "reply": "Принтер устал первым. Участники сохранили по копии и по одной скрепке.",
                "points_delta": -5,
            },
        ),
    },
    {
        "id": "insurer_renewal",
        "caller": "Страхунец обосрунец",
        "title": "Страховка от уведомлений",
        "opening": "Страховая предлагает застраховать телефон от звонков, которыми сама же звонит.",
        "requirements": {"day": 7},
        "choices": (
            {
                "id": "decline_policy",
                "label": "Отказаться от полиса",
                "reply": "Отказ зафиксирован. Вам оставили памятку о том, как отказаться от памятки.",
                "points_delta": 15,
            },
            {
                "id": "buy_policy",
                "label": "Купить полис на месяц",
                "reply": "Полис действует месяц. Продление начинается за неделю до звонка.",
                "points_delta": -20,
            },
        ),
    },
    {
        "id": "tolya_database",
        "caller": "Толя",
        "title": "Оптовая база",
        "opening": "Толя предлагает проверить базу клиентов. В образце один адрес и десять согласий на рассылку.",
        "requirements": {"data_base": 1},
        "choices": (
            {
                "id": "delete_copy",
                "label": "Удалить копию и оставить только журнал сделки",
                "reply": "Копия удалена. Толя сохранил журнал и пообещал не называть его копией.",
                "points_delta": 10,
            },
            {
                "id": "return_database",
                "label": "Вернуть базу владельцам",
                "reply": "База отправлена владельцам. Подтверждение доставки пришло без списка адресов.",
                "points_delta": 20,
            },
        ),
    },
    {
        "id": "mearephone_signal",
        "caller": "MearePhone",
        "title": "Сигнал из темноты",
        "opening": "На линии короткий сигнал. Толя утверждает, что это уже половина разговора.",
        "requirements": {"mearephone": 1},
        "choices": (
            {
                "id": "request_text",
                "label": "Попросить прислать условия текстом",
                "reply": "Условия прислали сообщением. В нём только ссылка и просьба не открывать ссылку.",
                "points_delta": 10,
            },
            {
                "id": "call_back",
                "label": "Перезвонить по номеру из сообщения",
                "reply": "Перезвонить не удалось: номер занят собственным автоответчиком.",
                "points_delta": -10,
            },
        ),
    },
)

_EVENTS_BY_ID = {event["id"]: event for event in _EVENTS}


def event_catalog():
    return deepcopy(_EVENTS)


def default_state():
    return {"version": 1, "seen": {}, "choices": {}}


def normalize_state(value):
    if not isinstance(value, dict):
        return default_state()

    raw_seen = value.get("seen")
    if not isinstance(raw_seen, dict):
        raw_seen = {}
    seen = {}
    for event_id, day in raw_seen.items():
        if (
            event_id in _EVENTS_BY_ID
            and isinstance(day, int)
            and not isinstance(day, bool)
            and day >= 0
        ):
            seen[event_id] = day

    raw_choices = value.get("choices")
    if not isinstance(raw_choices, dict):
        raw_choices = {}
    choices = {}
    for event_id, choice_id in raw_choices.items():
        event = _EVENTS_BY_ID.get(event_id)
        if event and any(choice["id"] == choice_id for choice in event["choices"]):
            choices[event_id] = choice_id

    return {"version": 1, "seen": seen, "choices": choices}


def _requirements_match(requirements, day, flags):
    for key, expected in requirements.items():
        actual = day if key == "day" else flags.get(key)
        if isinstance(expected, int) and not isinstance(expected, bool):
            if isinstance(actual, bool) or not isinstance(actual, int):
                return False
            if key == "day":
                if actual < expected:
                    return False
            elif actual != expected:
                return False
        elif actual != expected:
            return False
    return True


def available_events(state, day, flags):
    if isinstance(day, bool) or not isinstance(day, int) or day < 0:
        return ()
    if not isinstance(flags, dict):
        flags = {}
    normalized = normalize_state(state)
    available = []
    for event in _EVENTS:
        last_seen = normalized["seen"].get(event["id"])
        if last_seen is not None and day <= last_seen:
            continue
        if _requirements_match(event["requirements"], day, flags):
            available.append(event["id"])
    return tuple(available)


def select_event(state, day, flags, index=0):
    available = available_events(state, day, flags)
    if not available:
        return None
    if isinstance(index, bool) or not isinstance(index, int):
        raise ValueError("event index must be an integer")
    if index < 0 or index >= len(available):
        raise ValueError("event index is outside the available range")
    return available[index]


def resolve_choice(state, event_id, choice_id, day, flags):
    if not isinstance(event_id, str) or not isinstance(choice_id, str):
        raise ValueError("call event and choice IDs must be strings")
    event = _EVENTS_BY_ID.get(event_id)
    if event is None:
        raise ValueError("unknown call event")
    if event_id not in available_events(state, day, flags):
        raise ValueError("call event is not available")
    choice = next(
        (item for item in event["choices"] if item["id"] == choice_id),
        None,
    )
    if choice is None:
        raise ValueError("unknown call event choice")

    normalized = normalize_state(state)
    next_state = deepcopy(normalized)
    next_state["seen"][event_id] = day
    next_state["choices"][event_id] = choice_id
    effect = {
        "event_id": event_id,
        "choice_id": choice_id,
        "reply": choice["reply"],
        "points_delta": choice["points_delta"],
    }
    return next_state, effect
