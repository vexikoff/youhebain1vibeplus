from copy import deepcopy

from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text


CHAPTERS = (
    "Приглашение",
    "Первое знакомство",
    "Проверка договора",
    "Экзамен",
    "Совет директоров",
    "Подготовка документов",
    "Сбор доказательств",
    "Побочное дело",
    "Финальное заседание",
    "Подписание",
    "Проверка подписки",
    "Письмо после подписания",
    "Куда ушли деньги",
    "Сбор новых доказательств",
    "Допрос представителя Vibe Plus",
    "Подготовка публичного слушания",
    "Второе заседание",
    "Архив жалоб",
    "Ответ компании",
    "Письмо, которое всё-таки пришло",
    "Реестр обещаний",
    "Сверка с банком",
    "Совет подписчиков",
    "Аудит без печати",
    "Проверка исполнения",
    "Апелляция на апелляцию",
    "Общественный отчёт",
    "План последствий",
    "Досье закрыто",
)

CONTINUATION_OPTIONS = {
    "letter": ("opened", "delegated"),
    "promises": ("deadlines", "wording"),
    "bank_check": ("reconciled", "statement_requested", "unverified"),
    "council": ("collective", "delegates"),
    "audit": ("certified", "pending", "internal"),
    "verification": ("documented", "discrepancies", "spot_check"),
    "appeal": ("regulator", "ombudsman"),
    "report": ("public", "held", "sealed"),
    "plan": ("monitoring", "appeal", "settlement"),
}

CONTINUATION_RESULT_TEXT = {
    "compliance_monitored": "Исполнение обещаний поставили на контроль. "
    "В этот раз у контроля появился календарь.",
    "monitoring_pending": "Контроль назначен, но части документов всё ещё не хватает.",
    "appeal_reopened": "Новая проверка открыта. Уведомления уже попросили отсрочку.",
    "appeal_pending": "Повторную апелляцию приняли, но доказательств для решения пока недостаточно.",
    "supervised_settlement": "Соглашение оставили под внешним наблюдением и с проверяемыми сроками.",
    "settlement_pending": "Стороны согласились продолжить переговоры под наблюдением.",
}

ENDING_TEXT = {
    "refund": (
        "Банк вернул деньги. Он не смог вернуть время, проведённое на линии ожидания.",
        "Банк одобрил возврат. Vibe Plus прислала вам счёт за эмоциональный ущерб — "
        "себе.",
    ),
    "regulator": (
        "Регулятор заметил мелкий шрифт.",
        "Регулятор потребовал переписать условия. Юристы переписали их крупнее, "
        "но читать всё равно неприятно.",
    ),
    "union": (
        "Подписчики объединились.",
        "Вы собрали подписчиков в одну группу. Теперь у Vibe Plus один общий чат "
        "поддержки, и никто не знает, кто должен отвечать.",
    ),
    "whistleblower": (
        "Правда вышла наружу.",
        "История попала в новости. Компания назвала это «непредусмотренным "
        "публичным раскрытием очевидного».",
    ),
    "settlement": (
        "Сделка закрыта.",
        "Вы получили компенсацию. В договоре к ней прилагалась подписка на "
        "уведомления о компенсации.",
    ),
    "loophole": (
        "Условия сыграли против авторов.",
        "Вы нашли лазейку в правилах и воспользовались ею. Юрист попросил "
        "не называть это прецедентом.",
    ),
    "appeal_denied": (
        "Апелляция принята к рассмотрению.",
        "Рассмотрение назначено на дату, которую календарь пока отказывается "
        "показывать.",
    ),
    "public_exposure": (
        "Публичное разоблачение.",
        "Ваша презентация доказательств собрание всех в зале. Компания пыталась "
        "выключить проектор, но было уже поздно.",
    ),
    "legal_victory": (
        "Юридическая победа.",
        "Суд признал ущемление прав потребителей. Vibe Plus подала на кассацию "
        "в существующую реальность.",
    ),
    "corporate_surrender": (
        "Капитуляция корпорации.",
        "Под давлением доказательств и публичного внимания компания отозвала "
        "все претензии. Но оставила за собой право изменить мнение.",
    ),
    "company_accepted": (
        "Ответ принят.",
        "Компания признала ошибку и предложила выгодные условия. "
        "Вы подписали соглашение, но мелкий шрифт остался.",
    ),
    "counter_claim": (
        "Встречный иск.",
        "Ваше встречное требование заставило компанию уступить. "
        "Теперь у вас есть не только компенсация, но и гарантии.",
    ),
    "third_party": (
        "Передача документов.",
        "Третья сторона инициировала независимое расследование. "
        "Компания потеряла лицензию, а вы получили моральное удовлетворение.",
    ),
    "consented_archive": (
        "Публикация с согласием.",
        "Обезличенные истории опубликованы только с разрешения рассказчиков. "
        "Компания получила ответ общественности, а не список чужих адресов.",
    ),
    "protected_archive": (
        "Защищённый архив.",
        "Суд принял материалы с ограниченным доступом. Истории помогли делу, "
        "не превращаясь в публичное досье на пострадавших.",
    ),
    "anonymous_summary": (
        "Обезличенная сводка.",
        "Третья сторона получила только сводные данные. Отдельные истории "
        "остались закрытыми, и это тоже оказалось полезным решением.",
    ),
}


def default_state():
    return {
        "version": 6,
        "chapter": 0,
        "route": "",
        "origin_route": "",
        "approach": "",
        "ending": "",
        "exam_progress": 0,
        "side_quest": None,
        "trust_level": 0,
        "evidence": 0,
        "archive_policy": None,
        "previous_ending": "",
        "continuation": {name: None for name in CONTINUATION_OPTIONS},
        "continuation_result": "",
    }


