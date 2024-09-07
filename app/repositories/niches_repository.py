from datetime import datetime
from typing import List
from sqlmodel import select
from sqlalchemy.orm import joinedload
from functional import seq


from app.interfaces.dtos.niche_amazon_commission import NicheAmazonCommission
from database.models import Niche, Keyword
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

    def get_niche_candidates(self, minimum_volume: int, maximum_da: int) -> List[Niche]:
        """
        Get a list of niche candidates based on the specified criteria.

        Args:
            minimum_volume (int): The minimum volume at least one keyword of the niche should have.
            maximum_da (int): The maximum DA for at least one website in the top 10 SERP results should have.

        Returns:
            List[Niche]: A list of niche objects.
        """
        with self.conn.session() as session:
            niches = session.exec(select(Niche)).all()
            return (
                seq(niches)
                .filter(
                    lambda niche: self.__check_if_niche_is_valid_candidate(
                        niche, minimum_volume, maximum_da
                    )
                )
                .to_list()
            )

    def __check_if_niche_is_valid_candidate(
        self, niche: Niche, minimum_volume: int, maximum_da: int
    ) -> bool:
        """
        Check if a niche is a valid candidate based on the specified criteria.

        Args:
            niche (Niche): The niche object to check.
            minimum_volume (int): The minimum volume this niche should have.
            maximum_da (int): The maximum DA for at least one website in the top 10 last SERP results to have.

        Returns:
            bool: True if the niche is a valid candidate, False otherwise.
        """
        for keyword in niche.keywords:
            if self.__check_if_keyword_is_valid_candidate(
                keyword, minimum_volume, maximum_da
            ):
                return True

            if any(
                self.__check_if_keyword_is_valid_candidate(
                    suggested_keyword, minimum_volume, maximum_da
                )
                for suggestion_set in keyword.suggestion_sets
                for suggested_keyword in suggestion_set.suggested_keywords
            ):
                return True

        return False

    def __check_if_keyword_is_valid_candidate(
        self, keyword: Keyword, minimum_volume: int, maximum_da: int
    ) -> bool:
        """
        Check if a keyword is a valid candidate based on the specified criteria.

        Args:
            keyword (Keyword): The keyword object to check.
            minimum_volume (int): The minimum volume this keyword should have.
            maximum_da (int): The maximum DA for at least one website in the top 10 last SERP results to have.

        Returns:
            bool: True if the keyword is a valid candidate, False otherwise.
        """

        if not keyword.metrics_reports:
            return False

        last_metrics_report = keyword.metrics_reports[-1]

        if last_metrics_report.volume < minimum_volume:
            return False

        if not keyword.serp_analyses:
            return False

        last_serp_analysis = keyword.serp_analyses[-1]
        top_n_items = [
            item for item in last_serp_analysis.analysis_items if item.position <= 10
        ]
        return any(
            item.domain_authority != None and item.domain_authority <= maximum_da
            for item in top_n_items
        )
