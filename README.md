<h1 align="center">Affiliana CLI</h1>
<div align="center">

 
![Docker](https://img.shields.io/badge/docker-blue?logo=docker)
![Poetry](https://img.shields.io/badge/poetry-blue?logo=poetry)
![Python](https://img.shields.io/badge/python-3.10-blue?logo=python)
![build](https://github.com/brunotatsuya/affiliana-cli/actions/workflows/run_tests.yml/badge.svg)


</div>


## ❔ What is this?

This is a CLI application with resources to help finding potential niches and products for affiliate marketing businesses.

## 🪛 Getting started

### 1. Install dependencies
Make sure you have the following dependencies installed on your machine before proceeding:
- [Docker](https://docs.docker.com/engine/install/) and [Docker Compose](https://docs.docker.com/compose/install/)
- [Poetry](https://python-poetry.org/docs/#installation)
- [Python](https://www.python.org/downloads/) (3.10+)

### 2. Install packages

In a terminal, navigate to the **root** folder of this repo. Then:

```bash
poetry install
```

### 3. Setup environment variables

Create a `.env.development` file on the root folder from the `.env.example`. See below what each variable is for:

| Variable | Description |
| :---     | :----       |
| POSTGRES_HOST | The PostgreSQL instance host. If running with docker, keep `localhost` |
| POSTGRES_PORT | The PostgreSQL instance port. If running with docker, keep `6001` |
| POSTGRES_USER | The username to use when creating and connecting to the database in PostgreSQL instance |
| POSTGRES_PASSWORD | The password for the username above |
| POSTGRES_DB | The database name to use when creating the database in the PostgreSQL instance |
| ECHO_POSTGRES | If true, SQLModel will echo the SQL operations done through the ORM interface |
| PROXY_PROVIDER_CREDENTIALS | Credentials to connect to a proxy provider. Must be a string in the format `username:password@host:port` |
| OPENAI_API_KEY | API key to connect with OpenAI API |

### 4. Run migrations
In a terminal, navigate to the **root** folder of this repo and run:

```bash
python scripts/run_migrations.py
```

## ▶️ Running the application
This is a CLI application based on [Typer](https://github.com/fastapi/typer). To run a command, navigate to the **root** folder, and use:

```bash
python scripts/run.py COMMAND SUBCOMMAND [ARGUMENTS]
```

You can get useful information by using the `--help` flag at any level. For example, to check all available commands:

```bash
python scripts/run.py --help
```

To check available subcommands for the `niche_research` command:

```bash
python scripts/run.py niche_research --help
```

To verify the expected arguments for the `perform` subcommand:

```bash
python scripts/run.py niche_research perform --help
```

## 🧪 Running unit tests

This uses [pytest](https://docs.pytest.org/en/latest) for unit testing. Use the script below to run the tests with coverage report:
```bash
python scripts/run_tests.py
```

*Obs: you don't need to worry about migrations as they are run everytime pytest is evoked.*
