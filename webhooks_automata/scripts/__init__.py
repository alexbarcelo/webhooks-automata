import yaml
import click

from ..settings import Settings

@click.group()
@click.option("-s", "--settings-file", "settings",
              envvar="AUTOMATA_SETTINGS",
              default="./wha_settings.yaml",
              type=click.Path(exists=True, dir_okay=False),
              help="YAML settings with the automaton definitions")
@click.pass_context
def cli(ctx, settings):
    """Command line interface for the webhooks-automata project."""
    ctx.ensure_object(dict)
    with click.open_file(settings) as f:
        ctx.obj["settings"] = yaml.load(f, Loader=yaml.Loader)


@cli.command()
@click.pass_context
def validate(ctx):
    """Validate a YAML configuration file."""
    click.echo("Validation of %s" % ctx.obj["settings"])

    click.echo("pydantic says: %s" % Settings(**ctx.obj["settings"]))


@cli.command()
@click.argument("endpoint")
@click.pass_context
def trigger(ctx, endpoint):
    """Manually trigger the actions of an automaton.
    
    Provide the suffix as the ENDPOINT identifier."""
    pass
