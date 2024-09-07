from datetime import datetime
from typing import List
from sqlmodel import select
from sqlalchemy.orm import joinedload
from functional import seq
import statistics

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

    def get_statistics_for_candidate(self, niche: Niche):
        """
        For a given niche, calculate the statistics for it and its keywords.

        Args:
            niche (Niche): The niche to calculate statistics for.

        Returns:
            dict: A dictionary containing the calculated statistics.
        """
        with self.conn.session() as session:
            session.add(niche)
            amazon_products = [
                p
                for p in niche.amazon_products
                if p.is_sponsored == False and p.rating is not None and p.rating >= 4.0
            ]

            keywords_statistics = []
            for k in niche.keywords:
                keyword_statistics = self.__get_statistics_for_candidate_keyword(k)
                if keyword_statistics:
                    keywords_statistics.append(keyword_statistics)

                for ss in k.suggestion_sets:
                    for suggested_keyword in ss.suggested_keywords:
                        keyword_statistics = (
                            self.__get_statistics_for_candidate_keyword(
                                suggested_keyword
                            )
                        )
                        if keyword_statistics:
                            keywords_statistics.append(keyword_statistics)

            statistics = {
                "niche": niche.name,
                "amazon_commission_rate": niche.amazon_commission_rate,
                "amazon_products_price": self.__calculate_descriptive_statistics(
                    amazon_products, "price_usd"
                ),
                "amazon_products_reviews": self.__calculate_descriptive_statistics(
                    amazon_products, "reviews"
                ),
                "amazon_products_ratings": self.__calculate_descriptive_statistics(
                    amazon_products, "rating"
                ),
                "amazon_products_bought": self.__calculate_descriptive_statistics(
                    amazon_products, "bought_last_month"
                ),
                "keywords": keywords_statistics,
            }

            return statistics

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

    def __get_statistics_for_candidate_keyword(self, keyword: Keyword):
        """
        Calculate statistics for a candidate keyword.

        Args:
            keyword (Keyword): The keyword to calculate statistics for.

        Returns:
            dict: A dictionary containing the calculated statistics.
        """
        if not keyword.metrics_reports or not keyword.serp_analyses:
            return None

        target_report = keyword.metrics_reports[-1]
        target_serp_analysis = keyword.serp_analyses[-1]
        serp_analysis_items = [
            item for item in target_serp_analysis.analysis_items if item.position <= 10
        ]
        serp_analysis_items.sort(key=lambda x: x.position)

        return {
            "keyword": keyword.keyword,
            "volume": target_report.volume,
            "domains_with_DA_under_30": len(
                [
                    item
                    for item in serp_analysis_items
                    if item.domain_authority and item.domain_authority <= 30
                ]
            ),
            "da_top_1": serp_analysis_items[0].domain_authority,
            "da_top_2": serp_analysis_items[1].domain_authority,
            "da_top_3": serp_analysis_items[2].domain_authority,
            "da": self.__calculate_descriptive_statistics(
                serp_analysis_items, "domain_authority"
            ),
            "backlinks": self.__calculate_descriptive_statistics(
                serp_analysis_items, "backlinks"
            ),
            "referring_domains": self.__calculate_descriptive_statistics(
                serp_analysis_items, "referring_domains"
            ),
            "nofollow_backlinks": self.__calculate_descriptive_statistics(
                serp_analysis_items, "nofollow_backlinks"
            ),
            "dofollow_backlinks": self.__calculate_descriptive_statistics(
                serp_analysis_items, "dofollow_backlinks"
            ),
        }

    def __calculate_descriptive_statistics(self, values: List[object], key: str):
        """
        Calculate descriptive statistics for a list of values.

        Args:
            values (List[object]): The values to calculate statistics for.
            key (str): The key to use for the statistics.

        Returns:
            dict: A dictionary containing the calculated statistics.
        """
        key_values = [getattr(v, key) for v in values if getattr(v, key) is not None]
        if not key_values:
            return {
                "max": None,
                "min": None,
                "avg": None,
                "stdv": None
            }

        return {
            "max": max(
                [getattr(v, key) for v in values if getattr(v, key) is not None]
            ),
            "min": min(
                [getattr(v, key) for v in values if getattr(v, key) is not None]
            ),
            "avg": statistics.mean(
                [getattr(v, key) for v in values if getattr(v, key) is not None]
            ),
            "stdv": statistics.stdev(
                [getattr(v, key) for v in values if getattr(v, key) is not None]
            ) if len(key_values) > 2 else 0,
        }
