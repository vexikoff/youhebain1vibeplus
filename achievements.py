from copy import deepcopy

from rich.table import Table


ACHIEVEMENT_VERSION = 1

VIBE_ROUTE_VALUES = {
    "standard",
    "premium",
    "exam",
    "exam_passed",
    "blind_sign",
    "full_text",
    "honest",
    "blame",
    "refuse",
    "press",
    "consultant",
    "tolya",
    "appeal",
    "settlement",
    "bank",
    "regulator",
    "union",
    "refund",
    "exploit",
}
VIBE_ORIGIN_ROUTE_VALUES = {"press", "consultant", "tolya"}
VIBE_ENDING_VALUES = {
    "refund",
    "regulator",
    "union",
    "whistleblower",
    "settlement",
    "loophole",
    "appeal_denied",
    "public_exposure",
    "legal_victory",
    "corporate_surrender",
    "company_accepted",
    "counter_claim",
    "third_party",
    "consented_archive",
    "protected_archive",
    "anonymous_summary",
}
VIBE_FINAL_ENDINGS = {
    "company_accepted",
    "counter_claim",
    "third_party",
    "consented_archive",
    "protected_archive",
    "anonymous_summary",
}
VIBE_SIDE_QUEST_VALUES = {
    "completed",
    "billing_records",
    "subscriber_testimony",
}
VIBE_ARCHIVE_POLICIES = {
    "public_consented",
    "consent_pending",
    "restricted",
    "summary_only",
    "skipped",
}

STAT_KEYS = (
    "days",
    "points_earned",
    "points_spent",
    "max_points",
    "chores_dishes",
    "chores_floor",
    "chores_trash",
    "chores_nerve",
    "chores_games",
    "fishing_sessions",
    "fishing_catches",
    "calls_answered",
    "vibe_plus_visits",
)

COUNTER_FIELDS = {
    "pomit": "chores_dishes",
    "pomitp": "chores_floor",
    "musor": "chores_trash",
    "dro": "chores_nerve",
    "igr": "chores_games",
}

