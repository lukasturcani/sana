import os
from collections.abc import Callable
from datetime import timedelta
from pathlib import Path

from nicegui import binding, native, ui

from sana._internal.analysis import plot_raw_data, plot_sliding_mean, read_file
from sana._internal.components.local_file_picker import LocalFilePicker


class Data:
    every = binding.BindableProperty()
    period = binding.BindableProperty()
    offset = binding.BindableProperty()

    def __init__(self, on_change: Callable[[], None]) -> None:
        self.on_change = on_change
        self._page: Path | None = None
        self.every = 1
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
        with ui.column().classes("w-full"):
            with ui.row():
                every = ui.slider(min=1, max=10, step=1).bind_value(
                    data, "every"
                )
                ui.label().bind_text_from(
                    every, "value", lambda v: f"Every: {v} s"
                )
            with ui.row():
                period = ui.slider(min=1, max=500, step=1).bind_value(
                    data, "period"
                )
                ui.label().bind_text_from(
                    period, "value", lambda v: f"Window Size: {v} s"
                )
            with ui.row():
                offset = ui.slider(min=0, max=50, step=1).bind_value(
                    data, "offset"
                )
                ui.label().bind_text_from(
                    offset, "value", lambda v: f"Offset: {v} s"
                )
        figure = plot_sliding_mean(
            spectrum,
            every=timedelta(seconds=every.value),
            period=timedelta(seconds=period.value),
            offset=timedelta(seconds=offset.value),
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
