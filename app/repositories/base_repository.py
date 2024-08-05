from abc import ABC
import inject

from database.connection import DatabaseConnection


class BaseRepository(ABC):
    """
    Base class for repositories.
    """

    @inject.autoparams()
    def __init__(self, conn: DatabaseConnection):
        self.conn = conn
