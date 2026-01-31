from enum import Enum
from datetime import datetime
from textual import on
from textual.app import App, ComposeResult, Binding
from textual.containers import HorizontalGroup, VerticalScroll
from textual.reactive import reactive
from textual.widgets import Button, Digits, Footer, Header, DataTable, Label, Rule, Input
from textual.color import Color

from twd.config import Config
from twd.data import TwdManager, Entry
from twd.utils import fuzzy_search, linear_search
from twd.modals import ConfirmModal, EntryDeleteModal, EditEntryModal

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
            Binding("/", "slash_key", "Search"),
            Binding("d", "d_key", "Delete"),
            Binding("e", "e_key", "Edit"),
            Binding("escape", "escape_key", "Normal", show=False),
            # TODO: edit
            # TODO: rename

            # select
            Binding("enter", "select", "Select"),

            # exit
            Binding("q", "exit", "Exit"),
        ]

    mode: Mode = reactive(Mode.NORMAL)
    search_results = None

    def __init__(self, manager: TwdManager, *args, **kwargs):
        self.manager = manager
        super().__init__(*args, **kwargs)

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()

        # cwd
        yield HorizontalGroup(
                Label(f"cwd: {self.manager.cwd}", classes="cwd"),
                Label("", id="mode"),
                id="header"
                )

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

        # add headers
        table = self.query_one(DataTable)
        table.add_columns(*self.manager.CSV_HEADERS_FANCY)
        
        self._populate_table()

    def _populate_table(self, entries=None) -> None:
        """
        fill or refresh data table
        """
        table = self.query_one(DataTable)
        table.clear()

        if entries is None:
            entries = self.manager.list_all()
        
        # fill data
        for entry in entries:
            table.add_row(entry.alias, str(entry.path), entry.name, entry.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    def _current_row_entry(self) -> Entry:
        table = self.query_one(DataTable)

        # get row
        row_key = table.coordinate_to_cell_key(table.cursor_coordinate).row_key
        row_data = table.get_row(row_key)
        alias = row_data[0]

        # get entry
        entry = self.manager.get(alias)

        return entry

    def watch_mode(self, old_mode: Mode, new_mode: Mode) -> None:
        """
        react to mode changes
        """
        search_input = self.query_one("#search-input", Input)
        table = self.query_one(DataTable)
        mode_label = self.query_one("#mode")

        mode_label.update(str(new_mode.value).upper())

        if new_mode == Mode.SEARCH:
            # enter search mode
            search_input.display = True
            search_input.value = ""
            search_input.focus()

            mode_label.add_class("search")
        elif new_mode == Mode.NORMAL:
            # enter normal mode
            search_input.display = False
            search_input.value = ""
            self._populate_table()
            table.focus()

            mode_label.remove_class("search")

    # actions
    def action_cursor_down(self) -> None:
        """
        move cursor down
        """
        table = self.query_one(DataTable)

        try:
            current_row = table.cursor_coordinate.row
            next_row = (current_row + 1) % table.row_count
        except ZeroDivisionError as e:
            return

        table.move_cursor(row=next_row)

    def action_cursor_up(self) -> None:
        """
        move cursor up
        """
        table = self.query_one(DataTable)
        
        try:
            current_row = table.cursor_coordinate.row
            prev_row = (current_row - 1) % table.row_count
        except ZeroDivisionError as e:
            return

        table.move_cursor(row=prev_row)

    def action_slash_key(self) -> None:
        """
        enter search mode
        """
        if self.mode == Mode.SEARCH:
            return
        self.mode = Mode.SEARCH

    def action_escape_key(self) -> None:
        """
        enter normal mode
        """
        if self.mode == Mode.NORMAL:
            if self.search_results is not None:
                self._populate_table()
                self.search_results = None
            return
        self.mode = Mode.NORMAL

    def action_d_key(self) -> None:
        """
        open confirm modal and delete entry if yes
        """
        if not self.mode == Mode.NORMAL:
            return

        entry = self._current_row_entry()

        def check_delete(decision: bool | None) -> None:
            """
            open modal and return the decision
            """
            if not decision:
                return

            self.manager.remove(alias)

            self._populate_table()

            self.notify(f"Removed entry \"{entry.name}\"")

        self.push_screen(EntryDeleteModal(entry), check_delete)

    def action_e_key(self) -> None:
        """
        open edit modal and edit entry in place
        """
        entry = self._current_row_entry()

        def save_new_entry(new_entry: Entry | None) -> None:
            if not new_entry or entry == new_entry:
                # user hit 'Discard'
                # no changes so no update
                self.notify(f"No changes")
                return

            self.notify(f"Updated TWD '{new_entry.alias}'")

            self.manager.update(new_entry.alias, new_entry)
            self.manager._write_all(self.manager._read_all())
            self._populate_table()

        self.push_screen(EditEntryModal(entry), save_new_entry)

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

        if query is None:
            self._populate_table()
            return

        search_result = fuzzy_search(query, all_entries)

        filtered = [item[0] for item in search_result]

        self._populate_table(filtered)
        self.search_results = filtered

    @on(Input.Submitted, "#search-input")
    def on_search_submitted(self, e: Input.Submitted) -> None:
        """
        when user presses enter in search, return to normal mode
        """
        if self.mode != Mode.SEARCH:
            return

        self.mode = Mode.NORMAL
        self._populate_table(self.search_results)

        self.query_one(DataTable).focus()


    @on(DataTable.RowSelected)
    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        """
        select row and send back to the original program (probably cli)
        """
        table = event.data_table
        row_key = event.row_key

        entry = self._current_row_entry()

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
