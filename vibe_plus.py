from copy import deepcopy

from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text


CHAPTERS = (
    "Приглашение",
    "Первое знакомство",
    "Проверка договора",
    "Экзамен по мелкому шрифту",
    "Совет директоров",
    "Подготовка документов",
    "Сбор доказательств",
    "День открытых дверей",
    "Финальное заседание",
    "Ночь списаний",
    "Последняя подпись",
    "Досье закрыто",
)

ENDINGS = {
    "blind_sign": ("Вас подключили навсегда.", "Вы согласились на всё. Даже на письма с темой «последнее предупреждение» каждое утро."),
    "honest_sign": ("Подписано с чистой совестью.", "Договор подписан. Теперь у вас есть подписка, у договора — подпись, у юриста — выходной."),
    "blame_sign": ("Сосед признан виновным.", "Вы свалили всё на соседа. Он не знает, что произошло, зато теперь получает ваши счета."),
    "exam_sign": ("Экзамен сдан. Подписка тоже.", "Вы изучили каждый пункт и всё равно подписали. Юрист уважительно пожал вам руку."),
    "full_text_sign": ("Вы прочитали всё. Почти.", "Договор оказался длиннее, чем обещали. Последнюю страницу допечатали, пока вы читали первую."),
    "refused": ("Отказ принят. Уведомления — нет.", "Подписку отменили. Рекламные письма остались, потому что у них отдельная подписка."),
    "court": ("Суд встал на сторону подписчиков.", "Договор отменён. Юрист попросил не цитировать решение мелким шрифтом."),
    "bank": ("Банк отменил списание.", "Подписка подала апелляцию на здравый смысл. Банк её не принял."),
}

ROUTES = {"standard", "premium", "exam", "exam_passed", "full_text", "blind_sign", "press", "consultant", "tolya", "honest", "blame"}
ENDING_IDS = set(ENDINGS)


def default_state():
    return {
        "version": 3,
        "chapter": 0,
        "route": "",
        "ending": "",
        "exam_progress": 0,
        "side_quest": None,
        "bank_case": False,
        "evidence": 0,
        "ending_reward": 0,
    }


def normalize_state(value):
    if not isinstance(value, dict):
        return default_state()

    source_version = value.get("version", 2)
    chapter = value.get("chapter", 0)
    if not isinstance(chapter, int) or isinstance(chapter, bool) or chapter not in range(len(CHAPTERS)):
        chapter = 0

    route = value.get("route", "")
    ending = value.get("ending", "")
    exam_progress = value.get("exam_progress", 0)
    side_quest = value.get("side_quest")
    bank_case = value.get("bank_case", False)
    evidence = value.get("evidence", 0)
    ending_reward = value.get("ending_reward", 0)

    if not isinstance(route, str) or route not in ROUTES:
        route = ""
    if not isinstance(ending, str) or ending not in ENDING_IDS:
        ending = ""
    if not isinstance(exam_progress, int) or isinstance(exam_progress, bool) or exam_progress not in range(4):
        exam_progress = 0
    if side_quest not in (None, "archive_case_done"):
        side_quest = None
    if not isinstance(bank_case, bool):
        bank_case = False
    if not isinstance(evidence, int) or isinstance(evidence, bool) or evidence < 0:
        evidence = 0
    if not isinstance(ending_reward, int) or isinstance(ending_reward, bool) or ending_reward < 0:
        ending_reward = 0

    state = {
        "version": 3,
        "chapter": chapter,
        "route": route,
        "ending": ending,
        "exam_progress": exam_progress,
        "side_quest": side_quest,
        "bank_case": bank_case,
        "evidence": evidence,
        "ending_reward": ending_reward,
    }

    if source_version != 3:
        if chapter <= 6:
            state["chapter"] = chapter
        elif chapter == 7:
            state["chapter"] = 8
        elif chapter == 8:
            state["chapter"] = 9 if route == "blind_sign" else 10
        elif chapter >= 9:
            state["chapter"] = 11
            state["ending"] = ending if ending in ENDING_IDS else "refused"
    return state