def normalize_state(value):
    if not isinstance(value, dict):
        return default_state()

    source_version = value.get("version", 1)
    if not isinstance(source_version, int) or isinstance(source_version, bool):
        source_version = 1

    chapter = value.get("chapter", 0)
    if not isinstance(chapter, int) or isinstance(chapter, bool) or chapter not in range(len(CHAPTERS)):
        chapter = 0
    source_chapter = chapter

    route = value.get("route", "")
    origin_route = value.get("origin_route", "")
    approach = value.get("approach", "")
    ending = value.get("ending", "")
    ending_was_valid = isinstance(ending, str)
    exam_progress = value.get("exam_progress", 0)
    side_quest = value.get("side_quest", None)
    trust_level = value.get("trust_level", 0)
    evidence = value.get("evidence", 0)
    archive_policy = value.get("archive_policy", None)
    previous_ending = value.get("previous_ending", "")
    continuation_source = value.get("continuation", {})
    continuation_result = value.get("continuation_result", "")

    if not isinstance(route, str):
        route = ""
    if not isinstance(origin_route, str):
        origin_route = ""
    if not isinstance(approach, str):
        approach = ""
    if not ending_was_valid:
        ending = ""
    if not isinstance(ending, str):
        ending = ""
    if not isinstance(exam_progress, int) or isinstance(exam_progress, bool) or exam_progress not in range(4):
        exam_progress = 0
    if side_quest is not None and not isinstance(side_quest, str):
        side_quest = None
    if not isinstance(trust_level, int) or isinstance(trust_level, bool) or trust_level not in range(5):
        trust_level = 0
    if not isinstance(evidence, int) or isinstance(evidence, bool) or evidence < 0:
        evidence = 0
    if archive_policy not in (
        None,
        "public_consented",
        "consent_pending",
        "restricted",
        "summary_only",
        "skipped",
    ):
        archive_policy = None
    if not isinstance(previous_ending, str):
        previous_ending = ""
    if not isinstance(continuation_source, dict):
        continuation_source = {}
    continuation = {
        name: continuation_source.get(name)
        if continuation_source.get(name) in options
        else None
        for name, options in CONTINUATION_OPTIONS.items()
    }
    if not isinstance(continuation_result, str) or continuation_result not in CONTINUATION_RESULT_TEXT:
        continuation_result = ""

    if source_version == 1 and chapter == 11:
        chapter = 13
    if source_version == 2 and chapter == 14:
        chapter = 16
    if source_version == 2 and chapter == 15:
        chapter = 17
    if source_version == 3 and chapter == 16:
        chapter = 17
    if source_version == 3 and chapter == 17:
        chapter = 18
    if source_version < 3 and chapter == 15:
        chapter = 17
    if source_version < 4 and chapter == 17:
        chapter = 18
    if source_version < 5 and chapter >= 17:
        chapter += 1
    if source_version < 6 and chapter == 19:
        chapter = len(CHAPTERS) - 1
        if ending and not previous_ending:
            previous_ending = ending
    if chapter not in range(len(CHAPTERS)):
        chapter = 0
    if source_version < 3 and source_chapter == 11 and not ending and ending_was_valid:
        ending = "Вы закрыли досье. Уведомления пока думают, что это не окончательно."
    if source_version < 3 and source_chapter == 15 and not ending and ending_was_valid:
        ending = "Вы закрыли досье. Уведомления пока думают, что это не окончательно."

    return {
        "version": 6,
        "chapter": chapter,
        "route": route,
        "origin_route": origin_route,
        "approach": approach,
        "ending": ending,
        "exam_progress": exam_progress,
        "side_quest": side_quest,
        "trust_level": trust_level,
        "evidence": evidence,
        "archive_policy": archive_policy,
        "previous_ending": previous_ending,
        "continuation": continuation,
        "continuation_result": continuation_result,
    }


def _show_dossier(console, state, day, points):
    chapter = state["chapter"]
    progress = Table.grid(padding=(0, 2))
    progress.add_column(style="bold cyan")
    progress.add_column()

    for index, title in enumerate(CHAPTERS):
        marker = "[green]●[/]" if index < chapter else "[cyan]◉[/]" if index == chapter else "[dim]○[/]"
        progress.add_row(marker, title)

    if chapter == 0:
        status = "Заблокировано до 3-го дня" if day < 3 else "Входящее письмо ждёт ответа"
    elif chapter == 1:
        status = "Первое знакомство с Vibe Plus"
    elif chapter == 2:
        status = "Договор вскрыт. Выбор ещё можно испортить."
    elif chapter == 3:
        status = f"Экзамен: {state['exam_progress']}/3 вопросы"
    elif chapter == 4:
        status = "Совет директоров собран"
    elif chapter == 5:
        status = "Документы готовятся"
    elif chapter == 6:
        status = "Сбор доказательств"
    elif chapter == 7:
        status = "Побочное дело" + (
            " — выполнено"
            if state["side_quest"] in ("completed", "billing_records", "subscriber_testimony")
            else ""
        )
    elif chapter == 8:
        status = "Финальное заседание"
    elif chapter == 9:
        status = "Подписание документа"
    elif chapter == 10:
        status = "Проверка подписки"
    elif chapter == 11:
        status = "Условия мелким шрифтом стали условиями крупного разговора"
    elif chapter == 12:
        status = "Выбор инстанции"
    elif chapter == 13:
        status = f"Найдено документов: {state['evidence']}"
    elif chapter == 14:
        status = "Допрос представителя Vibe Plus"
    elif chapter == 15:
        status = "Подготовка публичного слушания"
    elif chapter == 16:
        status = "Второе заседание"
    elif chapter == 17:
        status = "Архив жалоб"
    elif chapter == 18:
        status = "Ответ компании"
    elif chapter == 19:
        status = "Письмо, которое всё-таки пришло"
    elif chapter == 20:
        status = "Реестр обещаний"
    elif chapter == 21:
        status = "Сверка с банком"
    elif chapter == 22:
        status = "Совет подписчиков"
    elif chapter == 23:
        status = "Аудит без печати"
    elif chapter == 24:
        status = "Проверка исполнения"
    elif chapter == 25:
        status = "Апелляция на апелляцию"
    elif chapter == 26:
        status = "Общественный отчёт"
    elif chapter == 27:
        status = "План последствий"
    elif chapter == 28:
        status = f"Досье закрыто: {state['ending']}"
    else:
        status = "Ожидание"

    trust_text = f"Уровень доверия: {'★' * state['trust_level']}{'☆' * (5 - state['trust_level'])}"

    console.print(Panel(
        Text.from_markup(
            "[bold bright_magenta]V I B E   P L U S[/]\n"
            "[dim]РАСШИРЕНИЕ • «УСЛОВИЯ ПРИМЕНЕНИЯ» • ВЕРСИЯ 1.0[/]\n\n"
            f"[white]{status}[/]\n"
            f"[green]Баланс: {points} очков[/]   [cyan]День: {day}[/]\n"
            f"[yellow]{trust_text}[/]"
        ),
        border_style="bright_magenta",
        title="[bold white]ВНЕШНИЙ МОДУЛЬ[/]",
        subtitle="[dim]Любое сходство с подписками случайно и списывается ежемесячно[/]",
        padding=(1, 2),
    ))
    console.print(Panel(progress, border_style="cyan", title=f"Досье: {len(CHAPTERS) - 1} игровых глав"))


