from pathlib import Path
from unittest.mock import patch
import contextlib, io, unittest

from insight_cli.repository import InvalidRepositoryError
from insight_cli.commands import QueryCommand
from insight_cli.utils import Color


class TestQueryCommand(unittest.TestCase):
    def test_print_matches_with_no_matches(self) -> None:
        Color.init()
        matches = []

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            QueryCommand._print_matches(matches)
            output = buffer.getvalue().strip().split("\n")

        self.assertEqual(output, [Color.yellow("0 matches found")])

    def test_print_matches_with_one_match(self) -> None:
        Color.init()
        matches = [
            {
                "path": "/example_path",
                "start_line": 3,
                "end_line": 4,
                "content": "const x = () => {...};",
            }
        ]

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            QueryCommand._print_matches(matches)
            output = buffer.getvalue().strip().split("\n")

        self.assertEqual(
            output,
            [
                Color.yellow("1 match found in the following file:"),
                "/example_path",
                f"\tLine 3 - 4: {Color.green('const x = () => {...};')}",
            ],
        )

    def test_print_matches_with_two_matches(self) -> None:
        matches = [
            {
                "path": "/server/insight_cli/config/database.js",
                "start_line": 3,
                "end_line": 15,
                "content": "const connectToDatabase = async () => {...};",
            },
            {
                "path": "/server/insight_cli/server.js",
                "start_line": 25,
                "end_line": 25,
                "content": "await connectToDatabase(app);",
            },
        ]

        with io.StringIO() as buffer, contextlib.redirect_stdout(buffer):
            QueryCommand._print_matches(matches)
            output = buffer.getvalue().strip().split("\n")

        self.assertEqual(
            output,
            [
                Color.yellow("2 matches found in the following files:"),
                "/server/insight_cli/config/database.js",
                f"\tLine 3 - 15: {Color.green('const connectToDatabase = async () => {...};')}",
                "",
                "/server/insight_cli/server.js",
                f"\tLine 25: {Color.green('await connectToDatabase(app);')}",
            ],
        )

    @patch("insight_cli.commands.QueryCommand._print_matches")
    @patch("insight_cli.repository.Repository.query")
    @patch("insight_cli.api.ValidateRepositoryIdAPI.make_request")
    def test_execute_with_valid_repository(
        self,
        mock_validate_repository_id_api_make_request,
        mock_repository_query,
        mock_print_matches,
    ) -> None:
        query_command = QueryCommand()
        query_string = "sample_query_string"

        mock_validate_repository_id_api_make_request.return_value = {
            "repository_id_is_valid": True
        }

        mock_repository_query.return_value = []

        query_command.execute(query_string)

        mock_validate_repository_id_api_make_request.assert_called_once()
        mock_repository_query.assert_called_once_with(query_string)
        mock_print_matches.assert_called_once()

    @patch("builtins.print")
    @patch("insight_cli.repository.Repository.query")
    @patch("insight_cli.api.ValidateRepositoryIdAPI.make_request")
    def test_execute_with_invalid_repository(
        self,
        mock_validate_repository_id_api_make_request,
        mock_repository_query,
        mock_print,
    ) -> None:
        Color.init()
        query_command = QueryCommand()
        query_string = "sample_query_string"

        mock_validate_repository_id_api_make_request.return_value = {
            "repository_id_is_valid": True
        }
        mock_repository_query.side_effect = InvalidRepositoryError(Path.cwd())

        query_command.execute(query_string)

        mock_validate_repository_id_api_make_request.assert_called_once()
        mock_repository_query.assert_called_once_with(query_string)
        mock_print.assert_called_once_with(
            Color.red(f"{Path.cwd()} is not an insight repository")
        )

    @patch("insight_cli.repository.Repository.query")
    @patch("insight_cli.api.ValidateRepositoryIdAPI.make_request")
    def test_execute_with_connection_error(
        self, mock_validate_repository_id_api_make_request, mock_repository_query
    ) -> None:
        Color.init()
        query_command = QueryCommand()
        query_string = "sample_query_string"

        mock_validate_repository_id_api_make_request.return_value = {
            "repository_id_is_valid": True
        }
        mock_repository_query.side_effect = ConnectionError("error message")

        with self.assertRaises(ConnectionError):
            query_command.execute(query_string)

        mock_validate_repository_id_api_make_request.assert_called_once()
        mock_repository_query.assert_called_once_with(query_string)


if __name__ == "__main__":
    unittest.main()
