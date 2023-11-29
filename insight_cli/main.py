from insight_cli.cli import CLI
from insight_cli.commands import (
    create_initialize_command,
    create_uninitialize_command,
    create_query_command,
    create_version_command,
)


def insight_cli() -> None:
    cli = CLI(
        commands=[
            create_initialize_command(),
            create_query_command(),
            create_uninitialize_command(),
            create_version_command(),
        ],
        description="insight-cli"
    )

    cli.parse_arguments()

    cli.execute_invoked_commands()


if __name__ == "__main__":
    insight_cli()
