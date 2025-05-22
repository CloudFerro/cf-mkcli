from typing import (
    ContextManager,
    Optional,
)

from rich import (
    box,
    print,
)
from rich.console import Console
from rich.table import Table


def ok() -> None:
    print("Done! :+1:")


def exc(msg: Optional[str] = None) -> None:
    print(":heavy_exclamation_mark:")
    if msg is not None:
        print(msg)


def display_table(columns: list[str], rows: set[str], title: str):
    console = Console()
    table = Table(title=title, box=box.ASCII2)
    for col in columns:
        table.add_column(col)
    for row in rows:
        row = map(str, row)
        table.add_row(*row)
    console.print(table)


def display(_str: str) -> None:
    print(_str)


def status_frame(_str: str) -> ContextManager:
    return Console().status(_str)
