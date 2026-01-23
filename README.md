<p align="center">
  <h1 align="center">asana</h1>
  <p align="center">A fast, modern CLI for Asana.</p>
</p>

<p align="center">
  <a href="https://pypi.org/project/py-asana-cli/"><img src="https://img.shields.io/pypi/v/py-asana-cli?color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/py-asana-cli/"><img src="https://img.shields.io/pypi/pyversions/py-asana-cli" alt="Python"></a>
  <a href="https://github.com/koenvanderveen/asana-cli/blob/main/LICENSE"><img src="https://img.shields.io/github/license/koenvanderveen/asana-cli" alt="License"></a>
</p>

<br>

```
$ asana tasks list -p 1210542925864934

                              Tasks
┏━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┓
┃ GID            ┃ Name               ┃ Done ┃ Due        ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━┩
│ 12108644513... │ Launch MVP         │ ✗    │ 2024-03-15 │
│ 12108611480... │ Write docs         │ ✓    │ 2024-03-01 │
│ 12107908102... │ Setup CI/CD        │ ✓    │ 2024-02-28 │
└────────────────┴────────────────────┴──────┴────────────┘
```

## Install

```bash
pip install py-asana-cli
```

## Setup

1. Get a token from [Asana Developer Console](https://app.asana.com/0/developer-console)
2. Configure the CLI:

```bash
asana config set-token YOUR_TOKEN
asana workspaces select  # set default workspace
```

## Usage

```bash
# Tasks
asana tasks list -p PROJECT_GID      # list tasks
asana tasks create "Task name" -p PROJECT_GID
asana tasks complete TASK_GID
asana tasks delete TASK_GID

# Projects & Sections
asana projects list
asana sections list -p PROJECT_GID

# JSON output for scripting
asana tasks list -p PROJECT_GID -o json | jq '.[].name'
```

## Commands

| Command | Description |
|---------|-------------|
| `asana tasks` | List, create, update, complete, delete tasks |
| `asana projects` | List projects, get details |
| `asana sections` | List sections and their tasks |
| `asana workspaces` | List and select workspaces |
| `asana users` | Get user info |
| `asana config` | Manage configuration |

Run `asana <command> --help` for details.

## License

MIT
