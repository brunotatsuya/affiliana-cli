import inject
from unittest.mock import MagicMock
from pathlib import Path
from alembic.config import Config as AlembicConfig
from alembic import command

from config import Config, setup_injector
from monitoring import Logger
from app.domain.niche_research import NicheResearch
from integrations.retriable_http_client import RetriableHttpClient


def injector_config(binder):
    binder.bind(Config, Config(_env_file=".env.test"))
    binder.bind(Logger, MagicMock())
    binder.bind(RetriableHttpClient, MagicMock())
    binder.bind(NicheResearch, MagicMock())


def run_migrations_psql():
    database_dir = Path(__file__).resolve().parent / "database"
    alembic_cfg = AlembicConfig(database_dir / "alembic.ini")
    app_config = inject.instance(Config)
    database_user = app_config.POSTGRES_USER
    database_password = app_config.POSTGRES_PASSWORD
    database_host = app_config.POSTGRES_HOST
    database_port = app_config.POSTGRES_PORT
    database_name = app_config.POSTGRES_DB
    database_uri = f"postgresql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"

    alembic_cfg.set_main_option("script_location", str(database_dir / "migrations"))
    alembic_cfg.set_main_option("sqlalchemy.url", database_uri)
    command.upgrade(alembic_cfg, "head")


setup_injector(injector_config)
run_migrations_psql()
