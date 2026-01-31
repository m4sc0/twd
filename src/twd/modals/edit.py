from textual import on
from textual.app import ComposeResult
from textual.containers import Container, Horizontal
from textual.widgets import Button, Label, Input

from twd.data import Entry
from twd.modals import ConfirmModal

class EditEntryModal(ConfirmModal[Entry | None]):
    """A modal to edit an existing entry"""

    DEFAULT_CSS = """
        Label {
            width: 100%;
            text-align: left;
        }
        Input {
            margin: 1;
        }
    """

    def __init__(self, entry):
        """
        entry: the entry to edit
        """
        self.entry = Entry.from_values(entry.alias, entry.path, entry.name, entry.created_at)

        super().__init__(
                confirm_text="Save",
                cancel_text="Discard",
                confirm_value=self.entry,
                )

    def compose_content(self) -> ComposeResult:
        yield Label(f"Edit Entry", id="title")

        yield Label("Alias")
        yield Input(value=self.entry.alias, id="alias", disabled=True)
        yield Label("Path")
        yield Input(value=str(self.entry.path), id="path")
        yield Label("Name")
        yield Input(value=self.entry.name, id="name")
    
    @on(Input.Changed, "#path")
    def on_path_change(self, event: Input.Changed) -> None:
        self.entry.path = event.value
    
    @on(Input.Changed, "#name")
    def on_name_change(self, event: Input.Changed) -> None:
        self.entry.name = event.value

        
