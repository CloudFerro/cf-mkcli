import time
from typing import (
    Callable,
    Optional,
    Any,
)

from mkcli.core.models.backup import BaseResourceModel
import rich.rule
from rich import box, print, print_json
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.style import Style
from rich.highlighter import RegexHighlighter
from rich.theme import Theme

HIGHLIGHTED: str = "italic bright_green"
INACTIVE: str = "dim"
LIVE_CONSOLE: Console = Console()


class StatusHighlighter(RegexHighlighter):
    """Apply styles to status keywords."""

    base_style = "status."
    highlights = [
        r"(?P<running>\bRunning\b)",
        r"(?P<creating>\bCreating\b)",
        r"(?P<configuring>\bConfiguring\b)",
        r"(?P<upgrading>\bUpgrading\b)",
        r"(?P<deleting>\bDeleting\b)",
        r"(?P<error>\bError\b)",
    ]


theme = Theme(
    {
        "status.running": "bold green",
        "status.creating": "bold yellow",
        "status.configuring": "bold yellow",
        "status.upgrading": "bold cyan",
        "status.deleting": Style(color="black", dim=True, bold=True),
        "status.error": "bold red",
    }
)


def get_console() -> Console:
    return Console(highlighter=StatusHighlighter(), theme=theme)


class ResourceTable:
    def __init__(self, columns: list[str], title: str) -> None:
        self.console = Console(highlighter=StatusHighlighter(), theme=theme)
        self.table = Table(title=title, box=box.HEAVY_HEAD, highlight=True)
        for col in columns:
            self.table.add_column(col)

    def add_row(self, values: list[Any], style=None) -> None:
        """
        Add a row to the table.
        """
        values = map(str, values)  # type: ignore
        self.table.add_row(*values, style=style)

    def display(self) -> None:
        self.console.print(self.table)


class LiveResourceTable:
    SELECTED = Style(color="black", bgcolor="yellow", bold=True)

    def __init__(
        self,
        columns: list[str],
        title: str,
        feed: Callable[[], list[BaseResourceModel]],
        selection_frame_size: int = 10,
    ) -> None:
        """LiveResourceTable is a table that updates in real-time with data got from feed function call.

        Args:
            columns (list[str]): The columns to display in the table.
            title (str): The title of the table.
            feed (Callable[[], list[BaseResourceModel]]): A function that returns the current data for the table.
        """
        self.console = Console(highlighter=StatusHighlighter(), theme=theme)
        self.columns = columns
        self.feed = feed
        self.title = title

        self.style = None
        self.selection_frame_size = selection_frame_size

        self._table: Table | None = None
        self._data: list[BaseResourceModel] = []
        self._selected_index: int = 0
        self._init_table()

    def _init_table(self) -> None:
        """Initialize the table with data from the feed."""
        self._table = Table(title=self.title, box=box.HEAVY_HEAD, highlight=True)
        for col in self.columns:
            self._table.add_column(col)

    def select(self, index: int) -> "LiveResourceTable":
        """Select a row in the table by index."""
        size = self.selection_frame_size
        rows = self._table.rows

        if len(rows) + 3 > size:
            if index < size / 2:
                rows = rows[:size]
            elif index + size / 2 > len(rows):
                rows = rows[-size:]
                index -= len(rows) - size
            else:
                rows = rows[index - size // 2 : index + size // 2]
                index -= index - size // 2
        self._selected_index = index
        return self

    def render(self) -> "LiveResourceTable":
        for i, obj in enumerate(self._data):
            row = map(str, obj.as_table_row())
            self._table.add_row(
                *row, style=self.SELECTED if i == self._selected_index else self.style
            )
        return self

    def refresh(self) -> "LiveResourceTable":
        """Refresh the table data from the feed."""
        self._init_table()
        self._data = self.feed()
        return self

    def __rich__(self) -> Table:
        return self.refresh().render()._table


def ok() -> None:
    print("Done! :+1:")


def exc(msg: Optional[str] = None) -> None:
    print(":heavy_exclamation_mark:")
    if msg is not None:
        print(msg)


def make_table_gen(
    table: Table, cols: list[str], feed_data: Callable[Any, list[BaseResourceModel]]
):
    def generate_table() -> Table:
        """Make a new table."""
        for col in cols:
            table.add_column(col)

        data: list[BaseResourceModel] = feed_data()
        for index, obj in enumerate(data):
            row = obj.as_table_row()
            table.add_row(
                *map(str, row), style=HIGHLIGHTED if index % 2 == 0 else INACTIVE
            )
        return table

    return generate_table


def display_live(gen_table: Callable) -> None:
    with Live(gen_table(), refresh_per_second=1, console=LIVE_CONSOLE) as live:
        try:
            while True:
                live.update(gen_table())
                time.sleep(1)  # Wait 1 second between updates
        except KeyboardInterrupt:
            pass  # Exit gracefully when user presses Ctrl+C


def display_table(columns: list[str], rows: list[list[Any]], title: str):
    console = Console()
    table = Table(title=title, box=box.HEAVY_HEAD)
    for col in columns:
        table.add_column(col)
    for row in rows:
        row = map(str, row)
        table.add_row(*row)
    console.print(table)


def display(_str: Any) -> None:
    print(_str)


def display_json(_data: str) -> None:
    """
    Print the given data as JSON.
    """
    print_json(_data, indent=2, ensure_ascii=False, highlight=True)


def draw_rule(title: str | None = None) -> None:
    """
    Draw a horizontal rule.
    """
    if title is None:
        title = ""

    print(
        rich.rule.Rule(
            title=title,
            style="bold blue",
        )
    )
