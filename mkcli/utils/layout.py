from datetime import datetime
from typing import Callable
from rich.json import JSON

import pyperclip
import readchar
from rich.align import Align
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.text import Text

from mkcli.core.models.cluster import Cluster
from mkcli.core.models.node_pool import NodePool
from mkcli.utils.console import LiveResourceTable


class Clock:
    def __rich__(self) -> Text:
        return Text(datetime.now().ctime(), style="bold magenta", justify="center")


class ExtraInfo:
    def __init__(self, feed_func: Callable[[], Text]) -> None:
        self._data: Text | None = None
        self._feed_func = feed_func

    def refresh(self) -> None:
        self._data = self._feed_func()
        return self

    def __rich__(self) -> Text:
        return self.refresh()._data


class Dashboard:
    """This class is a proof of concept of Live Dashboards with keyboard interactivity
    DO NOT USE IN PRODUCTION YET - WORK IN PROGRESS
    In the future there should be threading implemented to refresh data in the background without blocking by readchar
    """

    def __init__(
        self,
        console: Console,
        func_clusters_sync: Callable[[], list[Cluster]],
        func_node_pools_sync: Callable[
            [str], list[NodePool]
        ],  # Fixed: takes cluster_id parameter
    ) -> None:
        self.console = console
        self.func_clusters_sync = func_clusters_sync
        self.func_node_pools_sync = func_node_pools_sync

        self.clock = Clock()
        self._layout = None

        self._setup_layout()
        self.sync_body()
        self.sync_footer(
            "Press 'q' to quit, ↑/k and ↓/j to navigate, Enter to copy cluster ID to clipboard. Press Ctrl+C to exit."
        )

    def _setup_layout(self) -> None:
        self._layout = Layout()

        self._layout.split(
            Layout(name="header", size=1),
            Layout(ratio=1, name="main"),
            Layout(size=2, name="footer"),
        )

        self._layout["main"].split_row(
            Layout(name="body_main", ratio=4), Layout(name="extra_right", ratio=2)
        )

        self._layout["body_main"].split(
            Layout(name="body", ratio=2), Layout(name="extra_down", ratio=1)
        )

        self._layout["header"].update(Clock())

        self._layout["body"].update(
            LiveResourceTable(
                columns=Cluster.table_columns,
                title="Cluster List",
                feed=self.func_clusters_sync(),
            )
        )

    def sync_body(self) -> None:
        self._layout["body"].update(
            LiveResourceTable(
                columns=Cluster.table_columns,
                title="Cluster List",
                feed=lambda: self.func_clusters_sync(),
            )
        )

    def sync_footer(self, msg: str) -> None:
        self._layout["footer"].update(
            Align.center(
                Text(msg, style="bold yellow"),
                vertical="middle",
            )
        )

    def sync_extra_right(self, cluster: Cluster) -> None:
        self._layout["extra_right"].update(JSON.from_data(cluster.model_dump()))

    def sync_extra_down(self, cluster_id: str) -> None:
        self._layout["extra_down"].update(
            LiveResourceTable(
                columns=NodePool.table_columns,
                title=f"Cluster {cluster_id} Node Pools",
                feed=lambda: self.func_node_pools_sync(cluster_id),
            )
        )

    def go_live(self) -> None:
        with Live(
            self._layout, screen=True, redirect_stderr=False, auto_refresh=False
        ) as live:
            try:
                while True:
                    selectable_layout = self._layout["body"]
                    max_height = len(selectable_layout.renderable._data)  # TODO fix
                    data = selectable_layout.renderable.refresh()._data
                    selected = selectable_layout.renderable._selected_index

                    ch = readchar.readkey()

                    if ch == "q" or ch == readchar.key.ESC:
                        live.stop()
                        break
                    if ch == readchar.key.UP or ch == "k":
                        selected = max(0, selected - 1)
                    if ch == readchar.key.DOWN or ch == "j":
                        selected = min(max_height - 1, selected + 1)

                    # Get the selected item AFTER navigation
                    selected_cluster_id = data[selected].id if data else 0
                    selected_item = data[selected] if data else None

                    if (
                        ch == readchar.key.ENTER and selected_item
                    ):  # COPY CLUSTER ID TO THE CLIPBOARD
                        selected_cluster_id = selected_item.id
                        pyperclip.copy(str(selected_cluster_id))
                        self._layout["footer"].update(
                            Text(
                                f"Clusters id copied to the clipboard - {selected_item.name}: {selected_cluster_id}",
                                style="bold yellow",
                            )
                        )

                    if selected_item:
                        self._layout["header"].update(Clock())
                        self.sync_extra_right(selected_item)
                        self.sync_extra_down(selected_item.id)

                        self._layout["body"].update(
                            self._layout["body"]
                            .renderable.select(selected)
                            .refresh()
                            .render()
                        )

                    live.refresh()
                    # time.sleep(1). # TODO: add threading and then sleep

            except KeyboardInterrupt:
                live.stop()
                self.console.clear()
