import sys
import typer
from ..exception import FrictionlessException
from ..actions import transform
from .main import program
from . import common


@program.command(name="transform")
def program_transform(
    # Source
    source: str = common.source,
    # Command
    yaml: bool = common.yaml,
    json: bool = common.json,
):
    """Transform data using a provided pipeline.

    Please read more about Transform pipelines to write a pipeline
    that can be accepted by this function.
    """

    # Support stdin
    is_stdin = False
    if not source:
        if not sys.stdin.isatty():
            is_stdin = True
            source = [sys.stdin.buffer.read()]

    # Validate input
    if not source:
        message = 'Providing "source" is required'
        typer.secho(message, err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Transform source
    try:
        status = transform(source)
        if not status.valid:
            # NOTE: improve how we handle/present errors
            groups = [status.errors] + list(map(lambda task: task.errors, status.tasks))
            for group in groups:
                for error in group:
                    raise FrictionlessException(error)
    except Exception as exception:
        typer.secho(str(exception), err=True, fg=typer.colors.RED, bold=True)
        raise typer.Exit(1)

    # Return JSON
    if json:
        content = status.to_json()
        typer.secho(content)
        raise typer.Exit()

    # Return YAML
    if yaml:
        content = status.to_yaml().strip()
        typer.secho(content)
        raise typer.Exit()

    # Return default
    if is_stdin:
        source = "stdin"
    prefix = "success"
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
    typer.secho(f"# {prefix}: {source}", bold=True)
    typer.secho(f"# {'-'*len(prefix)}", bold=True)
