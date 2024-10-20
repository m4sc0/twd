import curses
import os

CONFIG = None
DIRS = None


def draw_hr(stdscr, y):
    _, max_cols = stdscr.getmaxyx()
    stdscr.addstr(y, 1, "─" * (max_cols - 2))


def display_select_screen(stdscr):
    max_items = len(DIRS)
    selected_entry = 0
    pre_selected_path = None

    running = True

    while running:
        # running = False
        stdscr.clear()

        # Border
        height, width = stdscr.getmaxyx()

        top_left = "╭"
        top_right = "╮"
        bottom_left = "╰"
        bottom_right = "╯"
        horizontal = "─"
        vertical = "│"

        stdscr.addstr(0, 0, top_left)
        stdscr.addstr(0, 1, horizontal * (width - 2))
        stdscr.addstr(0, width - 1, top_right)

        stdscr.refresh()

        stdscr.addstr(height - 1, 0, bottom_left)
        stdscr.addstr(height - 1, 1, horizontal * (width - 2))
        stdscr.addstr(height - 2, width - 1, bottom_right)

        stdscr.refresh()

        for i in range(1, height - 1):
            stdscr.addstr(i, 0, vertical)
            stdscr.addstr(i, width - 1, vertical)

        stdscr.refresh()

        inner_height = height - 2
        inner_width = width - 2

        # Other stuff
        stdscr.addstr(1, 1, f"Current directory: {os.getcwd()}")

        draw_hr(stdscr, 2)

        # Draw headers
        min_alias_len = 5
        min_id_len = 2
        min_path_len = 4

        max_alias_len = (
            max(max(len(entry["alias"]) for entry in DIRS.values()), min_alias_len)
            if DIRS
            else min_alias_len
        )
        max_path_len = (
            max(max(len(entry["path"]) for entry in DIRS.values()), min_path_len)
            if DIRS
            else min_path_len
        )
        max_id_len = (
            max(max(len(alias_id) for alias_id in DIRS.keys()), min_id_len)
            if DIRS
            else min_id_len
        )

        alias_col = max_alias_len + 2
        id_col = max_id_len + 2
        path_col = max_path_len

        alias_header = "ALIAS".ljust(alias_col, horizontal)
        id_header = "ID".ljust(id_col, horizontal)
        path_header = "PATH".ljust(path_col, horizontal)

        header_text = f"{alias_header}{id_header}{path_header}"
        stdscr.addstr(2, 1, header_text[:inner_width])

        # Selection process
        line_start = 3
        line_counter = line_start

        for entry_id, entry in enumerate(DIRS.values()):
            if line_counter >= inner_height:
                break

            alias = entry["alias"].ljust(max_alias_len)
            path = entry["path"].ljust(max_path_len)
            alias_id = list(DIRS.keys())[entry_id].ljust(max_id_len)

            line_text = f"{alias}  {alias_id}  {path}"
            line_text = line_text[:inner_width]
            line_text = line_text + " " * (inner_width - len(line_text))

            if entry_id == selected_entry:  # Select based on entry_id
                stdscr.addstr(line_counter, 1, line_text, curses.A_REVERSE)
                pre_selected_path = entry["path"]
            else:
                stdscr.addstr(line_counter, 1, line_text)
            line_counter += 1

        # draw "command about to be executed"
        if pre_selected_path:
            draw_hr(stdscr, height - 4)

            stdscr.addstr(height - 3, 1, "Command about to be executed:")

            stdscr.addstr(
                height - 2,
                1,
                f"$ cd {os.path.abspath(os.path.expanduser(pre_selected_path))}",
            )

        # Refresh to update changes
        stdscr.refresh()

        # Key bindings
        key = stdscr.getch()

        if key == curses.KEY_UP or key == ord("k"):
            selected_entry = max(0, selected_entry - 1)
        elif key == curses.KEY_DOWN or key == ord("j"):
            selected_entry = min(max_items - 1, selected_entry + 1)
        elif key == ord("\n"):
            selected_entry_id = list(DIRS.keys())[selected_entry]
            return DIRS[selected_entry_id]
        elif key == ord("q"):
            return None


def display_select(config, dirs):
    global CONFIG, DIRS
    CONFIG = config
    DIRS = dirs

    selected_directory = curses.wrapper(display_select_screen)

    return selected_directory or None