# py-asana-cli

A modern command-line interface for Asana.

## Install

```bash
pip install py-asana-cli
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install py-asana-cli
```

## Authentication

Get a Personal Access Token from [Asana Developer Console](https://app.asana.com/0/developer-console).

```bash
# Option 1: Save to config file
asana config set-token YOUR_TOKEN

# Option 2: Environment variable
export ASANA_TOKEN=YOUR_TOKEN
```

## Quick Start

```bash
# See your user info
asana users me

# List workspaces and set default
asana workspaces list
asana workspaces select

# List projects
asana projects list

# List tasks in a project
asana tasks list -p PROJECT_GID

# Create a task
asana tasks create "My task" -p PROJECT_GID

# Complete a task
asana tasks complete TASK_GID

# JSON output for scripting
asana tasks list -p PROJECT_GID -o json
```

## Commands

```
asana config      - Manage configuration (set-token, show)
asana workspaces  - List and select workspaces
asana projects    - List projects, get details
asana tasks       - Create, list, update, complete, delete tasks
asana sections    - List sections and their tasks
asana users       - Get user info
```

Run `asana --help` or `asana <command> --help` for details.

## License

MIT