ACHIEVEMENTS = (
    {
        "id": "first_light",
        "title": "Первая свечка",
        "description": "Заключить договор с Sunne CL и открыть режим рыбалки.",
        "condition": "dss == 1",
    },
    {
        "id": "week_survivor",
        "title": "Неделя выдержки",
        "description": "Дожить до седьмого дня. Камеры ещё молчат.",
        "condition": "days >= 7",
    },
    {
        "id": "twelve_days",
        "title": "Двенадцать огней",
        "description": "Прожить двенадцать дней в этом чудесном месте.",
        "condition": "days >= 12",
    },
    {
        "id": "clean_freak",
        "title": "Чистюля-неудачник",
        "description": "Помыть посуду, полы и вынести мусор хотя бы по одному разу.",
        "condition": "chores_dishes >= 1 and chores_floor >= 1 and chores_trash >= 1",
    },
    {
        "id": "nervous_tic",
        "title": "Нервный тик",
        "description": "Подрочить три раза. Очки решают всё.",
        "condition": "chores_nerve >= 3",
    },
    {
        "id": "gamer_soul",
        "title": "Игровая душа",
        "description": "Поиграть пять раз вместо решения жизненных проблем.",
        "condition": "chores_games >= 5",
    },
    {
        "id": "fisherman",
        "title": "Рыбак года",
        "description": "Провести на рыбалке три сессии. Рыба уже боится.",
        "condition": "fishing_sessions >= 3",
    },
    {
        "id": "golden_perch",
        "title": "Золотой окунь",
        "description": "Поймать рыбу шесть раз. Удочка просит отпуск.",
        "condition": "fishing_catches >= 6",
    },
    {
        "id": "privacy_paid",
        "title": "Приватность за десятку",
        "description": "Оплатить пароль для камер OpenCreate.",
        "condition": "opencr == 1",
    },
    {
        "id": "bargain_found",
        "title": "Находчивый барыга",
        "description": "Купить базу данных клиентов Sunne CL у Толи на почте.",
        "condition": "data_base == 1",
    },
    {
        "id": "snitch",
        "title": "Стукач месяца",
        "description": "Сдать Толю полиции и потом позвонить ему сами знаешь куда.",
        "condition": "tolea_sdan == 1 and path_tolya == 1",
    },
    {
        "id": "partner_in_crime",
        "title": "Товарищ по скаму",
        "description": "Договориться с Толей работать вместе.",
        "condition": "path_tolya == 2",
    },
    {
        "id": "poster_hanger",
        "title": "Дизайнер окна",
        "description": "Успешно повесить рекламный плакат Sunne CL.",
        "condition": "posilka == 5",
    },
    {
        "id": "rich_man",
        "title": "Новый русский бедняк",
        "description": "Накопить одновременно три тысячи очков.",
        "condition": "max_points >= 3000",
    },
    {
        "id": "scam_master",
        "title": "Скам-мастер",
        "description": "Довести скам с Толей до конца и получить деньги.",
        "condition": "gamecorpscam == 1",
    },
    {
        "id": "paranoid",
        "title": "Со мной всё хорошо",
        "description": "После сдачи Толи дожить до второго тревожного утра.",
        "condition": "paranoya_day >= 2",
    },
    {
        "id": "phone_addict",
        "title": "Телефонный наркоман",
        "description": "Ответить на пятнадцать звонков корпораций.",
        "condition": "calls_answered >= 15",
    },
    {
        "id": "dlc_first_look",
        "title": "Любитель мелкого шрифта",
        "description": "Открыть Vibe Plus и добраться до первой главы досье.",
        "condition": "vibe_chapter >= 1",
    },
    {
        "id": "dlc_side_business",
        "title": "Двойное списание",
        "description": "Закрыть побочное дело внутри Vibe Plus.",
        "condition": "vibe_side_quest in ('billing_records', 'subscriber_testimony', 'completed')",
    },
    {
        "id": "dlc_dossier",
        "title": "Досьё закрыто",
        "description": "Довести сюжет Vibe Plus до финального письма.",
        "condition": "vibe_chapter >= 11",
    },
    {
        "id": "dlc_lawyer",
        "title": "Народный адвокат",
        "description": "Довести второе заседание Vibe Plus до вердикта.",
        "condition": "vibe_chapter >= 17",
    },
    {
        "id": "dlc_full_dossier",
        "title": "Коллектор-энтузиаст",
        "description": "Собрать четыре документа в деле Vibe Plus.",
        "condition": "vibe_evidence >= 4",
    },
    {
        "id": "dlc_archive_consent",
        "title": "Согласие в приложении",
        "description": "Завершить дело после публикации историй с подтверждённым согласием.",
        "condition": "vibe_archive_policy == 'public_consented' and vibe_case_completed",
    },
    {
        "id": "dlc_archive_restricted",
        "title": "Архив не для всех",
        "description": "Завершить дело с архивом, доступным только судебной группе.",
        "condition": "vibe_archive_policy == 'restricted' and vibe_case_completed",
    },
    {
        "id": "dlc_archive_summary",
        "title": "Сводка без подробностей",
        "description": "Завершить дело, передав только обезличенную сводку.",
        "condition": "vibe_archive_policy == 'summary_only' and vibe_case_completed",
    },
    {
        "id": "dlc_archive_declined",
        "title": "Не публиковать — тоже выбор",
        "description": "Завершить дело, сознательно пропустив архив жалоб.",
        "condition": "vibe_archive_policy == 'skipped' and vibe_case_completed",
    },
    {
        "id": "dlc_consent_pending",
        "title": "Письмо с просьбой подождать",
        "description": "Завершить дело, оставив публикацию закрытой до ответа на запрос согласия.",
        "condition": "vibe_archive_policy == 'consent_pending' and vibe_case_completed",
    },
    {
        "id": "dlc_trusted_evidence",
        "title": "Доверие подшито к делу",
        "description": "Завершить дело с доверием не ниже 3 и минимум четырьмя доказательствами.",
        "condition": "vibe_trust >= 3 and vibe_evidence >= 4 and vibe_case_completed",
    },
    {
        "id": "dlc_private_evidence",
        "title": "Документы под замком",
        "description": "Завершить дело с доверием и доказательствами, сохранив закрытый или сводный архив.",
        "condition": "vibe_trust >= 2 and vibe_evidence >= 2 and vibe_archive_policy in ('restricted', 'summary_only') and vibe_case_completed",
    },
    {
        "id": "dlc_sidequest_documents",
        "title": "Побочка пошла в папку",
        "description": "Завершить побочное дело и основное разбирательство минимум с четырьмя доказательствами.",
        "condition": "vibe_side_quest in ('billing_records', 'subscriber_testimony', 'completed') and vibe_evidence >= 4 and vibe_case_completed",
    },
    {
        "id": "dlc_testimony_route",
        "title": "Свидетели — в общий чат",
        "description": "Собрать показания подписчиков и завершить дело по маршруту их объединения.",
        "condition": "vibe_side_quest == 'subscriber_testimony' and vibe_route == 'union' and vibe_case_completed",
    },
    {
        "id": "dlc_ending_consented",
        "title": "Согласие зафиксировано",
        "description": "Получить финал публикации с согласием.",
        "condition": "vibe_ending == 'consented_archive'",
    },
    {
        "id": "dlc_ending_protected",
        "title": "Архив под защитой",
        "description": "Получить финал защищённого архива.",
        "condition": "vibe_ending == 'protected_archive'",
    },
    {
        "id": "dlc_ending_summary",
        "title": "Имена оставили за кадром",
        "description": "Получить финал обезличенной сводки.",
        "condition": "vibe_ending == 'anonymous_summary'",
    },
    {
        "id": "dlc_ending_counterclaim",
        "title": "Встречное предложение",
        "description": "Получить финал встречного требования к компании.",
        "condition": "vibe_ending == 'counter_claim'",
    },
    {
        "id": "dlc_ending_independent",
        "title": "Независимая подпись",
        "description": "Получить финал передачи документов третьей стороне.",
        "condition": "vibe_ending == 'third_party'",
    },
    {
        "id": "dlc_press_route",
        "title": "Заголовок проверен юристом",
        "description": "Завершить разбирательство, начав его по маршруту независимой прессы.",
        "condition": "vibe_origin_route == 'press' and vibe_case_completed",
    },
)

