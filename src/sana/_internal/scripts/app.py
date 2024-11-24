import os
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

from nicegui import native, ui

from sana._internal.analysis import plot_raw_data, plot_sliding_mean, read_file
from sana._internal.components.local_file_picker import LocalFilePicker


class Data:
    def __init__(self, on_change: Callable[[], None]) -> None:
        self.on_change = on_change
        self._page: Path | None = None

    @property
    def page(self) -> Path | None:
        return self._page

    @page.setter
    def page(self, value: Path | None) -> None:
        self._page = value
        self.on_change()


@ui.refreshable
def analysis_ui() -> None:
    if data.page is None:
        return

    spectrum = read_file(data.page)

    with ui.card():
        ui.label(f"Viewing {data.page}")

    with ui.card():
        ui.label("Raw Data")
        figure = plot_raw_data(spectrum)
        ui.plotly(figure)

    with ui.card():
        ui.label("Sliding Mean")
        figure = plot_sliding_mean(
            spectrum,
            every=timedelta(seconds=1),
            period=timedelta(seconds=120),
            offset=timedelta(seconds=0),
        )
        ui.plotly(figure)


data = Data(on_change=analysis_ui.refresh)


async def pick_file() -> None:
    result = await LocalFilePicker("~")
    data.page = Path(result[0])


@ui.page("/")
def index() -> None:
    ui.button("Choose file", on_click=pick_file, icon="folder")
    analysis_ui()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        port=native.find_open_port(),
        reload=os.environ.get("SANA_RELOAD", "FALSE") == "TRUE",
    )
