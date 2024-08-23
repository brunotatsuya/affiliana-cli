<h1 align="center">Market Research</h1>
<div align="center">

 
![Docker](https://img.shields.io/badge/docker-blue?logo=docker)
![Poetry](https://img.shields.io/badge/poetry-blue?logo=poetry)
![Python](https://img.shields.io/badge/python-3.10-blue?logo=python)
![build](https://img.shields.io/github/actions/workflow/status/brunotatsuya/market-research/run_tests.yml)


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

In a terminal, navigate to the **root folder** of this repo. Then:

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

### 4. Setup docker
💡*Docker is used to containerize the PostgreSQL database instance.*

In a terminal, navigate to the **`/docker` folder** of this repo. Then:

```bash
docker compose -f docker-compose.yml up -d
```

This will create the `market_research` docker project with a `postgres-database` container inside of it, to be exposed to the port `6001` of your host machine (usually `localhost`). Make sure this is up and running before moving to the next step.

### 5. Run migrations
In a terminal, navigate to the **`/database` folder** of this repo.\
Then, activate the virtual environment by running:
```bash
poetry shell
```
Run migrations by:
```bash
alembic upgrade --head
```

## ▶️ Running the application
First, make sure the `market_research` docker project has its containers up and running.\
Then, navigate to the **root folder** of this repo and activate the virtual environment:
```bash
poetry shell
```

This is a CLI application based on [Typer](https://github.com/fastapi/typer). To run a command, use:

```bash
python main.py COMMAND SUBCOMMAND [ARGUMENTS]
```

The tree below represents the current available commands and subcommands:
```bash
main.py
   niche_research
      perform
      perform_from_file
   product_research
      fetch_amazon_products 
```

You can get useful information by using the `--help` flag at any level. For example, to check all available commands:

```bash
python main.py --help
```

To check available subcommands for the `niche_research` command:

```bash
python main.py niche_research --help
```

To verify the expected arguments for the `perform` subcommand:

```bash
python main.py niche_research perform --help
```

## 🧪 Running unit tests

### 1. Setup docker container (only once)
💡*For testing, Docker is also used to containerize the PostgreSQL database instance.*

In a terminal, navigate to the **`/docker` folder** of this repo. Then:

```bash
docker compose -f docker-compose.test.yml up -d
```

This will create the `market_research_test` docker project with a `postgres-database-test` container inside of it, to be exposed to the port `6002` of your host machine (usually `localhost`). Make sure this is up and running before moving to the next step.


### 2. Run pytest

Use the command below to run the tests with coverage report:
```bash
poetry run pytest -v --cov=.
```

*Obs: you don't need to worry about migrations as they are run everytime pytest is evoked.*
