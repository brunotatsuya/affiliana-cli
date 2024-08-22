from datetime import datetime
from typing import List
from sqlmodel import select
from sqlalchemy.orm import joinedload

from app.interfaces.dtos.niche_amazon_commission import NicheAmazonCommission
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

    def find_niche(self, name: str) -> Niche:
        """
        Find a niche in the database based its name.

        Args:
            name (str): The niche name.

        Returns:
            Niche: The found niche object, or None if not found.
        """
        with self.conn.session() as session:
            statement = (
                select(Niche)
                .options(joinedload(Niche.keywords))
                .where(Niche.name == name)
            )
            return session.exec(statement).first()

    def find_or_insert_niche(self, name: str) -> Niche:
        """
        Find a niche in the database based on its name,
        or insert a new niche if it doesn't exist.

        Args:
            name (str): The niche name.

        Returns:
            Niche: The found or inserted niche object.

        Raises:
            Exception: If an error occurs during the insertion process.
        """
        with self.conn.session() as session:
            try:
                db_niche = self.find_niche(name)
                if db_niche:
                    return db_niche
                niche = Niche(
                    name=name,
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

    def get_all_niches_names(self) -> List[str]:
        """
        Get the names of all niches in the database.

        Returns:
            list[str]: A list of niche names.
        """
        with self.conn.session() as session:
            statement = select(Niche.name)
            return session.exec(statement).all()

    def get_niches_names_with_no_amazon_commission_rate(self) -> List[str]:
        """
        Get the names of all niches in the database that have no commission rate.

        Returns:
            list[str]: A list of niche names.
        """
        with self.conn.session() as session:
            statement = select(Niche.name).where(Niche.amazon_commission_rate == None)
            return session.exec(statement).all()

    def update_niches_amazon_commission_rates(
        self, commissions_fetched: NicheAmazonCommission
    ) -> List[Niche]:
        """
        Update the commission rates of the specified niches.

        Args:
            commissions_fetched (List[NicheAmazonCommission]): A list of commission rates to update.

        Returns:
            List[Niche]: The updated niche objects.
        """
        with self.conn.session() as session:
            updated_niches = []
            for commission in commissions_fetched:
                db_niche = self.find_niche(commission.niche)
                if db_niche:
                    db_niche.amazon_commission_rate = commission.commission_rate
                    updated_niches.append(db_niche)
            session.add_all(updated_niches)
            session.commit()
            return updated_niches
