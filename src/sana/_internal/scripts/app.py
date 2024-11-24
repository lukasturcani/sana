from nicegui import ui


def main() -> None:
    """Run the app."""
    ui.label("Hello, World!")
    ui.run()


if __name__ in {"__main__", "__mp_main__"}:
    main()
