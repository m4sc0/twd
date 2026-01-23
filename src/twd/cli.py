import click
import os
from pathlib import Path
from . import __version__
from .config import Config
from .data import TwdManager
from .tui import TWDApp

@click.group(invoke_without_command=True)
@click.pass_context
@click.version_option(version=__version__)
def cli(ctx):
    """
    TWD - Temp / Tracked Working Directory
    """
    ctx.ensure_object(dict)

    ctx.obj['config'] = Config.load() # load config
    ctx.obj['manager'] = TwdManager(ctx.obj['config'].data_path)

    # if no subcommand was provided, launch TUI
    if ctx.invoked_subcommand is None:
        # TODO: launch TUI here

        path = TWDApp(manager=ctx.obj['manager']).run()

        if not path:
            print("Exiting...")
            exit(0)

        # write to fd3
        os.write(3, bytes(str(path), "utf-8"))
        exit(0)

@cli.command()
@click.argument('path')
@click.argument('alias', required=False)
@click.argument('name', required=False)
@click.pass_context
def save(ctx, path, alias, name):
    """
    Save a new twd with PATH, [opt] ALIAS and [opt] NAME
    """
    manager: TwdManager = ctx.obj['manager']

    path_obj = Path(path).expanduser().resolve()

    # get alias from path
    if alias is None:
        alias = path_obj.name.lower().replace(" ", "_")

    try:
        entry = manager.add(alias, path_obj, name)
        click.echo(f"Saved '{entry.alias}' -> {entry.path}")
    except ValueError as e:
        click.echo(f"Error: {e}")
        raise click.Abort()

@cli.command()
@click.argument('alias')
@click.pass_context
def get(ctx, alias):
    """
    get path for ALIAS
    """
    manager = ctx.obj['manager']

    entry = manager.get(alias)

    if entry is None:
        click.echo(f"Alias '{alias}' not found")
        raise click.Abort()

    # TODO: os.write(3) / write to fd3 for shell integration
    os.write(3, bytes(str(entry.path), "utf-8"))

    click.echo(f"cd-ing to {entry.path}")

@cli.command()
@click.argument('alias')
@click.pass_context
def remove(ctx, alias):
    """
    remove TWD by ALIAS
    """
    manager = ctx.obj['manager']
    
    try:
        manager.remove(alias)
        click.echo(f"Removed '{alias}'")
    except KeyError as e:
        click.echo(f"{e}", err=True)
        raise click.Abort()

@cli.command('list')
@click.pass_context
def list_twds(ctx):
    """List all TWDs"""
    manager = ctx.obj['manager']
    
    entries = manager.list_all()
    if not entries:
        click.echo("No TWDs saved yet. Use 'twd save <path> <alias>' to add one.")
        return
    
    invalid_found = False
    for entry in entries:
        if os.path.exists(entry.path) and not invalid_found:
            invalid_found = True
        click.echo(f"{entry.alias:20} {entry.name:30} {entry.path}")

    if not invalid_found:
        return

    click.echo(f"\nInvalid TWD paths found. Run <twd clean> to remove them.")

@cli.command('clean')
@click.option('--yes', '-y', is_flag=True, help="Remove all invalid entries without asking")
@click.pass_context
def clean(ctx, yes):
    """
    clean twds from invalid paths
    """
    manager = ctx.obj['manager']

    # all entries, valid and invalid
    entries = manager.list_all()

    # only invalids
    invalids = []
    for entry in entries:
        if os.path.exists(entry.path):
            continue

        invalids.append(entry)

    click.echo(f"Found {len(invalids)} invalid TWDs\n")

    # only valid
    valid_entries = []
    for entry in entries:
        if entry not in invalids:
            valid_entries.append(entry)

    # remove all
    if yes:
        click.echo("Removing all invalid entries...")
        manager._write_all(valid_entries)
        click.echo(f"Done. {len(valid_entries)} TWDs left.")
        return

    to_keep = []
    for inv in invalids:
        if not click.confirm(f"Do you want to remove '{inv.alias}'?", default=True):
            # user wants to keep invalid TWD (weird but i'll allow it)
            to_keep.append(inv)

    # write a unison list of valid entries and the ones to keep
    final_entries = valid_entries + to_keep
    manager._write_all(final_entries)
    click.echo(f"Done. {len(final_entries)} TWDs left.")
