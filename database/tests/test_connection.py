import inject
import pytest
from sqlalchemy import text
from config.config import Config
from database.connection import DatabaseConnection


class TestDatabaseConnection:

    def test_should_create_a_valid_database_connection_with_valid_credentials(self):
        database_connection = DatabaseConnection()

        with database_connection.session() as session:
            result = session.exec(text("SELECT 1")).fetchall()
            assert result[0][0] == 1

    def test_should_raise_an_exception_when_creating_a_database_connection_with_invalid_credentials(
        self,
    ):
        config = inject.instance(Config)
        config.POSTGRES_USER = "invalid_user"
        database_connection = DatabaseConnection()

        with pytest.raises(Exception):
            with database_connection.session() as session:
                session.exec(text("SELECT 1")).fetchall()
