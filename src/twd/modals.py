from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal
from textual.widgets import Button, Label

from twd.data import Entry

class ConfirmModal(ModalScreen[bool]):
    """A confirm modal"""

    DEFAULT_CSS = """
        ConfirmModal {
            align: center middle;
        }

        ConfirmModal > Container {
            width: auto;
            height: auto;
            border: thick $background 80%;
            background: $surface;
        }

        ConfirmModal > Container > Label {
            width: 100%;
            content-align-horizontal: center;
            margin-top: 1;
        }

        ConfirmModal > Container > Horizontal {
            width: auto;
            height: auto;
        }

        ConfirmModal > Container > Horizontal > Button {
            margin: 2 4;
        }
    """

    def __init__(self, entry: Entry):
        self.entry = entry
        super().__init__()

    def compose(self) -> ComposeResult:
        with Container():
            yield Label(f"entry data: {self.entry.name}")
            with Horizontal():
                yield Button("No", id="no", variant="error")
                yield Button("Yes", id="yes", variant="success")

    @on(Button.Pressed, "#no")
    def no_decision(self) -> None:
        """decision no"""
        self.dismiss(False)

    @on(Button.Pressed, "#yes")
    def yes_decision(self) -> None:
        """decision yes"""
        self.dismiss(True)