def run(console, points, day, saved_state):
    state = normalize_state(deepcopy(saved_state))
    _show_dossier(console, state, day, points)

    if state["chapter"] == 0:
        if day < 3:
            console.print(Panel(
                "В почтовом ящике пока только квитанция за электричество.\n"
                "Даже корпорация решила не портить вам первые три дня.",
                border_style="yellow",
            ))
            return points, state

        console.print(Panel(
            "На экране всплывает письмо от «Vibe Plus»: «Поздравляем! Вы почти "
            "подписаны». Вы ничего не нажимали, но юридически это не мешает им.",
            border_style="bright_magenta",
        ))
        console.print("[cyan]1.[/] Прочитать письмо (бесплатно)")
        console.print("[cyan]2.[/] Купить приоритетную проверку (80 очков)")
        console.print("[cyan]3.[/] Закрыть письмо и жить в неведении")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state.update(chapter=1, route="standard", approach="standard")
        elif choice == "2":
            if points < 80:
                console.print("[red]Не хватает 80 очков. Даже мошенникам нужна ликвидность.[/]")
                return points, state
            points -= 80
            state.update(chapter=1, route="premium", approach="premium", trust_level=1)
        else:
            console.print("[dim]Письмо закрыто. Оно откроется само. Конечно же.[/]")
        return points, state

    if state["chapter"] == 1:
        console.print(Panel(
            "Вы открыли письмо. Vibe Plus приветствует вас в мировом сообществе.\n"
            "Теперь нужно пройти небольшое собеседование.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Продолжить собеседование")
        console.print("[cyan]2.[/] Прервать и уйти")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            state.update(chapter=2)
        else:
            console.print("[dim]Вы ушли. Но они всё равно найдут вас.[/]")
        return points, state

    if state["chapter"] == 2:
        console.print(Panel(
            "Юрист называет тариф «Бессрочный пробный период»: первые 14 лет "
            "бесплатно, дальше — по настроению бухгалтерии.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Подписаться без проверки")
        console.print("[cyan]2.[/] Пройти экзамен")
        console.print("[cyan]3.[/] Потребовать полный текст договора")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="2")
        if choice == "1":
            state.update(chapter=9, route="blind_sign", approach="blind_sign")
        elif choice == "2":
            state.update(chapter=3, route="exam", approach="exam", exam_progress=0)
        else:
            state.update(chapter=4, route="full_text", approach="full_text")
        return points, state

    if state["chapter"] == 3:
        if state["exam_progress"] == 0:
            console.print(Panel("Вопрос 1: Что такое автопродление?", border_style="yellow"))
            console.print("[cyan]1.[/] Autistic production")
            console.print("[cyan]2.[/] Автоматическое продление подписки")
            console.print("[cyan]3.[/] Вид маркетинга")
            choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="2")
            if choice == "2":
                state["exam_progress"] = 1
                state["trust_level"] = min(state["trust_level"] + 1, 4)
                points += 50
            else:
                console.print("[red]Неправильно! Минус 20 очков.[/]")
                points -= 20
                state["exam_progress"] = 1
        elif state["exam_progress"] == 1:
            console.print(Panel("Вопрос 2: Можно ли отменить автопродление?", border_style="yellow"))
            console.print("[cyan]1.[/] Да, в личном кабинете")
            console.print("[cyan]2.[/] Нет, это навсегда")
            console.print("[cyan]3.[/] Только по телефону поддержки")
            choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
            if choice == "1":
                state["exam_progress"] = 2
                state["trust_level"] = min(state["trust_level"] + 1, 4)
                points += 50
            else:
                console.print("[red]Неправильно! Минус 20 очков.[/]")
                points -= 20
                state["exam_progress"] = 2
        elif state["exam_progress"] == 2:
            console.print(Panel("Вопрос 3: Что будет если не отменить?", border_style="yellow"))
            console.print("[cyan]1.[/] С вас спишут деньги")
            console.print("[cyan]2.[/] Вас заблокируют")
            console.print("[cyan]3.[/] Ничего не будет")
            choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
            if choice == "1":
                state["exam_progress"] = 3
                state["trust_level"] = min(state["trust_level"] + 1, 4)
                points += 100
                console.print("[green]Экзамен сдан! +100 очков[/]")
                state.update(chapter=4, route="exam_passed")
            else:
                console.print("[red]Экзамен не сдан. Начинаем заново.[/]")
                state["exam_progress"] = 0
        return points, state

    if state["chapter"] == 4:
        console.print(Panel(
            "Совет директоров собрался в переговорной. На столе вода, "
            "договор на 47 страниц и единственный стул для вас.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Передать договор независимой газете")
        console.print("[cyan]2.[/] Устроиться консультантом")
        console.print("[cyan]3.[/] Позвонить Толе")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        routes = {"1": "press", "2": "consultant", "3": "tolya"}
        state.update(chapter=5, route=routes[choice], origin_route=routes[choice])
        return points, state

    if state["chapter"] == 5:
        preparation_scenes = {
            "press": "Редактор газеты просит документы. Он уже подготовил заголовок: "
            "«Компания раскрыла условия», но оставил место для уточнения, какие именно.",
            "consultant": "Коллеги-консультанты принесли папку. В ней есть план отмены, "
            "но сначала план отмены самого плана.",
            "tolya": "Толя присылает список документов и отдельную инструкцию: "
            "«Не открывай файл final_final_точно_последний.pdf».",
        }
        console.print(Panel(
            "Начинается подготовка документов. Нужно собрать доказательства.\n\n"
            + preparation_scenes.get(
                state["route"],
                "Архив выдаёт папку и уверяет, что внутри всё необходимое. "
                "Папка подозрительно лёгкая.",
            ),
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Собрать документы самостоятельно")
        console.print("[cyan]2.[/] Попросить помощь (+50 очков)")
        console.print("[cyan]3.[/] Найти ready-made пакет")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "2":
            points += 50
        state.update(chapter=6)
        return points, state

    if state["chapter"] == 6:
        evidence_scenes = {
            "press": "Редактор ждёт подтверждений. Его дедлайн — вчера, но он готов "
            "сделать вид, что сегодня.",
            "consultant": "Консультант предлагает сверить пункты. За каждую сверку "
            "он выставляет отдельный счёт за сверку счёта.",
            "tolya": "Толя находит письмо с условиями. Оно отправлено вам за день до "
            "того, как вы узнали о существовании подписки.",
        }
        console.print(Panel(
            "Сбор доказательств. Время истекает.\n\n"
            + evidence_scenes.get(
                state["route"],
                "В архиве заканчивается бумага, но не заканчиваются заявления, "
                "что бумага закончилась.",
            ),
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Подождать ещё недельку")
        console.print("[cyan]2.[/] Собрать что есть и идти на заседание")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="2")
        if choice == "1":
            console.print("[yellow]Прошла неделя. Доказательств не прибавилось, "
                          "зато календарь теперь соответствует текущему году.[/]")
        else:
            hearing_scenes = {
                "press": "Редактор берёт папку и обещает проверить каждую страницу "
                "до публикации. Он не уточняет, в каком году.",
                "consultant": "Консультант ставит на папке печать «проверено». "
                "Проверено кем — следующий тариф.",
                "tolya": "Толя подтверждает подлинность файлов и присылает ещё один "
                "файл. На этот раз без слова «финальный» в названии.",
            }
            console.print(
                "[cyan]"
                + hearing_scenes.get(
                    state["route"],
                    "Вы собираете документы и надеетесь, что скрепка тоже считается уликой.",
                )
                + "[/]"
            )
        state.update(chapter=7)
        return points, state

    if state["chapter"] == 7:
        console.print(Panel(
            "Побочное дело: можно проверить журнал списаний или найти других "
            "подписчиков. Оно необязательно и не блокирует основное дело.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Проверить журнал двойных списаний")
        console.print("[cyan]2.[/] Собрать показания других подписчиков")
        console.print("[cyan]3.[/] Пропустить побочное дело")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            points += 100
            state.update(
                chapter=8,
                side_quest="billing_records",
                trust_level=min(state["trust_level"] + 1, 4),
            )
            console.print("[green]Журнал списаний приложен к делу. +100 очков[/]")
        elif choice == "2":
            points += 100
            state.update(
                chapter=8,
                side_quest="subscriber_testimony",
                trust_level=min(state["trust_level"] + 1, 4),
            )
            console.print("[green]Показания подписчиков записаны. +100 очков[/]")
        else:
            state.update(chapter=8)
        return points, state

    if state["chapter"] == 8:
        hearing_openings = {
            "press": "Редактор включает диктофон. На записи слышно, как юрист "
            "просит не записывать.",
            "consultant": "Консультант занимает место свидетеля и выставляет счёт "
            "за присутствие в зале.",
            "tolya": "Толя подключается по видеосвязи. Камера показывает потолок, "
            "зато микрофон работает без подписки.",
        }
        console.print(Panel(
            "Финальное заседание. Все документы на столе.\n\n"
            + hearing_openings.get(
                state["route"],
                "Председатель проверяет папку и спрашивает, есть ли возражения. "
                "Юрист возражает против самого вопроса.",
            ),
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Представить доказательства")
        console.print("[cyan]2.[/] Переложить вину на соседа")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            state.update(chapter=9, route="honest")
        else:
            state.update(chapter=9, route="blame")
        return points, state

    if state["chapter"] == 9:
        console.print(Panel("Остался последний шаг - подписание договора.", border_style="yellow"))
        if state["route"] == "blind_sign":
            console.print("[cyan]1.[/] Подписать не читая")
            console.print("[cyan]2.[/] Всё же прочитать")
        else:
            console.print("[cyan]1.[/] Подписать с гордостью")
            console.print("[cyan]2.[/] Отказаться в последний момент")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            state.update(chapter=10, route=state["route"])
        else:
            state.update(chapter=10, route="refuse")
        return points, state

    if state["chapter"] == 10:
        final_reviews = {
            "blind_sign": "На экране три галочки. Одна отмечена заранее, вторая "
            "отмечена первой, третья уверяет, что галочки вообще не обязательны.",
            "honest": "Вы перечитываете условия вслух. Юрист просит говорить тише: "
            "другие клиенты тоже начали слушать.",
            "blame": "Сосед прислал сообщение: «Почему мне пришёл ваш договор?» "
            "Вы решаете, что это уже не ваша проблема.",
            "exam_passed": "Вам выдают сертификат об успешном прохождении экзамена. "
            "На обратной стороне — заявление о вступлении в подписку.",
            "full_text": "Вы дочитали договор до конца. Внизу страницы мелким шрифтом "
            "написано: «Спасибо, что дочитали до начала»",
            "press": "Редактор прислал вёрстку статьи. Заголовок уже есть, "
            "но юридический отдел предложил заменить его на пустую страницу.",
            "consultant": "Консультант нашёл лазейку. Она ведёт в форму оплаты "
            "консультации по поиску лазеек.",
            "tolya": "Толя нашёл кнопку отмены. Она спрятана за кнопкой "
            "«Подтвердить, что вы ищете кнопку отмены».",
            "refuse": "Ваш отказ зарегистрирован. Система спрашивает, уверены ли вы, "
            "что не хотите подтвердить отказ от отказа.",
        }
        console.print(Panel(
            "Проверка подписки. Последний шанс всё изменить.\n\n"
            + final_reviews.get(
                state["route"],
                "Представитель Vibe Plus ждёт решения и уже открыл форму продления.",
            ),
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Подтвердить подписку")
        console.print("[cyan]2.[/] Отменить всё")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            endings = {
                "blind_sign": "Вы подписались не читая. Теперь вы наш. Навсегда.",
                "honest": "Вы честно подписали. Vibe Plus вами гордится.",
                "blame": "Вы свалили вину на соседа. Он теперь в чёрном списке.",
                "exam_passed": "Вы сдали экзамен и подписали. Умница!",
                "full_text": "Вы прочитали всё и подписали. Но мелкий шрифт остался.",
                "press": "Вы разоблачили мошенников. Подписка отменена.",
                "consultant": "Вы нашли лазейку. Подписка бесплатная.",
                "tolya": "Толя помог отменить. Вы свободны.",
                "refuse": "Вы отказались. Форма согласия закрылась не с первого раза.",
                "perfect": "Вы закрыли побочное дело, собрали документы и всё равно "
                "получили письмо «остались ли у вас вопросы?». Конечно остались.",
            }
            ending_key = state["route"]
            if ending_key == "honest":
                if state["approach"] == "blind_sign":
                    ending_key = "blind_sign"
                elif state["approach"] == "exam" and state["exam_progress"] == 3:
                    ending_key = "exam_passed"
                elif state["approach"] == "full_text":
                    ending_key = "full_text"
                elif state["origin_route"] in ("press", "consultant", "tolya"):
                    ending_key = state["origin_route"]
            if state["side_quest"] in ("completed", "billing_records", "subscriber_testimony"):
                ending_key = "perfect"
            state.update(chapter=11, ending=endings.get(ending_key, "Подписка оформлена."))
            if choice == "1":
                points += 200
        else:
            state.update(chapter=11, ending="Вы отменили всё. Но они всё равно спишут деньги.")
            points += 50
        return points, state

    if state["chapter"] == 11:
        console.print(Panel(
            f"Через неделю приходит письмо о результате: «{state['ending']}»\n\n"
            "Внизу письма мелким шрифтом добавлено: «Результат не влияет на "
            "возможность дальнейших списаний».",
            border_style="yellow",
            title="Письмо после подписания",
        ))
        console.print("[cyan]1.[/] Оспорить списание и продолжить разбирательство")
        console.print("[cyan]2.[/] Принять компенсацию и договориться")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        state.update(chapter=12, route="appeal" if choice == "1" else "settlement")
        return points, state

    if state["chapter"] == 12:
        if state["route"] == "appeal":
            console.print(Panel(
                "Куда направить жалобу? Банк просит чек, регулятор — заявление, "
                "а подписчики — ссылку на общий чат.",
                border_style="yellow",
                title="Куда ушли деньги",
            ))
            console.print("[cyan]1.[/] Оспорить платёж через банк")
            console.print("[cyan]2.[/] Обратиться к регулятору")
            console.print("[cyan]3.[/] Собрать подписчиков вместе")
            routes = {"1": "bank", "2": "regulator", "3": "union"}
        else:
            console.print(Panel(
                "Компания предлагает закрыть вопрос. В приложении к соглашению "
                "нашёлся ещё один вопрос.",
                border_style="yellow",
                title="Переговоры о компенсации",
            ))
            console.print("[cyan]1.[/] Попросить банк вернуть деньги")
            console.print("[cyan]2.[/] Передать историю журналистам")
            console.print("[cyan]3.[/] Использовать условия договора против компании")
            routes = {"1": "refund", "2": "press", "3": "exploit"}
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        state.update(chapter=13, route=routes[choice])
        return points, state

    if state["chapter"] == 13:
        evidence_scenes = {
            "bank": "Банк просит доказать, что платёж был неожиданным. Вы показываете "
            "ему письмо, в котором вас поздравили с тем, чего вы не делали.",
            "regulator": "Регулятор просит указать пункт договора. Юрист присылает "
            "ссылку на весь договор и называет это точностью.",
            "union": "В общем чате уже 84 участника и 85 мнений о том, кто создавал чат.",
            "refund": "Банк ищет транзакцию. Она нашлась быстрее, чем оператор поддержки.",
            "press": "Редакция просит подтвердить каждую цитату. Компания подтверждает "
            "только наличие редакции.",
            "exploit": "Вы перечитываете условия компании. На этот раз ищете не кнопку "
            "«согласен», а пункт, который они забыли проверить.",
        }
        side_quest_clues = {
            "completed": "Материалы побочного дела подтверждают, что списания были не единичными.",
            "billing_records": "Журнал показывает повторные списания по одному и тому же пункту.",
            "subscriber_testimony": "Подписчики подтверждают, что уведомления о списаниях не приходили.",
        }
        side_quest_clue = side_quest_clues.get(state["side_quest"], "")
        console.print(Panel(
            evidence_scenes.get(state["route"], "Архив ждёт документы.")
            + (f"\n\n{side_quest_clue}" if side_quest_clue else ""),
            border_style="yellow",
            title="Сбор новых доказательств",
        ))
        console.print("[cyan]1.[/] Поднять переписку и выписки (+1 документ)")
        console.print("[cyan]2.[/] Приложить материалы побочного дела (+2 документа, если оно закрыто)")
        console.print("[cyan]3.[/] Передать копию журналистам (+1 документ)")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state["evidence"] += 1
        elif choice == "2":
            has_billing_records = state["side_quest"] in ("completed", "billing_records")
            state["evidence"] += 2 if has_billing_records else 1
        else:
            state["evidence"] += 1
        state["chapter"] = 14
        return points, state

    if state["chapter"] == 14:
        interrogation_scenes = {
            "bank": "Представитель банка уверяет, что все списания были согласованы. "
            "Вы показываете скриншот пустого личного кабинета.",
            "regulator": "Представитель регулятора спрашивает, читали ли вы условия. "
            "Вы отвечаете, что читать 47 страниц — это отдельная подписка.",
            "union": "Представитель компании предлагает индивидуальные условия. "
            "Условия для всех остальных остаются старыми.",
            "refund": "Представитель банка ищет виновных. В компании все указывают "
            "друг на друга, а вы указываете на них всех.",
            "press": "Представитель компании пытается убедить, что это недоразумение. "
            "Вы показываете переписку, где они называют это бизнес-моделью.",
            "exploit": "Представитель предлагает компромисс. Компромисс заключается в том, "
            "что вы принимаете их условия.",
        }
        console.print(Panel(
            interrogation_scenes.get(state["route"], "Представитель Vibe Plus сидит "
            "напротив и улыбается. Это плохой знак."),
            border_style="yellow",
            title="Допрос представителя Vibe Plus",
        ))
        console.print(f"[yellow]Документов в деле: {state['evidence']}[/]")
        console.print("[cyan]1.[/] Требовать полные пояснения (+1 документ)")
        console.print("[cyan]2.[/] Предъявить имеющиеся доказательства (+0, проверка текущих)")
        console.print("[cyan]3.[/] Записать допрос на камеру (+1 документ)")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state["evidence"] += 1
            console.print("[green]Получен протокол допроса.[/]")
        elif choice == "3":
            state["evidence"] += 1
            console.print("[green]Видеозапись добавлена в дело.[/]")
        state["chapter"] = 15
        return points, state

    if state["chapter"] == 15:
        preparation_scenes = {
            "bank": "Банк объявляет дату слушания. На календаре это число "
            "уже прошло, но в компании ещё не знают.",
            "regulator": "Регулятор готовит заседание. В замечаниях значится: "
            "«Проверить наличие подписчиков у компании».",
            "union": "Подписчики готовят коллективное заявление. "
            "Его длина превышает длину всех предыдущих договоров.",
            "refund": "Банк обещает предоставить часть доказательств. "
            "Часть, которая не на руке у компании.",
            "press": "Журналисты готовят публикацию. Коэффициент достоверности: "
            "98%. Оставшиеся 2% — это openly анонимный источник.",
            "exploit": "Вы изучаете найденные лазейки. Каждая из них ведёт "
            "к новому уровню подписки.",
        }
        side_quest_scenes = {
            "completed": "Материалы побочного дела готовы для приложения к заявлению.",
            "billing_records": "Журнал списаний можно приложить к публикации.",
            "subscriber_testimony": "Подписчики готовы подтвердить показания на слушании.",
        }
        side_quest_scene = side_quest_scenes.get(state["side_quest"], "")
        console.print(Panel(
            preparation_scenes.get(state["route"], "Подготовка к публичному слушанию. "
            "Все взгляды обращены на вас.")
            + (f"\n\n{side_quest_scene}" if side_quest_scene else ""),
            border_style="yellow",
            title="Подготовка публичного слушания",
        ))
        console.print(f"[yellow]Документов в деле: {state['evidence']}[/]")
        console.print("[cyan]1.[/] Опубликовать все доказательства" +
                      (" [green](+1 доверие)[/]" if state["trust_level"] < 4 else ""))
        console.print("[cyan]2.[/] Обратиться за поддержкой к подписчикам")
        console.print("[cyan]3.[/] Сосредоточиться на ключевых пунктах")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state["trust_level"] = min(state["trust_level"] + 1, 4)
            state["evidence"] += 1
            console.print("[green]Публикация вызвала резонанс! +1 доверие, +1 документ[/]")
        elif choice == "2":
            has_subscriber_testimony = state["side_quest"] in (
                "completed",
                "subscriber_testimony",
            )
            state["evidence"] += 2 if has_subscriber_testimony else 1
            console.print("[green]Поддержка подписчиков помогла![/]")
        state["chapter"] = 16
        return points, state

    if state["chapter"] == 16:
        hearing_lines = {
            "bank": "Банк назначил слушание. Оператор соединяет вас с отделом, "
            "который отвечает за соединение с отделом.",
            "regulator": "Регулятор открыл заседание. Компания заявила, что готова "
            "сотрудничать в пределах рабочего графика.",
            "union": "Подписчики пришли вместе. Компания считает каждого участника "
            "отдельной заявкой.",
            "refund": "Банк нашёл платёж и теперь выясняет, почему его искали так долго.",
            "press": "Журналистка готова опубликовать документы. Юрист готов "
            "опубликовать возражения к публикации.",
            "exploit": "На заседании зачитывают пункт, который вы нашли. Юрист "
            "просит перейти к следующему пункту, но их больше нет.",
        }
        console.print(Panel(
            hearing_lines.get(state["route"], "Заседание началось."),
            border_style="yellow",
            title="Второе заседание",
        ))
        console.print(f"[yellow]Документов в деле: {state['evidence']}[/]")
        console.print("[cyan]1.[/] Настоять на официальном решении")
        console.print("[cyan]2.[/] Согласиться на компенсацию")
        console.print("[cyan]3.[/] Опубликовать материалы")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "2":
            ending = "settlement"
        elif choice == "3":
            ending = "whistleblower"
        elif state["route"] == "bank":
            ending = "refund" if state["evidence"] >= 2 else "appeal_denied"
        elif state["route"] == "regulator":
            ending = "regulator" if state["evidence"] >= 2 else "appeal_denied"
        elif state["route"] == "union":
            ending = "union" if state["evidence"] >= 2 else "appeal_denied"
        elif state["route"] == "refund":
            ending = "refund" if state["evidence"] >= 1 else "appeal_denied"
        elif state["route"] == "press":
            ending = "public_exposure" if state["evidence"] >= 3 else "regulator" if state["evidence"] >= 2 else "appeal_denied"
        elif state["route"] == "exploit":
            ending = "legal_victory" if state["evidence"] >= 3 else "loophole" if state["evidence"] >= 2 else "settlement"
        else:
            ending = "loophole" if state["evidence"] >= 2 else "settlement"
        state.update(chapter=17, ending=ending)
        return points, state

    if state["chapter"] == 17:
        console.print(Panel(
            "В досье есть обезличенные истории пострадавших. Имена, адреса и "
            "контакты в архив не добавляются. Публикация возможна только с "
            "явным согласием рассказчиков.",
            border_style="yellow",
            title="Архив жалоб",
        ))
        console.print(
            f"[yellow]Документов: {state['evidence']}   "
            f"Доверие: {state['trust_level']}/4[/]"
        )
        console.print("[cyan]1.[/] Опубликовать истории после подтверждённого согласия и обезличивания")
        console.print("[cyan]2.[/] Запросить согласие, оставив архив закрытым до ответа")
        console.print("[cyan]3.[/] Ограничить доступ к архиву судебной группой")
        console.print("[cyan]4.[/] Не публиковать истории; передать обезличенную сводку")
        console.print("[cyan]5.[/] Пропустить архив жалоб")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3", "4", "5"], default="5")
        if choice == "1":
            if state["evidence"] >= 2 and state["trust_level"] >= 2:
                archive_policy = "public_consented"
                console.print("[green]Согласие подтверждено; опубликована только обезличенная подборка.[/]")
            else:
                archive_policy = "consent_pending"
                console.print("[yellow]Сначала нужны проверенные документы и доверие рассказчиков. Публикация отложена.[/]")
        elif choice == "2":
            archive_policy = "consent_pending"
            console.print("[cyan]Запрос отправлен. Архив останется закрытым до ответа.[/]")
        elif choice == "3":
            archive_policy = "restricted"
            console.print("[cyan]Архив доступен только судебной группе; публичной публикации не будет.[/]")
        elif choice == "4":
            archive_policy = "summary_only"
            console.print("[cyan]В дело попадёт только обезличенная сводка, не отдельные истории.[/]")
        else:
            archive_policy = "skipped"
            console.print("[dim]Архив пропущен. Рассмотрение дела продолжается.[/]")
        state.update(chapter=18, archive_policy=archive_policy)
        return points, state

    if state["chapter"] == 18:
        response_scenes = {
            "refund": "Компания согласна вернуть деньги. В письме сказано: "
            "«Ошибка код 404: ваших денег у нас нет». Но чек прилагается.",
            "regulator": "Компания предлагает урегулировать вопрос до судебного разбирательства. "
            "Их юристы уже подготовили новый договор.",
            "union": "Компания предлагает встретиться с каждым подписчиком лично. "
            "В отдельности условия звучат иначе.",
            "public_exposure": "Компания пытается опровергнуть публикацию. "
            "Их пресс-релиз длиннее вашего досье.",
            "legal_victory": "Компания предлагает мировое соглашение. "
            "Они называют это победой, вы — компромиссом.",
            "corporate_surrender": "Компания признаёт поражение и обещает исправиться. "
            "Но в мелком шрифте что-то про «бету».",
            "settlement": "Компания готова выплатить компенсацию. "
            "Сумма указана, но условия получения — на отдельной странице.",
            "whistleblower": "Компания угрожает судом за клевету. "
            "Их адвокаты уже ждут вашего ответа.",
            "loophole": "Компания нашла лазейку в вашем иске. "
            "Они предлагают начать всё сначала.",
            "appeal_denied": "Компания игнорирует апелляцию. "
            "Они считают, что время работает на них.",
        }
        archive_scenes = {
            "public_consented": "Обезличенные истории опубликованы с разрешения рассказчиков.",
            "consent_pending": "Согласия ещё ждут; содержание архива не раскрывается.",
            "restricted": "Доступ к архиву ограничен судебной группой.",
            "summary_only": "Отдельные истории закрыты; в деле только обезличенная сводка.",
            "skipped": "Архив жалоб не создавался.",
        }
        archive_scene = archive_scenes.get(state["archive_policy"], "")
        console.print(Panel(
            response_scenes.get(state["ending"], "Компания подготовила официальный ответ. "
            "Он начинается с извинений и заканчивается новым предложением.")
            + (f"\n\n{archive_scene}" if archive_scene else ""),
            border_style="yellow",
            title="Ответ компании",
        ))
        console.print("[cyan]1.[/] Принять ответ компании")
        console.print("[cyan]2.[/] Предъявить встречное требование")
        console.print("[cyan]3.[/] Передать документы третьей стороне")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            if (
                state["archive_policy"] == "public_consented"
                and state["evidence"] >= 2
                and state["trust_level"] >= 2
            ):
                final_ending = "consented_archive"
            else:
                final_ending = "company_accepted"
        elif choice == "2":
            if (
                state["archive_policy"] == "restricted"
                and state["evidence"] >= 2
                and state["trust_level"] >= 2
            ):
                final_ending = "protected_archive"
            else:
                final_ending = "counter_claim"
        else:
            if (
                state["archive_policy"] == "summary_only"
                and state["evidence"] >= 2
                and state["trust_level"] >= 1
            ):
                final_ending = "anonymous_summary"
            else:
                final_ending = "third_party"
        state.update(
            chapter=19,
            ending=final_ending,
            previous_ending=final_ending,
        )
        return points, state

    if state["chapter"] == 19:
        previous_result = ENDING_TEXT.get(
            state["previous_ending"] or state["ending"],
            ("Результат сохранён.", ""),
        )[0]
        archive_scenes = {
            "public_consented": "Разрешённые обезличенные истории уже опубликованы.",
            "consent_pending": "Ответы рассказчиков ещё ждут; вложения закрыты.",
            "restricted": "Архив по-прежнему доступен только судебной группе.",
            "summary_only": "Вместо историй доступна только обезличенная сводка.",
            "skipped": "Архив жалоб вы не заводили.",
        }
        console.print(Panel(
            f"После результата «{previous_result}» пришло письмо от компании. "
            "В нём обещают всё исправить, но забыли указать, что именно.\n\n"
            + archive_scenes.get(state["archive_policy"], "Приложений к письму пока нет."),
            border_style="yellow",
            title="Письмо, которое всё-таки пришло",
        ))
        console.print("[cyan]1.[/] Открыть письмо и проверить срок ответа")
        console.print("[cyan]2.[/] Переслать письмо представителям подписчиков")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        state["continuation"]["letter"] = "opened" if choice == "1" else "delegated"
        state["chapter"] = 20
        return points, state

    if state["chapter"] == 20:
        letter_scenes = {
            "opened": "В письме есть обещание, срок и сноска, которая пытается стать главным документом.",
            "delegated": "Совет подписчиков открыл пересланное письмо. Файл называется "
            "«ответ_точно_окончательный_финал.pdf».",
        }
        console.print(Panel(
            letter_scenes.get(state["continuation"]["letter"], "Письмо всё ещё в пути."),
            border_style="yellow",
            title="Реестр обещаний",
        ))
        console.print("[cyan]1.[/] Записать обещания вместе со сроками и ответственными")
        console.print("[cyan]2.[/] Сохранить только формулировки компании")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        state["continuation"]["promises"] = "deadlines" if choice == "1" else "wording"
        state["chapter"] = 21
        return points, state

    if state["chapter"] == 21:
        route_scenes = {
            "bank": "Банк узнаёт номер дела. На этот раз соединение не требует отдельного заявления.",
            "refund": "Банк нашёл платёж. Теперь он проверяет, не нашёл ли его кто-то раньше.",
            "regulator": "Банк просит приложить распоряжение регулятора, даже если его ещё нет.",
            "union": "Подписчики принесли выписки. У каждой своя версия банковского приложения.",
        }
        promise_scene = (
            "Сроки из реестра можно сверить с транзакциями."
            if state["continuation"]["promises"] == "deadlines"
            else "Без сроков даже выписка выглядит как календарь, который не хочет брать ответственность."
        )
        console.print(Panel(
            route_scenes.get(state["route"], "Банк изучает историю платежей.")
            + "\n\n"
            + promise_scene,
            border_style="yellow",
            title="Сверка с банком",
        ))
        console.print("[cyan]1.[/] Сверить операции с письмом компании")
        console.print("[cyan]2.[/] Запросить заверенную выписку")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            is_reconciled = (
                state["continuation"]["letter"] == "opened"
                and state["continuation"]["promises"] == "deadlines"
                and state["route"] in ("bank", "refund")
                and state["evidence"] >= 2
            )
            state["continuation"]["bank_check"] = (
                "reconciled" if is_reconciled else "unverified"
            )
        else:
            state["continuation"]["bank_check"] = "statement_requested"
        state["chapter"] = 22
        return points, state

    if state["chapter"] == 22:
        bank_scenes = {
            "reconciled": "Суммы сошлись с обещаниями. Совпадение впервые выглядит подозрительно полезным.",
            "statement_requested": "Заверенная выписка готовится. Банк заверил, что подготовка уже началась.",
            "unverified": "Сверка не подтвердила обещания: документы разошлись раньше, чем участники заседания.",
        }
        console.print(Panel(
            bank_scenes.get(state["continuation"]["bank_check"], "Совет ждёт банковские данные."),
            border_style="yellow",
            title="Совет подписчиков",
        ))
        console.print(f"[yellow]Доверие участников: {state['trust_level']}/4[/]")
        console.print("[cyan]1.[/] Принять общее решение всем советом")
        console.print("[cyan]2.[/] Передать переговоры выбранным представителям")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        state["continuation"]["council"] = "collective" if choice == "1" else "delegates"
        state["chapter"] = 23
        return points, state

    if state["chapter"] == 23:
        archive_audit_scenes = {
            "public_consented": "Аудитор изучает только опубликованные обезличенные истории.",
            "consent_pending": "Вложения без согласия не открывают; проверяют только финансовые документы.",
            "restricted": "Аудит проходит в закрытом архиве, доступ к которому ограничен.",
            "summary_only": "Проверяют сводные данные, не отдельные истории.",
            "skipped": "Архива нет, зато остались банковские документы и обещания.",
        }
        council_scene = (
            "Общий совет сверяет выводы."
            if state["continuation"]["council"] == "collective"
            else "Представители сверяют выводы и обещают не потерять остальных подписчиков."
        )
        console.print(Panel(
            archive_audit_scenes.get(state["archive_policy"], "Аудитор работает только с материалами дела.")
            + "\n\n"
            + council_scene,
            border_style="yellow",
            title="Аудит без печати",
        ))
        console.print("[cyan]1.[/] Позвать независимого аудитора")
        console.print("[cyan]2.[/] Провести внутреннюю проверку по открытым документам")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            can_certify = (
                state["evidence"] >= 2
                and state["trust_level"] >= 2
                and state["continuation"]["bank_check"] == "reconciled"
                and state["continuation"]["council"] == "collective"
            )
            state["continuation"]["audit"] = "certified" if can_certify else "pending"
        else:
            state["continuation"]["audit"] = "internal"
        state["chapter"] = 24
        return points, state

    if state["chapter"] == 24:
        audit_scenes = {
            "certified": "Аудитор подтвердил совпадение записей и не стал заверять печатью собственное отсутствие печати.",
            "pending": "Аудитору нужны дополнительные подтверждения; одного оптимизма в приложении нет.",
            "internal": "Внутренняя проверка завершилась внутренним сообщением о внутреннем успехе.",
        }
        console.print(Panel(
            audit_scenes.get(state["continuation"]["audit"], "Результат проверки ещё не готов."),
            border_style="yellow",
            title="Проверка исполнения",
        ))
        console.print("[cyan]1.[/] Сверить выполненные обещания с документами")
        console.print("[cyan]2.[/] Попросить выборочную проверку операций")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            is_documented = (
                state["continuation"]["audit"] == "certified"
                and state["continuation"]["promises"] == "deadlines"
            )
            state["continuation"]["verification"] = (
                "documented" if is_documented else "discrepancies"
            )
        else:
            state["continuation"]["verification"] = "spot_check"
        state["chapter"] = 25
        return points, state

    if state["chapter"] == 25:
        verification_scenes = {
            "documented": "Сроки и документы совпали. Компания попросила сверить ещё и календарь.",
            "discrepancies": "В обещаниях обнаружились расхождения; юристы назвали их особенностью формата.",
            "spot_check": "Выборочная проверка нашла детали, которые обычно выбирают не замечать.",
        }
        console.print(Panel(
            verification_scenes.get(
                state["continuation"]["verification"],
                "Сроки исполнения пока не подтверждены.",
            ),
            border_style="yellow",
            title="Апелляция на апелляцию",
        ))
        console.print("[cyan]1.[/] Подать повторную жалобу регулятору")
        console.print("[cyan]2.[/] Передать спор независимому омбудсмену")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        state["continuation"]["appeal"] = "regulator" if choice == "1" else "ombudsman"
        state["chapter"] = 26
        return points, state

    if state["chapter"] == 26:
        appeal_scenes = {
            "regulator": "Регулятор принимает повторную жалобу и просит приложить не повторную жалобу.",
            "ombudsman": "Омбудсмен готов изучить спор, если стороны не начнут изучать друг друга.",
        }
        console.print(Panel(
            appeal_scenes.get(state["continuation"]["appeal"], "Новая инстанция запросила материалы."),
            border_style="yellow",
            title="Общественный отчёт",
        ))
        console.print("[cyan]1.[/] Опубликовать только разрешённые обезличенные сведения")
        console.print("[cyan]2.[/] Передать закрытый отчёт выбранной инстанции")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="2")
        if choice == "1":
            can_publish = (
                state["archive_policy"] in ("public_consented", "summary_only")
                and state["evidence"] >= 2
                and state["trust_level"] >= 2
            )
            state["continuation"]["report"] = "public" if can_publish else "held"
        else:
            state["continuation"]["report"] = "sealed"
        state["chapter"] = 27
        return points, state

    if state["chapter"] == 27:
        report_scenes = {
            "public": "Опубликован только разрешённый обезличенный отчёт; личные истории остались закрытыми.",
            "held": "Отчёт отложен: для публикации не хватает согласия или подтверждённых документов.",
            "sealed": "Закрытый отчёт передан инстанции без публичного раскрытия историй.",
        }
        console.print(Panel(
            report_scenes.get(state["continuation"]["report"], "Отчёт ещё не готов."),
            border_style="yellow",
            title="План последствий",
        ))
        console.print("[cyan]1.[/] Назначить контроль сроков и исполнения")
        console.print("[cyan]2.[/] Добиваться повторного решения по апелляции")
        console.print("[cyan]3.[/] Согласовать контролируемое урегулирование")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state["continuation"]["plan"] = "monitoring"
            result = (
                "compliance_monitored"
                if state["continuation"]["verification"] == "documented"
                and state["continuation"]["report"] in ("public", "sealed")
                else "monitoring_pending"
            )
        elif choice == "2":
            state["continuation"]["plan"] = "appeal"
            result = (
                "appeal_reopened"
                if state["continuation"]["appeal"] == "regulator"
                and state["continuation"]["audit"] == "certified"
                and state["evidence"] >= 3
                and state["trust_level"] >= 2
                else "appeal_pending"
            )
        else:
            state["continuation"]["plan"] = "settlement"
            result = (
                "supervised_settlement"
                if state["continuation"]["bank_check"] == "reconciled"
                and state["trust_level"] >= 2
                else "settlement_pending"
            )
        state.update(chapter=28, continuation_result=result)
        return points, state

    if state["chapter"] == 28:
        ending = ENDING_TEXT.get(state["ending"])
        if ending:
            ending_title, ending_details = ending
            ending_message = f"[bold bright_magenta]{ending_title}[/]\n\n{ending_details}"
        else:
            ending_message = f"[bold bright_magenta]ДОСЬЕ ЗАКРЫТО[/]\n{state['ending']}"
        continuation_result = CONTINUATION_RESULT_TEXT.get(
            state["continuation_result"],
            "",
        )
        if state["previous_ending"] and state["previous_ending"] != state["ending"]:
            previous_result = ENDING_TEXT.get(state["previous_ending"])
            previous_title = previous_result[0] if previous_result else state["previous_ending"]
            ending_message += f"\n\n[bold cyan]Прежний итог: {previous_title}[/]"
        if continuation_result:
            ending_message += f"\n\n[bold cyan]Продолжение: {continuation_result}[/]"
        console.print(Panel(
            f"{ending_message}\n\nДокументы: {state['evidence']}   "
            f"Доверие: {state['trust_level']}/4\n"
            "[cyan]Нажмите Enter для выхода[/]",
            border_style="bright_magenta",
            title="[bold]VIBE PLUS[/]",
        ))
        console.print("\n[cyan]1.[/] Начать заново")
        console.print("[red]2.[/] Выйти из DLC")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="2")
        if choice == "1":
            state = default_state()
            return points, state
        return points, state

    return points, state