ACHIEVEMENT_IDS = tuple(item["id"] for item in ACHIEVEMENTS)


def default_stats():
    return {key: 0 for key in STAT_KEYS}


def default_state():
    return {
        "version": ACHIEVEMENT_VERSION,
        "stats": default_stats(),
        "unlocked": {},
    }


def normalize_state(value):
    if not isinstance(value, dict):
        return default_state()

    version = value.get("version", ACHIEVEMENT_VERSION)
    if not isinstance(version, int) or isinstance(version, bool) or version < 1:
        version = ACHIEVEMENT_VERSION

    raw_stats = value.get("stats")
    if not isinstance(raw_stats, dict):
        raw_stats = {}
    stats = default_stats()
    for key in STAT_KEYS:
        current = raw_stats.get(key, 0)
        if isinstance(current, bool):
            continue
        if isinstance(current, int) and current > 0:
            stats[key] = current

    raw_unlocked = value.get("unlocked")
    if not isinstance(raw_unlocked, dict):
        raw_unlocked = {}
    unlocked = {}
    for key, day in raw_unlocked.items():
        if key not in ACHIEVEMENT_IDS:
            continue
        if isinstance(day, bool) or not isinstance(day, int):
            continue
        if day < 0:
            continue
        unlocked[key] = day
    return {"version": version, "stats": stats, "unlocked": unlocked}


def build_context(snapshot, vibe_plus):
    context = {}
    if not isinstance(snapshot, dict):
        snapshot = {}
    for key, value in snapshot.items():
        if isinstance(key, str) and key.startswith("vibe_"):
            continue
        if isinstance(value, bool) or not isinstance(value, int):
            continue
        context[key] = value

    if isinstance(vibe_plus, dict):
        chapter = vibe_plus.get("chapter", 0)
        if not isinstance(chapter, bool) and isinstance(chapter, int):
            context["vibe_chapter"] = max(0, chapter)
        evidence = vibe_plus.get("evidence", 0)
        if not isinstance(evidence, bool) and isinstance(evidence, int) and evidence >= 0:
            context["vibe_evidence"] = max(0, evidence)
        route = vibe_plus.get("route")
        if isinstance(route, str) and route in VIBE_ROUTE_VALUES:
            context["vibe_route"] = route
        origin_route = vibe_plus.get("origin_route")
        if isinstance(origin_route, str) and origin_route in VIBE_ORIGIN_ROUTE_VALUES:
            context["vibe_origin_route"] = origin_route
        ending = vibe_plus.get("ending")
        if isinstance(ending, str) and ending in VIBE_ENDING_VALUES:
            context["vibe_ending"] = ending
            context["vibe_case_completed"] = ending in VIBE_FINAL_ENDINGS
        side_quest = vibe_plus.get("side_quest")
        if isinstance(side_quest, str) and side_quest in VIBE_SIDE_QUEST_VALUES:
            context["vibe_side_quest"] = side_quest
        archive_policy = vibe_plus.get("archive_policy")
        if isinstance(archive_policy, str) and archive_policy in VIBE_ARCHIVE_POLICIES:
            context["vibe_archive_policy"] = archive_policy
        trust_level = vibe_plus.get("trust_level", 0)
        if (
            not isinstance(trust_level, bool)
            and isinstance(trust_level, int)
            and trust_level in range(5)
        ):
            context["vibe_trust"] = trust_level

    stats = context.get("stats")
    if isinstance(stats, dict):
        for key, value in stats.items():
            if isinstance(value, bool) or not isinstance(value, int):
                continue
            context[key] = value
    return context


