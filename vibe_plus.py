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
    "Досье закрыто",
)

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
}


def default_state():
    return {
        "version": 3,
        "chapter": 0,
        "route": "",
        "origin_route": "",
        "approach": "",
        "ending": "",
        "exam_progress": 0,
        "side_quest": None,
        "trust_level": 0,
        "evidence": 0,
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

    if source_version == 1 and chapter == 11:
        chapter = 13
    if source_version == 2 and chapter == 14:
        chapter = 16
    if source_version == 2 and chapter == 15:
        chapter = 17
    if source_version < 3 and chapter == 15:
        chapter = 17
    if source_version < 3 and source_chapter == 11 and not ending and ending_was_valid:
        ending = "Вы закрыли досье. Уведомления пока думают, что это не окончательно."
    if source_version < 3 and source_chapter == 15 and not ending and ending_was_valid:
        ending = "Вы закрыли досье. Уведомления пока думают, что это не окончательно."

    return {
        "version": 3,
        "chapter": chapter,
        "route": route,
        "origin_route": origin_route,
        "approach": approach,
        "ending": ending,
        "exam_progress": exam_progress,
        "side_quest": side_quest,
        "trust_level": trust_level,
        "evidence": evidence,
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
        status = "Побочное дело" + (" — выполнено" if state["side_quest"] == "completed" else "")
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
        status = "Повторное заседание"
    elif chapter == 15:
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
    console.print(Panel(progress, border_style="cyan", title="Досье: 18 игровых глав"))


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
            "Побочное дело: нужно найти дополнительные доказательства.\n"
            "Это не обязательно для основного прохождения, но даёт бонусы.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Выполнить побочное дело (+100 очков)")
        console.print("[cyan]2.[/] Пропустить побочное дело")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            points += 100
            state.update(chapter=8, side_quest="completed", trust_level=min(state["trust_level"] + 1, 4))
            console.print("[green]Побочное дело выполнено! +100 очков[/]")
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
            if state["side_quest"] == "completed":
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
        console.print(Panel(
            evidence_scenes.get(state["route"], "Архив ждёт документы."),
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
            state["evidence"] += 2 if state["side_quest"] == "completed" else 1
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
        console.print(Panel(
            preparation_scenes.get(state["route"], "Подготовка к публичному слушанию. "
            "Все взгляды обращены на вас."),
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
            state["evidence"] += 2 if state["side_quest"] == "completed" else 1
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
        ending = ENDING_TEXT.get(state["ending"])
        if ending:
            ending_title, ending_details = ending
            ending_message = f"[bold bright_magenta]{ending_title}[/]\n\n{ending_details}"
        else:
            ending_message = f"[bold bright_magenta]ДОСЬЕ ЗАКРЫТО[/]\n{state['ending']}"
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