def _show_dossier(console, state, day, points):
    progress = Table.grid(padding=(0, 1))
    progress.add_column(style="bold cyan", width=3)
    progress.add_column()
    for index, title in enumerate(CHAPTERS):
        marker = "[green]●[/]" if index < state["chapter"] else (
            "[bright_magenta]◉[/]" if index == state["chapter"] else "[dim]○[/]"
        )
        progress.add_row(marker, title)

    chapter = state["chapter"]
    status = "Заблокировано до 3-го дня" if chapter == 0 and day < 3 else (
        f"Досье закрыто: {ENDINGS[state['ending']][0]}"
        if chapter == 11 and state["ending"] in ENDINGS
        else f"Глава {chapter + 1} из {len(CHAPTERS)}"
    )
    header = Text()
    header.append("V I B E   P L U S\n", style="bold bright_magenta")
    header.append("РАСШИРЕННОЕ ИЗДАНИЕ • «УСЛОВИЯ ПРИМЕНЕНИЯ»\n\n", style="dim")
    header.append(f"{status}\n", style="white")
    header.append(f"Баланс: {points} очков", style="green")
    header.append(f"   День: {day}", style="cyan")
    header.append(f"\nУлики: {state['evidence']}", style="yellow")
    console.print(Panel(
        header,
        border_style="bright_magenta",
        title="[bold white]ВНЕШНИЙ МОДУЛЬ[/]",
        subtitle="[dim]Любое сходство с подписками случайно и списывается ежемесячно[/]",
        padding=(1, 2),
    ))
    console.print(Panel(progress, border_style="cyan", title="Досье: 11 игровых глав"))


def _finish(state, ending, reward):
    state.update(chapter=11, ending=ending, ending_reward=reward)


