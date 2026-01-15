import click
import os
from pathlib import Path
from .config import Config
from .data import TwdManager
from .tui import TWDApp

@click.group()
@click.pass_context
def cli(ctx):
    """
    TWD - Temp / Tracked Working Directory
    """
    ctx.ensure_object(dict)

    ctx.obj['config'] = Config.load() # load config
    ctx.obj['manager'] = TwdManager(ctx.obj['config'].data_path)

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
        click.echo(f"✓ Removed '{alias}'")
    except KeyError as e:
        click.echo(f"✗ {e}", err=True)
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
    
    for entry in entries:
        click.echo(f"{entry.alias:20} {entry.name:30} {entry.path}")
