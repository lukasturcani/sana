import os

from nicegui import native, ui

from sana._internal.components.local_file_picker import LocalFilePicker


def main() -> None:
    """Run the app."""
    ui.run(
        port=native.find_open_port(),
        reload=os.environ.get("SANA_RELOAD", "FALSE") == "TRUE",
    )


async def pick_file() -> None:
    result = await LocalFilePicker("~")
    ui.notify(f"You chose {result}")


@ui.page("/")
def index() -> None:
    ui.button("Choose file", on_click=pick_file, icon="folder")


if __name__ in {"__main__", "__mp_main__"}:
    main()
