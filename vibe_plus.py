from copy import deepcopy

from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text


ENDINGS = {
    ("press", "1"): "Договор опубликован. Юрист подписался на рассылку.",
    ("press", "2"): "Личные данные скрыты. Мелкий шрифт — нет.",
    ("consultant", "1"): "Кнопка найдена. Она была на первой странице.",
    ("consultant", "2"): "Вы ушли с компенсацией и корпоративной кружкой.",
    ("tolya", "1"): "Толя проверил договор. Теперь подписка боится Толю.",
    ("tolya", "2"): "Письмо разослано. Кто-то нажал. Не вы.",
}


def default_state():
    return {"chapter": 0, "route": "", "ending": ""}


def normalize_state(value):
    if not isinstance(value, dict):
        return default_state()

    chapter = value.get("chapter", 0)
    if not isinstance(chapter, int) or chapter not in range(4):
        chapter = 0

    route = value.get("route", "")
    ending = value.get("ending", "")
    if not isinstance(route, str) or route not in {"", "auditor", "insider", "press", "consultant", "tolya"}:
        route = ""
    if not isinstance(ending, str) or ending not in set(ENDINGS.values()):
        ending = ""

    return {"chapter": chapter, "route": route, "ending": ending}


def _show_dossier(console, state, day, points):
    chapter = state["chapter"]
    progress = Table.grid(padding=(0, 2))
    progress.add_column(style="bold cyan")
    progress.add_column()
    for index, title in enumerate(("Приглашение", "Проверка договора", "Совет директоров")):
        marker = "[green]●[/]" if index < chapter else "[cyan]◉[/]" if index == chapter else "[dim]○[/]"
        progress.add_row(marker, title)

    if chapter == 0:
        status = "Заблокировано до 3-го дня" if day < 3 else "Входящее письмо ждёт ответа"
    elif chapter == 1:
        status = "Договор вскрыт. Выбор ещё можно испортить."
    elif chapter == 2:
        status = "Заседание назначено. Галстук не обязателен."
    else:
        status = f"Досье закрыто: {state['ending']}"

    header = Text()
    header.append("V I B E   P L U S\n", style="bold bright_magenta")
    header.append("РАСШИРЕНИЕ • «УСЛОВИЯ ПРИМЕНЕНИЯ» • ВЕРСИЯ 1.0\n\n", style="dim")
    header.append(f"{status}\n", style="white")
    header.append(f"Баланс: {points} очков", style="green")
    header.append(f"   День: {day}", style="cyan")
    console.print(Panel(
        header,
        border_style="bright_magenta",
        title="[bold white]ВНЕШНИЙ МОДУЛЬ[/]",
        subtitle="[dim]Любое сходство с подписками случайно и списывается ежемесячно[/]",
        padding=(1, 2),
    ))
    console.print(Panel(progress, border_style="cyan", title="Досье: 03 дела"))


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
        console.print("[cyan]1.[/] Прочитать договор (бесплатно)")
        console.print("[cyan]2.[/] Купить приоритетную проверку (80 очков)")
        console.print("[cyan]3.[/] Закрыть письмо и жить в неведении")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        if choice == "1":
            state.update(chapter=1, route="auditor")
        elif choice == "2":
            if points < 80:
                console.print("[red]Не хватает 80 очков. Даже мошенникам нужна ликвидность.[/]")
                return points, state
            points -= 80
            state.update(chapter=1, route="insider")
        else:
            console.print("[dim]Письмо закрыто. Оно откроется само. Конечно же.[/]")
        return points, state

    if state["chapter"] == 1:
        introduction = (
            "Независимый аудитор нашёл тариф «Бессрочный пробный период»: "
            "первые 14 лет бесплатно, дальше — по настроению бухгалтерии."
            if state["route"] == "auditor"
            else "За 80 очков вам открыли внутренний договор. В нём есть пункт "
            "«отмена подписки»: он напечатан белым по белому."
        )
        console.print(Panel(
            introduction,
            border_style="yellow",
        ))
        console.print("[cyan]1.[/] Передать договор независимой газете")
        console.print("[cyan]2.[/] Устроиться консультантом и узнать, где кнопка «отмена»")
        console.print("[cyan]3.[/] Позвонить Толе: пусть оценит шрифт мелкого текста")
        choice = Prompt.ask("Выбор", choices=["1", "2", "3"], default="1")
        routes = {"1": "press", "2": "consultant", "3": "tolya"}
        state.update(chapter=2, route=routes[choice])
        return points, state

    if state["chapter"] == 2:
        console.print(Panel(
            "Совет директоров собрался в переговорной. На столе вода, "
            "договор на 47 страниц и единственный стул для вас.",
            border_style="yellow",
        ))
        if state["route"] == "press":
            console.print("[cyan]1.[/] Опубликовать договор целиком (+240 очков)")
            console.print("[cyan]2.[/] Удалить личные данные и опубликовать выдержки (+160 очков)")
        elif state["route"] == "consultant":
            console.print("[cyan]1.[/] Показать совету кнопку отмены (+240 очков)")
            console.print("[cyan]2.[/] Взять выходное пособие и уйти красиво (+160 очков)")
        elif state["route"] == "tolya":
            console.print("[cyan]1.[/] Передать копию Толе (+240 очков)")
            console.print("[cyan]2.[/] Отправить всем письмо «не нажимайте сюда» (+160 очков)")
        else:
            console.print("[cyan]1.[/] Выступить с разоблачением (+240 очков)")
            console.print("[cyan]2.[/] Потребовать тихую компенсацию (+160 очков)")
        choice = Prompt.ask("Финальный выбор", choices=["1", "2"], default="1")
        points += 240 if choice == "1" else 160
        state.update(chapter=3, ending=ENDINGS.get((state["route"], choice), "Подписка отменена. Деньги начислены."))
        result = Text()
        result.append("ДЕЛО ЗАКРЫТО\n", style="bold green")
        result.append(f"{state['ending']}\n")
        result.append(f"+{240 if choice == '1' else 160} очков", style="cyan")
        console.print(Panel(
            result,
            border_style="green",
            title="[bold]VIBE PLUS[/]",
        ))
        return points, state

    console.print(Panel(
        Text.assemble(
            ("КОНТЕНТ ПРОЙДЕН\n", "bold green"),
            (f"{state['ending']}\n"),
            ("Новая функция: вы теперь узнаёте слово «автопродление» с первого взгляда.", "dim"),
        ),
        border_style="green",
    ))
    return points, state
