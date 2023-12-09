from io import BufferedReader
from pathlib import Path

from .file import File
from .string_matcher import StringMatcher


class Directory:
    def __init__(self, path: Path):
        self._path: Path = path
        self._files: list[File] = []
        self._subdirectories: list[Directory] = []

    @staticmethod
    def create_in_file_system(directory: "Directory") -> None:
        directory.path.mkdir()

        for file in directory.files:
            File.create_in_file_system(file)

        for subdirectory in directory.subdirectories:
            Directory.create_in_file_system(subdirectory)

    @staticmethod
    def create_from_path(
        dir_path: Path, ignorable_regex_patterns: dict[str, set] = None
    ) -> "Directory":
        if ignorable_regex_patterns is None:
            ignorable_regex_patterns = {"directory": set(), "file": set()}

        directory = Directory(dir_path)

        for entry_path in directory.path.iterdir():
            if entry_path.is_dir() and not StringMatcher.matches_any_regex_pattern(
                str(entry_path), ignorable_regex_patterns["directory"]
            ):
                directory.add_subdirectory(
                    Directory.create_from_path(entry_path, ignorable_regex_patterns)
                )

            if entry_path.is_file() and not StringMatcher.matches_any_regex_pattern(
                str(entry_path), ignorable_regex_patterns["file"]
            ):
                directory.add_file(File.create_from_path(entry_path))

        return directory

    def add_file(self, file: File) -> None:
        self._files.append(file)

    def add_subdirectory(self, subdirectory: "Directory") -> None:
        self._subdirectories.append(subdirectory)

    @property
    def path(self) -> Path:
        return self._path

    @property
    def files(self) -> list[File]:
        return self._files

    @property
    def subdirectories(self) -> list["Directory"]:
        return self._subdirectories

    @property
    def nested_files_path_to_binary_data(self) -> dict[str:BufferedReader]:
        file_path_to_binary_data = {
            str(file.path): file.binary_data for file in self._files
        }

        for subdirectory in self._subdirectories:
            file_path_to_binary_data.update(
                subdirectory.nested_files_path_to_binary_data
            )

        return file_path_to_binary_data
