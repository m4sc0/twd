from textual import on
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal
from textual.widgets import Button, Label
from typing import Union, TypeVar, Generic

from twd.data import Entry

T = TypeVar('T')

class ConfirmModal(ModalScreen[T], Generic[T]):
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
            cancel_text: str = "No",
            confirm_value: T | None = None,
            cancel_value: T | None = None,
    ):
        """
        message: The message to display when popping the modal
        confirm_text: Text to show for confirmation
        cancel_text: Text to show for cancellation
        """
        self.message = message
        self.confirm_text = confirm_text
        self.cancel_text = cancel_text

        self.confirm_value = confirm_value
        self.cancel_value = cancel_value

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
                yield Button(self.cancel_text, id="cancel", variant="error")
                yield Button(self.confirm_text, id="confirm", variant="success")

    @on(Button.Pressed, "#cancel")
    def cancel_pressed(self) -> None:
        self.dismiss(self.cancel_value)

    @on(Button.Pressed, "#confirm")
    def confirm_pressed(self) -> None:
        self.dismiss(self.confirm_value)

class EntryDeleteModal(ConfirmModal):
    """Confirmation modal with detailed entry information"""

    def __init__(self, entry):
        self.entry = entry
        super().__init__(confirm_text="Delete", cancel_text="Cancel")

    def compose_content(self) -> ComposeResult:
        yield Label(f"Delete entry '{self.entry.name}'?", id="content")
