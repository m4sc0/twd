from textual import on
from textual.app import App, ComposeResult, Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header, DataTable, Label

from .data import TwdManager

class TWDApp(App):
    """
    TWD TUI Application
    """

    BINDINGS = [
            Binding("j", "cursor_down", "Down"),
            Binding("k", "cursor_up", "Up"),
            Binding("q", "exit", "Exit", show=False),
        ]

    def __init__(self, manager: TwdManager, *args, **kwargs):
        self.manager = manager
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:

        yield Footer()
        yield DataTable(
                cursor_type='row',
                cell_padding=2,
                )

    def on_mount(self) -> None:
        table = self.query_one(DataTable)

        # add headers
        table.add_columns(*self.manager.CSV_HEADERS)
        
        # fill data
        for entry in self.manager.list_all():
            table.add_row(entry.alias, entry.name, str(entry.path), entry.created_at)

    # actions
    def action_cursor_down(self) -> None:
        """
        move cursor down
        """
        table = self.query_one(DataTable)

        current_row = table.cursor_coordinate.row
        next_row = (current_row + 1) % table.row_count

        table.move_cursor(row=next_row)

    def action_cursor_up(self) -> None:
        """
        move cursor up
        """
        table = self.query_one(DataTable)
        
        current_row = table.cursor_coordinate.row
        prev_row = (current_row - 1) % table.row_count

        table.move_cursor(row=prev_row)

    def action_exit(self) -> None:
        self.exit()

    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        table = event.data_table
        row_key = event.row_key

        # get row
        row_data = table.get_row(row_key)
        alias = row_data[0]

        # get entry
        entry = self.manager.get(alias)

        self.notify(f"Selected: {entry.alias} -> {entry.path}")

        # TODO: return path chosen

if __name__ == "__main__":
    app = TWDApp()
    app.run()
