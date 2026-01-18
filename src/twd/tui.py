from enum import Enum
from textual import on
from textual.app import App, ComposeResult, Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header, DataTable, Label, Rule, Input
from textual.color import Color

from twd.config import Config
from twd.data import TwdManager
from twd.utils import search, linear_search

class Mode(Enum):
    NORMAL = "normal"
    SEARCH = "search"

class TWDApp(App):
    """
    TWD TUI Application
    """

    CSS_PATH = "tui.tcss"

    BINDINGS = [
            # motion
            Binding("j", "cursor_down", "Down"),
            Binding("k", "cursor_up", "Up"),

            # modify
            Binding("/", "enter_search_mode", "Search"),
            Binding("escape", "enter_normal_mode", "Normal", show=False),
            # TODO: edit
            # TODO: rename

            # select
            Binding("enter", "select", "Select"),

            # exit
            Binding("q", "exit", "Exit"),
        ]

    mode: Mode = reactive(Mode.NORMAL)

    def __init__(self, manager: TwdManager, *args, **kwargs):
        self.manager = manager
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

        # cwd
        yield Label(f"cwd: {self.manager.cwd}", classes="cwd")

        yield Input(placeholder="Search...", id="search-input")

        # twd selection table
        yield DataTable(
                cursor_type='row',
                cell_padding=2,
                # zebra_stripes=True,
                id="data",
                )

    def on_mount(self) -> None:
        # app config
        self.theme = "flexoki"
        self.title = "TWD"
        self.sub_title = "Tracked Working Directory"

        search_input = self.query_one("#search-input", Input)
        search_input.display = False
        
        self._populate_table()

    def _populate_table(self, entries=None) -> None:
        """
        fill or refresh data table
        """
        table = self.query_one(DataTable)
        table.clear(columns=True)

        # add headers
        table.add_columns(*self.manager.CSV_HEADERS)

        if entries is None:
            entries = self.manager.list_all()
        
        # fill data
        for entry in self.manager.list_all():
            table.add_row(entry.alias, str(entry.path), entry.name, entry.created_at)

    def watch_mode(self, old_mode: Mode, new_mode: Mode) -> None:
        """
        react to mode changes
        """
        search_input = self.query_one("#search-input", Input)
        table = self.query_one(DataTable)

        if new_mode == Mode.SEARCH:
            # enter search mode
            search_input.display = True
            search_input.value = ""
            search_input.focus()
            self.sub_title = "Tracked Working Directory — SEARCH"
        elif new_mode == Mode.NORMAL:
            # enter normal mode
            search_input.display = False
            search_input.value = ""
            self._populate_table()
            table.focus()
            self.sub_title = "Tracked Working Directory"

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

    def action_enter_search_mode(self) -> None:
        """
        enter search mode
        """
        if self.mode == Mode.SEARCH:
            return
        self.mode = Mode.SEARCH

    def action_enter_normal_mode(self) -> None:
        """
        enter normal mode
        """
        if self.mode == Mode.NORMAL:
            return
        self.mode = Mode.NORMAL

    def action_exit(self) -> None:
        self.exit()

    @on(Input.Changed, "#search-input")
    def on_search_input_changed(self, e: Input.Changed) -> None:
        """
        filter table as user types
        """
        if self.mode != Mode.SEARCH:
            return

        query = e.value

        all_entries = self.manager.list_all()

        # TODO: filter entries and repopulate table

        search_result = linear_search(query, all_entries)

        filtered = [entry for entry in all_entries if entry.alias in search_result]

        self._populate_table(filtered)

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self, e: Input.Submitted) -> None:
        """
        when user presses enter in search, return to normal mode
        """
        if self.mode != Mode.SEARCH:
            return

        self.mode = Mode.NORMAL

        self.query_one(DataTable).focus()


    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        select row and send back to the original program (probably cli)
        """
        table = event.data_table
        row_key = event.row_key

        # get row
        row_data = table.get_row(row_key)
        alias = row_data[0]

        # get entry
        entry = self.manager.get(alias)

        self.notify(f"Selected: {entry.alias} -> {entry.path}")

        # return selected path to cli
        self.exit(entry.path) 

if __name__ == "__main__":
    # made sure it works with 'serve'
    config = Config.load()
    manager = TwdManager(config.data_path)

    app = TWDApp(manager=manager)
    path = app.run()

    print(path)
