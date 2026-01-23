from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal
from textual.widgets import Button, Label
from typing import Union

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

    def __init__(
            self, 
            message: Union[str, None] = None,
            confirm_text: str = "Yes",
            cancel_text: str = "No"
    ):
        """
        message: The message to display when popping the modal
        confirm_text: Text to show for confirmation
        cancel_text: Text to show for cancellation
        """
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text

        super().__init__()

    def compose_content(self) -> ComposeResult:
        """
        Abstract method for presenting custom shenanigans
        """
        if self.message:
            yield Label(self.message, id="content")
        else:
            yield Label("Are you sure?", id="content")

    def compose(self) -> ComposeResult:
        with Container():
            yield from self.compose_content()
            with Horizontal():
                yield Button(self.cancel_text, id="no", variant="error")
                yield Button(self.confirm_text, id="yes", variant="success")

    @on(Button.Pressed, "#no")
    def no_decision(self) -> None:
        """decision no"""
        self.dismiss(False)

    @on(Button.Pressed, "#yes")
    def yes_decision(self) -> None:
        """decision yes"""
        self.dismiss(True)

class EntryDeleteModal(ConfirmModal):
    """Confirmation modal with detailed entry information"""

    def __init__(self, entry):
        self.entry = entry
        super().__init__(confirm_text="Delete", cancel_text="Cancel")

    def compose_content(self) -> ComposeResult:
        yield Label(f"Delete entry '{self.entry.name}'?", id="content")
