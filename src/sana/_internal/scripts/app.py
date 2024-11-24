import os
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

from nicegui import binding, native, ui

from sana._internal.analysis import (
    plot_cum_sum,
    plot_raw_data,
    plot_sliding_mean,
    read_file,
)
from sana._internal.components.local_file_picker import LocalFilePicker


class Data:
    every = binding.BindableProperty()
    period = binding.BindableProperty()
    offset = binding.BindableProperty()

    def __init__(self, on_change: Callable[[], None]) -> None:
        self.on_change = on_change
        self._page: Path | None = None
        self.every = 50
        self.period = 120
        self.offset = 0

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
        with ui.row():
            ui.label("Every:")
            ui.number(value=data.every).bind_value(data, "every").on(
                "keydown.enter", analysis_ui.refresh
            )
        with ui.row():
            ui.label("Window Size:")
            ui.number(value=data.period).bind_value(data, "period").on(
                "keydown.enter", analysis_ui.refresh
            )
        with ui.row():
            ui.label("Offset:")
            ui.number(value=data.offset).bind_value(data, "offset").on(
                "keydown.enter", analysis_ui.refresh
            )
        ui.button("confirm", on_click=analysis_ui.refresh)
        figure = plot_sliding_mean(
            spectrum,
            every=timedelta(seconds=data.every),
            period=timedelta(seconds=data.period),
            offset=timedelta(seconds=data.offset),
        )
        ui.plotly(figure)

    with ui.card():
        ui.label("CumSum")
        figure = plot_cum_sum(spectrum)
        ui.plotly(figure)


data = Data(on_change=analysis_ui.refresh)


async def pick_file() -> None:
    result = await LocalFilePicker("~")
    data.page = Path(result[0])


@ui.page("/")
def index() -> None:
    ui.page_title("Sana")
    ui.button("Choose file", on_click=pick_file, icon="folder")
    analysis_ui()


if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        port=native.find_open_port(),
        reload=os.environ.get("SANA_RELOAD", "FALSE") == "TRUE",
    )