def check(context):
    result = []
    if not isinstance(context, dict):
        return result
    variables = dict(context)
    stats = variables.get("stats")
    if isinstance(stats, dict):
        variables.update(stats)
    for achievement in ACHIEVEMENTS:
        try:
            if eval(achievement["condition"], {"__builtins__": {}}, variables):
                result.append(achievement["id"])
        except Exception:
            continue
    return result


def update(state, context, events=None):
    normalized = normalize_state(state)
    stats = normalized["stats"]
    unlocked = normalized["unlocked"]
    changed = False

    if isinstance(events, dict):
        activity = events.get("activity")
        field = COUNTER_FIELDS.get(activity) if isinstance(activity, str) else None
        if field:
            stats[field] += 1
            changed = True
        if events.get("event") == "fishing_start":
            stats["fishing_sessions"] += 1
            changed = True
        if events.get("event") == "fishing_catch":
            stats["fishing_catches"] += 1
            changed = True
        if events.get("event") == "call_answered":
            stats["calls_answered"] += 1
            changed = True
        if events.get("event") == "vibe_plus_visit":
            stats["vibe_plus_visits"] += 1
            changed = True
        delta = events.get("points_delta")
        if isinstance(delta, int) and not isinstance(delta, bool):
            if delta > 0:
                stats["points_earned"] += delta
                changed = True
            elif delta < 0:
                stats["points_spent"] += -delta
                changed = True

    if isinstance(context, dict):
        day = context.get("day", 0)
        if isinstance(day, int) and not isinstance(day, bool) and day > stats["days"]:
            stats["days"] = day
            changed = True
        points = context.get("ochko", 0)
        if isinstance(points, int) and not isinstance(points, bool) and points > stats["max_points"]:
            stats["max_points"] = points
            changed = True

    full_context = {"stats": stats}
    if isinstance(context, dict):
        for key, value in context.items():
            if key != "stats":
                full_context[key] = value
    for achievement_id in check(full_context):
        if achievement_id not in unlocked:
            day = full_context.get("day", 0)
            if isinstance(day, bool) or not isinstance(day, int) or day < 0:
                day = 0
            unlocked[achievement_id] = day
            changed = True

    if not changed:
        return state
    new_state = deepcopy(normalized)
    new_state["unlocked"] = dict(unlocked)
    return new_state


def render(console, state, snapshot, vibe_plus):
    normalized = normalize_state(state)
    context = build_context(snapshot, vibe_plus)
    context["stats"] = normalized["stats"]
    earned = set(check(context)) | set(normalized["unlocked"].keys())

    table = Table(title="Достижения и статистика прохождения")
    table.add_column("Достижение", style="bright_magenta")
    table.add_column("Статус")
    table.add_column("Описание")
    for achievement in ACHIEVEMENTS:
        got = achievement["id"] in earned
        status = "[green]получено[/]" if got else "[red]ещё нет[/]"
        title = f"[green]{achievement['title']}[/]" if got else achievement["title"]
        table.add_row(title, status, achievement["description"])

    stats = normalized["stats"]
    total = len(ACHIEVEMENTS)
    count = sum(1 for achievement in ACHIEVEMENTS if achievement["id"] in earned)
    summary = Table.grid(padding=(0, 2))
    summary.add_column(justify="right")
    summary.add_column(style="cyan", justify="left")
    summary.add_row("Получено достижений:", f"{count} из {total}")
    summary.add_row("Прожито дней:", str(max(stats["days"], context.get("day", 0))))
    summary.add_row("Текущие очки:", str(context.get("ochko", 0)))
    summary.add_row("Лучший баланс:", str(max(stats["max_points"], context.get("ochko", 0))))
    summary.add_row("Заработано всего:", str(stats["points_earned"]))
    summary.add_row("Потрачено всего:", str(stats["points_spent"]))
    summary.add_row("Бытовые занятия:", str(stats["chores_dishes"] + stats["chores_floor"] + stats["chores_trash"] + stats["chores_nerve"] + stats["chores_games"]))
    summary.add_row("Рыбалка:", f"{stats['fishing_sessions']} выходов, {stats['fishing_catches']} поклёвок")
    summary.add_row("Принятых звонков:", str(stats["calls_answered"]))
    summary.add_row("Визитов в Vibe Plus:", str(stats["vibe_plus_visits"]))

    console.print(table)
    console.print(summary)
    return normalized
