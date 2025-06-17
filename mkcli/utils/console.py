from typing import (
    Optional,
    Any,
)

import rich.rule
from rich import box, print, print_json
from rich.console import Console
from rich.table import Table


SHOW_INACTIVE_RESOURCES = False


class ResourceTable:
    def __init__(self, columns: list[str], title: str) -> None:
        self.console = Console()
        self.table = Table(title=title, box=box.HEAVY_HEAD)
        for col in columns:
            self.table.add_column(col)

    def add_row(self, values: list[Any], style=None) -> None:
        """
        Add a row to the table.
        """
        values = map(str, values)
        self.table.add_row(*values, style=style)

    def display(self) -> None:
        self.console.print(self.table)


def ok() -> None:
    print("Done! :+1:")


def exc(msg: Optional[str] = None) -> None:
    print(":heavy_exclamation_mark:")
    if msg is not None:
        print(msg)


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


def draw_rule(title: str = None) -> None:
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