def run(console, points, day, saved_state):
    state = normalize_state(deepcopy(saved_state))
    _show_dossier(console, state, day, points)
    chapter = state["chapter"]

    if chapter == 0:
        if day < 3:
            console.print(Panel(
                "В почтовом ящике пока только квитанция за электричество.\n"
                "Даже корпорация решила не портить вам первые три дня.",
                border_style="yellow",
            ))
            return points, state
        console.print(Panel(
            "На экране письмо от «Vibe Plus»: «Поздравляем! Вы почти подписаны». "
            "Вы ничего не нажимали, но юридически это не мешает им.",
            border_style="bright_magenta",
        ))
        console.print("[cyan]1.[/] Прочитать письмо бесплатно")
        console.print("[cyan]2.[/] Купить приоритетную проверку (-80 очков)")
        console.print("[cyan]3.[/] Закрыть письмо и жить в неведении")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state.update(chapter=1, route="standard")
        elif choice == "2":
            if points < 80:
                console.print("[red]Не хватает 80 очков. Даже мошенникам нужна ликвидность.[/]")
                return points, state
            points -= 80
            state.update(chapter=1, route="premium")
        else:
            console.print("[dim]Письмо закрыто. Оно открылось само. Конечно же.[/]")
        return points, state

    if chapter == 1:
        console.print(Panel(
            "Vibe Plus приветствует вас в мировом сообществе.\n"
            "Для доступа нужно пройти небольшое собеседование.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Продолжить собеседование")
        console.print("[cyan]2.[/] Прервать и уйти")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        if choice == "1":
            state["chapter"] = 2
        else:
            console.print("[dim]Вы ушли. Но они всё равно найдут вас.[/]")
        return points, state

    if chapter == 2:
        console.print(Panel(
            "Юрист называет тариф «Бессрочный пробный период»: первые 14 лет "
            "бесплатно, дальше — по настроению бухгалтерии.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Подписаться без проверки")
        console.print("[cyan]2.[/] Пройти экзамен по договору")
        console.print("[cyan]3.[/] Потребовать полный текст договора")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="2")
        if choice == "1":
            state.update(chapter=9, route="blind_sign")
        elif choice == "2":
            state.update(chapter=3, route="exam", exam_progress=0)
        else:
            state.update(chapter=4, route="full_text")
        return points, state

    if chapter == 3:
        questions = (
            (
                "Что такое автопродление?",
                ("Autistic production", "Автоматическое продление подписки", "Вид маркетинга"),
                1,
            ),
            (
                "Можно ли отменить автопродление?",
                ("Да, в личном кабинете", "Нет, это навсегда", "Только по телефону поддержки"),
                0,
            ),
            (
                "Что будет, если не отменить?",
                ("С вас спишут деньги", "Вас заблокируют", "Ничего не будет"),
                0,
            ),
        )
        index = state["exam_progress"]
        question, answers, correct = questions[index]
        console.print(Panel(f"Вопрос {index + 1} из 3: {question}", border_style="yellow"))
        for answer_index, answer in enumerate(answers, 1):
            console.print(f"[cyan]{answer_index}.[/] {answer}")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default=str(correct + 1))
        if int(choice) - 1 == correct:
            points += 50 if index < 2 else 100
            state["exam_progress"] += 1
            console.print("[green]Верно. Юрист отвёл взгляд.[/]")
            if state["exam_progress"] == 3:
                state.update(chapter=4, route="exam_passed")
                console.print("[bold green]Экзамен сдан![/]")
        elif index == 2:
            points -= 20
            state["exam_progress"] = 0
            console.print("[red]Неверно. Экзамен начинается заново. Деньги тоже.[/]")
        else:
            points -= 20
            state["exam_progress"] += 1
            console.print("[red]Неверно. Минус 20 очков; корпорация считает это обучением.[/]")
        return points, state

    if chapter == 4:
        console.print(Panel(
            "Совет директоров собрался в переговорной. На столе вода, "
            "договор на 47 страниц и единственный стул для вас.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Передать договор независимой газете")
        console.print("[cyan]2.[/] Устроиться консультантом и искать кнопку отмены")
        console.print("[cyan]3.[/] Позвонить Толе: пусть оценит шрифт мелкого текста")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        state.update(chapter=5, route={"1": "press", "2": "consultant", "3": "tolya"}[choice])
        return points, state

    if chapter == 5:
        console.print(Panel(
            "Для слушаний нужны документы. Архив выдал талончик и сообщил, "
            "что ваш талончик уже рассмотрен.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Собрать бумаги самостоятельно")
        console.print("[cyan]2.[/] Попросить сотрудников поднять свои договоры (+50 очков)")
        console.print("[cyan]3.[/] Купить готовую папку у консультанта")
        if state["side_quest"] is None:
            console.print("[cyan]4.[/] Проверить папку «обращения, которые не открывать» (+40 очков)")
            choices = ["1", "2", "3", "4"]
        else:
            choices = ["1", "2", "3"]
        choice = Prompt.ask("Выбор", choices=choices, default="1")
        if choice == "4":
            state["side_quest"] = "archive_case_done"
            state["evidence"] += 1
            points += 40
            console.print(Panel(
                "В папке обнаружено ваше обращение. Оно было закрыто ещё до отправки.",
                border_style="green",
                title="Побочное дело закрыто",
            ))
            return points, state
        if choice == "2":
            points += 50
            state["evidence"] += 1
        elif choice == "3":
            state["evidence"] += 1
        state["chapter"] = 6
        return points, state

    if chapter == 6:
        console.print(Panel(
            "Сбор доказательств. Время истекает, а архивный принтер печатает "
            "прошлогодний календарь.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Подождать ещё недельку (+2 улики)")
        console.print("[cyan]2.[/] Собрать всё, что есть, и идти дальше")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="2")
        if choice == "1":
            state["evidence"] += 2
            console.print("[yellow]Прошла неделя. Календарь всё ещё прошлогодний.[/]")
        else:
            state["evidence"] += 1
        state["chapter"] = 7
        return points, state

    if chapter == 7:
        console.print(Panel(
            "День открытых дверей. Дверь открыта, потому что замок "
            "входит только в премиум-подписку.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Показать посетителям настоящий договор (+2 улики)")
        console.print("[cyan]2.[/] Собрать показания сотрудников (+2 доверия и 30 очков)")
        console.print("[cyan]3.[/] Провести экскурсию в отдел отмены подписок")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state["evidence"] += 2
        elif choice == "2":
            points += 30
            state["evidence"] += 1
        else:
            state["evidence"] += 1
        state["chapter"] = 8
        return points, state

    if chapter == 8:
        console.print(Panel(
            f"Финальное заседание. На руках {state['evidence']} улик. "
            "Председатель предлагает сначала обсудить возможность обсуждения.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Представить документы открыто")
        console.print("[cyan]2.[/] Переложить вину на соседа")
        choice = Prompt.ask("Выбор", choices=["1", "2"], default="1")
        state.update(chapter=9, route="honest" if choice == "1" else "blame")
        return points, state

    if chapter == 9:
        console.print(Panel(
            "В 03:14 банк сообщает о новом списании. Поддержка ответит с 09:00 "
            "и по предварительной записи.",
            border_style="red",
            title="Ночь списаний",
        ))
        console.print("[cyan]1.[/] Сохранить выписку и оспорить списание")
        console.print("[cyan]2.[/] Передать выписку журналистам (+1 улика)")
        console.print("[cyan]3.[/] Заблокировать автоплатёж через банк")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state["bank_case"] = True
            state["evidence"] += 1
            console.print("[green]Обращение принято. Срок ответа — 4–6 бизнес-апокалипсисов.[/]")
        elif choice == "2":
            state["evidence"] += 1
            console.print("[green]Журналистка приняла выписку. У неё уже была такая же.[/]")
        else:
            state["bank_case"] = True
            console.print("[green]Автоплатёж заблокирован. Кнопка случайной разблокировки уже рядом.[/]")
        state["chapter"] = 10
        return points, state

    if chapter == 10:
        console.print(Panel(
            "Последняя страница договора. На ней крупно написано «РЕШЕНИЕ ЗА ВАМИ», "
            "мелко — всё остальное.",
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Подписать договор (+200 очков)")
        console.print("[cyan]2.[/] Отказаться (+50 очков)")
        console.print("[cyan]3.[/] Передать дело в суд по защите потребителей (+50 очков)")
        console.print("[cyan]4.[/] Добиться отмены через банк (+50 очков)")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3", "4"], default="1")
        if choice == "1":
            endings = {
                "blind_sign": "blind_sign",
                "honest": "honest_sign",
                "blame": "blame_sign",
                "exam_passed": "exam_sign",
                "full_text": "full_text_sign",
            }
            ending = endings.get(state["route"], "honest_sign")
            reward = 200
        elif choice == "2":
            ending, reward = "refused", 50
        elif choice == "3":
            ending, reward = "court", 50
        else:
            ending, reward = "bank", 50
        _finish(state, ending, reward)
        points += reward
        console.print(Panel(
            f"[bold green]{ENDINGS[ending][0]}[/]\n[cyan]+{reward} очков[/]",
            border_style="green",
            title="Решение принято",
        ))
        return points, state

    if chapter == 11:
        ending = state["ending"] if state["ending"] in ENDINGS else "refused"
        console.print(Panel(
            f"[bold bright_magenta]{ENDINGS[ending][0]}[/]\n\n{ENDINGS[ending][1]}\n\n"
            f"Улики: {state['evidence']}   Экзамен: {state['exam_progress']}/3\n"
            f"Побочное дело: {'закрыто' if state['side_quest'] else 'не открыто'}\n"
            f"[cyan]Награда: {state['ending_reward']} очков[/]",
            border_style="bright_magenta",
            title="ФИНАЛ • VIBE PLUS",
        ))
        console.print("[cyan]1.[/] Начать Vibe Plus заново")
        console.print("[red]2.[/] Выйти")
        if Prompt.ask("Выбор", choices=["1", "2"], default="2") == "1":
            state = default_state()
        return points, state

    return points, state
