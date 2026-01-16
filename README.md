# twd-m4sc0

> [!IMPORTANT]
> This is complete rewrite of the program `twd`. If you're using `<=v2.0.3` please make sure to upgrade to the newest major release. The archived version v2 can be viewed [here](https://github.com/m4sc0/twd-archived).

> twd-m4sc0 / twd is a command-line tool that allows you to temporarily save a working directory and easily navigate back to it. It's designed for developers and users who frequently need to switch between directories in the terminal.

That's what it was supposed to do at the start. Now it's more like a hub for your frequently visited directories. You can use it like a bookmark manager or for the quickest method of changing between directories that you can find.

There are quite a few things I wanna make better this time.

### Better directory changing

Previously twd wrote to a temp file, then a bash function used the contents if that file exists, cd's to the dir and deletes the file again. This time around I'm going a different way. I found the method `os.write(3, path)` which can write to [file descriptors](https://en.wikipedia.org/wiki/File_descriptor) directly. This is the same way stdout and stderr are handled in the background (i think). But i'm using a fourth (0 = stdin, 1 = stdout, 2 = stderr), unused FD to write to. This is then captured in the bash function separately from the stdout. 

### Improved TUI

For some reason I thought writing a whole UI system using [curses](https://de.wikipedia.org/wiki/Curses) was a good idea. Well, now at least I know better and can say that I won't do that ever again.

I'll use [Textual](https://textual.textualize.io/) now.

### Setup

It's possible to use TWD without the feature of cd'ing anywhere. But that's kinda lame lol. To make sure it works as intended, copy the following snippet into something like a `~/.bashrc` file.

```bash
t () {
  binary="twd"
  local target=$($binary "$@" 3>&1 >/dev/tty)
  if [[ -n "$target" && -d "$target" ]]; then
    cd "$target"
  fi
}
```
