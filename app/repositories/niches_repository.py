from datetime import datetime
from sqlmodel import select
from sqlalchemy.orm import joinedload

from database.models import Niche
from .base_repository import BaseRepository


class NichesRepository(BaseRepository):
    """
    Repository class for managing niches in the database.
    """

    def find_niche_by_id(self, id: int) -> Niche:
        """
        Find a niche in the database by id.

        Args:
            id (int): The ID of the niche to search for.

        Returns:
            Niche: The found niche object, or None if not found.
        """
        with self.conn.session() as session:
            statement = (
                select(Niche).options(joinedload(Niche.keywords)).where(Niche.id == id)
            )
            return session.exec(statement).first()

    def find_niche(self, niche: str, subniche: str) -> Niche:
        """
        Find a niche in the database based on the niche and subniche names.

        Args:
            niche (str): The name of the niche.
            subniche (str): The name of the subniche.

        Returns:
            Niche: The found niche object, or None if not found.
        """
        with self.conn.session() as session:
            statement = (
                select(Niche)
                .options(joinedload(Niche.keywords))
                .where(Niche.niche == niche, Niche.subniche == subniche)
            )
            return session.exec(statement).first()

    def find_or_insert_niche(self, niche: str, subniche: str) -> Niche:
        """
        Find a niche in the database based on the niche and subniche names,
        or insert a new niche if it doesn't exist.

        Args:
            niche (str): The name of the niche.
            subniche (str): The name of the subniche.

        Returns:
            Niche: The found or inserted niche object.

        Raises:
            Exception: If an error occurs during the insertion process.
        """
        with self.conn.session() as session:
            try:
                db_niche = self.find_niche(niche, subniche)
                if db_niche:
                    return db_niche
                niche = Niche(
                    niche=niche,
                    subniche=subniche,
                    created_at=datetime.now(),
                )
                session.add(niche)
                session.commit()
                session.refresh(niche)
                niche.keywords = []
                return niche
            except Exception as e:
                session.rollback()
                raise e
