## insight-cli

## Overview

insight is a search engine that enables developers to search codebases using natural language queries. The insight-cli provides a CLI for developers to use insight.

## Installation

Before installing the insight-cli, ensure that Python version 3.10.0+ is installed. To install the insight-cli globally, run the following command:

```bash
$ pip install insight-cli
```

To ensure the insight-cli was successfully installed, check the insight-cli version by running the following command:

```bash
$ insight --version
```

## CLI Commands

The following cli commands require an internet connection.

To initialize the current directory as an insight repository, run the following command:

```bash
$ insight --initialize
```

The following commands must be ran in a directory that has been initialized as an insight repository.

To display the files and lines in an insight repository (excluding the files and directories specified in the .insightignore file) that satisfy a given natural language query, run the following command:

```bash
$ insight --query "<query>"
```

To uninitialize an insight repository, run the following command:

```bash
$ insight --uninitialize
```

## .insightignore

The .insightignore file contains regex patterns that specify directory and file paths to ignore in an insight repository.

<ul>
    <li>Empty lines are not matchable, they serve as separators for readability</li>
    <li>Non-comment lines will be considered as a single regex pattern.</li>
    <li>Lines starting with a hashtag '#' serve as comments. A single backslash '\' is placed in front of the first hashtag for patterns that begin with a hashtag.</li>
    <li>Scope comments designate patterns to apply exclusively within a specified scope until encountering another scope comment. '## _directory_' and '## _file_' are scope comments which target patterns within directory and file path scopes respectively.</li>
</ul>

```.insightignore
# Ignore all directory and file paths ending in ".log"
\.log$

# Ignore all directory and file paths starting with "test_"
^test_

# Ignore all directory and file paths containing "#"
\#

## _directory_
# Patterns now only apply to directory paths

# Ignore all directory paths starting with "main"
^main

## _file_
# Patterns now only apply to file paths

# Ignore all file paths starting with "cache"
^cache
```

## Example Usage

Install the insight-cli.

```bash
$ pip install insight-cli
```

Change the current working directory to the desired codebase. This example will use the following GitHub repository: https://github.com/ChenGrant/fitcountr.

```bash
$ git clone https://github.com/ChenGrant/fitcountr
$ cd fitcountr
```

Initialize the current directory as an insight repository. This will create a .insight directory inside the current directory.

```bash
$ insight --initialize
Initialized insight repository in /path/to/current/directory/fitcountr
```

Create a .insightignore file in the current directory and specify that insight should ignore the .git directory.

```bash
$ echo "^\.git$" > .insightignore
```

Search in the current insight repository (excluding the .git directory) for the "function that makes a connection to the mongodb database".

```bash
$ insight --query "function that makes a connection to the mongodb database"
2 matches found in the following files:
/server/src/config/database.js
    Line 3 - 15: const connectToDatabase = async () => {...};

/server/src/server.js
    Line 25: await connectToDatabase(app);
```

## Contributing

Interested in contributing? Please read the [Contribution Guidelines](./CONTRIBUTING.md) to get started.

## License

This project is licensed under the [MIT License](./LICENSE).
