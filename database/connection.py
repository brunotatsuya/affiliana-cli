import inject
from sqlalchemy import Engine
from sqlmodel import Session, create_engine

from config import Config

# We import the models to register them into SQLModel metadata
from . import models


class DatabaseConnection:
    """
    Represents a connection to a database.
    """

    @inject.autoparams()
    def __init__(self, config: Config):
        self.config = config
        self.engine = self.__create_engine()

    def __build_connection_str(self):
        """
        Builds a connection string based on the DATABASE_URI environment variable.

        Returns:
            str: The connection string.

        """
        database_user = self.config.POSTGRES_USER
        database_password = self.config.POSTGRES_PASSWORD
        database_host = self.config.POSTGRES_HOST
        database_port = self.config.POSTGRES_PORT
        database_name = self.config.POSTGRES_DB
        return f"postgresql://{database_user}:{database_password}@{database_host}:{database_port}/{database_name}"

    def __create_engine(self) -> Engine:
        """
        Creates a database engine based on the DATABASE_URI environment variable.

        Returns:
            Engine: The created database engine.

        """
        echo = bool(self.config.ECHO_POSTGRES)
        return create_engine(self.__build_connection_str(), echo=echo)
    
    def session(self):
        """
        Creates a new session to the database.

        Returns:
            Session: The created session.

        """
        return Session(self.engine)