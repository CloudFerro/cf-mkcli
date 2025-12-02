"""

Demonstrates a dynamic Layout

"""

from datetime import datetime
import random
from typing import Callable

import pyperclip
import readchar

from rich.align import Align
from rich.console import Console
from rich.highlighter import RegexHighlighter
from rich.theme import Theme
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich.json import JSON

from mkcli.core.mk8s import MK8SClient
from mkcli.core.models.cluster import Cluster
from mkcli.core.models.node_pool import NodePool
from mkcli.utils.console import LiveResourceTable
from mkcli.core.session import get_auth_adapter, open_context_catalogue
# from readchar import key

# if ctrl-c, quit gracefully
# signal.signal(signal.SIGINT, lambda _, __: sys.exit(0))


class StatusHighlighter(RegexHighlighter):
    """Apply styles to status keywords."""

    base_style = "status."
    highlights = [
        r"(?P<running>\bRunning\b)",
        r"(?P<creating>\bCreating\b)",
        r"(?P<configuring>\bConfiguring\b)",
        r"(?P<deleting>\bDeleting\b)",
        r"(?P<error>\bError\b)",
    ]


theme = Theme(
    {
        "status.running": "bold green",
        "status.creating": "bold blue",
        "status.configuring": "bold yellow",
        "status.deleting": "bold red",
        "status.error": "bold red on white",
    }
)
console = Console(highlighter=StatusHighlighter(), theme=theme)

# console = Console()
layout = Layout()

layout.split(
    Layout(name="header", size=1),
    Layout(ratio=1, name="main"),
    Layout(size=2, name="footer"),
)

layout["main"].split_row(
    Layout(name="body_main", ratio=4), Layout(name="extra_right", ratio=2)
)
layout["body_main"].split(
    Layout(name="body", ratio=2), Layout(name="extra_down", ratio=1)
)
# layout["side"].split(Layout(), Layout())

layout["body_main"].update(
    Align.center(
        Text(
            f"{random.randint(1, 100)}",
            style="bold magenta",
            justify="center",
        ),
        vertical="middle",
    )
)


class Clock:
    """Renders the time in the center of the screen."""

    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")


class ExtraInfo:
    """Renders extra info in the body."""

    def __init__(self, feed_func: Callable[[], Text]) -> None:
        self._data: Text | None = None
        self._feed_func = feed_func

    def refresh(self) -> None:
        self._data = self._feed_func()
        return self

    def __rich__(self) -> Text:
        return self.refresh()._data


with open_context_catalogue() as cat:
    ctx = cat.current_context
    client = MK8SClient(get_auth_adapter(ctx), ctx.mk8s_api_url)

    layout["header"].update(Clock())

    layout["body"].update(
        LiveResourceTable(
            columns=Cluster.table_columns,
            title="Cluster List",
            feed=lambda: client.get_clusters(),
        )
    )

    layout["footer"].update(
        Align.center(
            Text("Press Ctrl+C to exit", style="bold yellow"),
            vertical="middle",
        )
    )

    with Live(layout, screen=True, redirect_stderr=False, auto_refresh=False) as live:
        try:
            while True:
                selectable_layout = layout["body"]
                max_height = len(selectable_layout.renderable._data)  # TODO fix
                data = selectable_layout.renderable.refresh()._data
                selected = selectable_layout.renderable._selected_index
                selected_cluster_id = data[selected].id if data else 0

                ch = readchar.readkey()

                if ch == "q" or ch == readchar.key.ESC:
                    live.stop()
                    break
                if ch == readchar.key.UP or ch == "k":
                    selected = max(0, selected - 1)
                if ch == readchar.key.DOWN or ch == "j":
                    selected = min(max_height - 1, selected + 1)
                if ch == readchar.key.ENTER:  # COPY CLUSTER ID TO THE CLIPBOARD
                    selected_cluster_id = selected_item.id
                    pyperclip.copy(str(selected_cluster_id))
                    layout["footer"].update(
                        Text(
                            f"Clusters id copied to the clipboard - {selected_item.name}: {selected_cluster_id}",
                            style="bold yellow",
                        )
                    )

                selected_item = data[selected]

                layout["header"].update(Clock())
                layout["extra_right"].update(JSON.from_data(selected_item.model_dump()))
                layout["extra_down"].update(
                    LiveResourceTable(
                        columns=NodePool.table_columns,
                        title=f"Cluster {selected_cluster_id} Node Pools",
                        feed=lambda: client.list_node_pools(selected_cluster_id),
                    )
                )

                layout["body"].update(
                    layout["body"].renderable.select(selected).refresh().render()
                )

                live.refresh()
                # time.sleep(1)

        except KeyboardInterrupt:
            live.stop()
            console.clear()
