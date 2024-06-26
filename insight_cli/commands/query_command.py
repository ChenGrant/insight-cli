from pathlib import Path

from .base.command import Command
from insight_cli.repository import Repository, InvalidRepositoryError
from insight_cli.utils import Color


class QueryCommand(Command):
    @staticmethod
    def _print_matches(matches) -> None:
        num_matches = len(matches)

        if num_matches == 0:
            print(Color.yellow(f"{num_matches} matches found"))

        elif num_matches == 1:
            print(Color.yellow(f"{num_matches} match found in the following file:"))

        else:
            print(Color.yellow(f"{num_matches} matches found in the following files:"))

        for i, match in enumerate(matches):
            is_first_match = i == 0

            terminal_output = "" if is_first_match else "\n"

            terminal_output += f"{match['path']}\n"

            if match["start_line"] == match["end_line"]:
                terminal_output += (
                    f"\tLine {match['start_line']}: {Color.green(match['content'])}"
                )

            else:
                terminal_output += f"\tLine {match['start_line']} - {match['end_line']}: {Color.green(match['content'])}"

            print(terminal_output)

    def __init__(self):
        super().__init__(
            flags=["-q", "--query"],
            description="shows files in the current insight repository that satisfy the given natural language query",
        )

    def execute(self, query_string: str) -> None:
        try:
            repository = Repository(Path(""))
            matches = repository.query(query_string)
            self._print_matches(matches)

        except InvalidRepositoryError as e:
            print(Color.red(e))
