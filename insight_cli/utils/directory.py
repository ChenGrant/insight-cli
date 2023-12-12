from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from datetime import datetime
import os

from .file import File
from .string_matcher import StringMatcher


class Directory:
    def __init__(self, path: Path):
        self._path: Path = path
        self._files: list[File] = []
        self._subdirectories: list[Directory] = []

    @staticmethod
    def create_from_path(
        dir_path: Path, ignorable_regex_patterns: dict[str, set] = None
    ) -> "Directory":
        if ignorable_regex_patterns is None:
            ignorable_regex_patterns = {"directory": set(), "file": set()}

        directory = Directory(dir_path)

        def add_directory_entry(entry_path):
            if entry_path.is_dir() and not StringMatcher.matches_any_regex_pattern(
                str(entry_path), ignorable_regex_patterns["directory"]
            ):
                directory.add_subdirectory(
                    Directory.create_from_path(entry_path, ignorable_regex_patterns)
                )

            if entry_path.is_file() and not StringMatcher.matches_any_regex_pattern(
                str(entry_path), ignorable_regex_patterns["file"]
            ):
                directory.add_file(File(entry_path))

        with ThreadPoolExecutor() as executor:
            executor.map(add_directory_entry, directory.path.iterdir())

        return directory

    def add_file(self, file: File) -> None:
        self._files.append(file)

    def add_subdirectory(self, subdirectory: "Directory") -> None:
        self._subdirectories.append(subdirectory)

    def compare_file_paths(
        self, previous_file_paths: dict[Path, datetime]
    ) -> dict[str, list[Path]]:
        file_paths_to_reinitialize = {"add": [], "update": [], "delete": []}

        def traverse(directory: Directory) -> None:
            nonlocal file_paths_to_reinitialize
            for file in directory.files:
                if file.path not in previous_file_paths:
                    file_paths_to_reinitialize["add"].append(file.path)
                    continue

                if (
                    datetime.fromtimestamp(os.path.getmtime(file.path))
                    != previous_file_paths[file.path]
                ):
                    file_paths_to_reinitialize["update"].append(file.path)

                del previous_file_paths[file.path]

            for subdirectory in directory.subdirectories:
                traverse(subdirectory)

        traverse(self)

        file_paths_to_reinitialize["delete"] = list(previous_file_paths.keys())

        return file_paths_to_reinitialize

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
    def nested_files(self) -> list[File]:
        nested_files = self._files

        for subdirectory in self._subdirectories:
            nested_files.extend(subdirectory.nested_files)

        return nested_files

    @property
    def nested_file_paths(self) -> list[Path]:
        nested_file_paths = [file.path for file in self._files]

        for subdirectory in self._subdirectories:
            nested_file_paths.extend(subdirectory.nested_file_paths)

        return nested_file_paths

    @property
    def nested_files_path_to_content(self) -> dict[str, bytes]:
        return {str(file.path): file.content for file in self.nested_files}
