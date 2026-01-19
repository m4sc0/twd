# twd

A command-line tool for managing and navigating between directories in the terminal.

## What it does

`twd` lets you bookmark directories and quickly jump between them. Instead of typing out long paths or navigating through multiple `cd` commands, you save directories once and access them with vim-like motion bindings.

Think of it as a directory hub for places you visit frequently.

## Why this exists

I got tired of constantly navigating through the same directory trees. This tool saves time when you're working across multiple projects or deep directory structures.

No AI was used in the development of this tool. It's written by hand, contains bugs, and isn't particularly optimized. But it works for what I need, and I'm continuing to improve it.

## Installation

```bash
pip install twd-m4sc0
```

## Setup

To actually change directories (rather than just print paths), add this function to your `~/.bashrc` or `~/.zshrc`:

```bash
t () {
  binary="twd"
  local target=$($binary "$@" 3>&1 >/dev/tty)
  if [[ -n "$target" && -d "$target" ]]; then
    cd "$target"
  fi
}
```

The tool can work without this setup, but you'll only get path output instead of directory changes. This also allows for a quicker launch — instead of having to type `twd` over and over you can start it with just `t` (might conflict with other programs or functions).

## Dev environment

Clone the repo and install locally with 

```bash
pip install -e .
```

It is recommend to create a virtual environment and install the dependencies beforehand.

## How it works

`twd` uses file descriptor 3 to communicate the target directory to the shell function. The bash function captures this output and executes the `cd` command. This avoids using temporary files.

The interface is built with Textual, a Python TUI framework.

## Version 3

This is a complete rewrite from version 2. If you're using v2.0.3 or earlier, the archived version is available [here](https://github.com/m4sc0/twd-archived).

Changes include better directory handling, a proper TUI instead of hand-rolled curses code, and generally cleaner implementation.

## Status

The project is functional but has known issues. I'm actively developing it and fixing bugs as I find them. Check the issues tab for current problems and planned improvements. Contributions are always appreciated!

## License

MIT
