import os

from nicegui import native, ui


def main() -> None:
    """Run the app."""
    ui.label("Hello, World 0!")
    ui.run(
        port=native.find_open_port(),
        reload=os.environ.get("SANA_RELOAD", "FALSE") == "TRUE",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
