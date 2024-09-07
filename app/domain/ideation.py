from typing import List
import inject

from app.domain import NicheResearch, ProductResearch
from app.repositories import NichesRepository
from database.connection import DatabaseConnection
from database.models import Keyword


class Ideation:
    """
    This class is responsible for handle Ideation functionalities.
    """

    @inject.autoparams()
    def __init__(
        self,
        niche_research: NicheResearch,
        product_research: ProductResearch,
        niches_repository: NichesRepository,
    ):
        self.niche_research = niche_research
        self.product_research = product_research
        self.niches_repository = niches_repository

    def start_gsa_data_collector(self) -> None:
        """
        Collects data for the GSA strategy.
        """
        while True:
            self.__collect_data_for_gsa()

    def generate_gsa_snapshot(self) -> None:
        """
        Generates a snapshot using the data collected for the GSA strategy.
        """
        # Get candidates
        candidates = self.niches_repository.get_niche_candidates(700, 30)

        candidates_metrics = []

        # For each candidate, get data and calculate metrics
        for candidate in candidates:
            candidate_metrics = self.niches_repository.get_statistics_for_candidate(candidate)
            candidates_metrics.append(candidate_metrics)

        rows = []
        for cm in candidates_metrics:
            rows += self.__format_candidate_snapshot_rows(cm)

        # Export to csv
        with open("gsa_snapshot.csv", "w") as file:
            # Write header
            file.write(",".join(rows[0].keys()) + "\n")

            # Write rows
            for row in rows:
                file.write(",".join([str(value) for value in row.values()]) + "\n")

    def __collect_data_for_gsa(self) -> None:
        """
        Collects data for the GSA strategy.
        """
        self.niche_research.fetch_data_from_gpt_ideas()
        self.niche_research.update_niches_amazon_commission_rates(force=False)
        self.product_research.fetch_amazon_products_for_candidates()

    def __format_candidate_snapshot_rows(self, data: dict) -> List[dict]:
        """
        Formats the data for the candidate snapshot.
        
        Args:
            data (dict): The data to format.

        Returns:
            List[dict]: The formatted data.
        """
        rows = []
        for kw_data in data["keywords"]:
            row = {
                "niche": data["niche"],
                "amazon_commission_rate": data["amazon_commission_rate"],
                "amazon_products_price_max": data["amazon_products_price"]["max"],
                "amazon_products_price_min": data["amazon_products_price"]["min"],
                "amazon_products_price_avg": data["amazon_products_price"]["avg"],
                "amazon_products_price_stdv": data["amazon_products_price"]["stdv"],
                "amazon_products_reviews_max": data["amazon_products_reviews"]["max"],
                "amazon_products_reviews_min": data["amazon_products_reviews"]["min"],
                "amazon_products_reviews_avg": data["amazon_products_reviews"]["avg"],
                "amazon_products_reviews_stdv": data["amazon_products_reviews"]["stdv"],
                "amazon_products_ratings_max": data["amazon_products_ratings"]["max"],
                "amazon_products_ratings_min": data["amazon_products_ratings"]["min"],
                "amazon_products_ratings_avg": data["amazon_products_ratings"]["avg"],
                "amazon_products_ratings_stdv": data["amazon_products_ratings"]["stdv"],
                "amazon_products_bought_max": data["amazon_products_bought"]["max"],
                "amazon_products_bought_min": data["amazon_products_bought"]["min"],
                "amazon_products_bought_avg": data["amazon_products_bought"]["avg"],
                "amazon_products_bought_stdv": data["amazon_products_bought"]["stdv"],
                "keyword": kw_data["keyword"],
                "volume": kw_data["volume"],
                "domains_with_DA_under_30": kw_data["domains_with_DA_under_30"],
                "da_top_1": kw_data["da_top_1"],
                "da_top_2": kw_data["da_top_2"],
                "da_top_3": kw_data["da_top_3"],
                "da_max": kw_data["da"]["max"],
                "da_min": kw_data["da"]["min"],
                "da_avg": kw_data["da"]["avg"],
                "da_stdv": kw_data["da"]["stdv"],
                "backlinks_max": kw_data["backlinks"]["max"],
                "backlinks_min": kw_data["backlinks"]["min"],
                "backlinks_avg": kw_data["backlinks"]["avg"],
                "backlinks_stdv": kw_data["backlinks"]["stdv"],
                "referring_domains_max": kw_data["referring_domains"]["max"],
                "referring_domains_min": kw_data["referring_domains"]["min"],
                "referring_domains_avg": kw_data["referring_domains"]["avg"],
                "referring_domains_stdv": kw_data["referring_domains"]["stdv"],
                "nofollow_backlinks_max": kw_data["nofollow_backlinks"]["max"],
                "nofollow_backlinks_min": kw_data["nofollow_backlinks"]["min"],
                "nofollow_backlinks_avg": kw_data["nofollow_backlinks"]["avg"],
                "nofollow_backlinks_stdv": kw_data["nofollow_backlinks"]["stdv"],
                "dofollow_backlinks_max": kw_data["dofollow_backlinks"]["max"],
                "dofollow_backlinks_min": kw_data["dofollow_backlinks"]["min"],
                "dofollow_backlinks_avg": kw_data["dofollow_backlinks"]["avg"],
                "dofollow_backlinks_stdv": kw_data["dofollow_backlinks"]["stdv"],
            }
            rows.append(row)
        return rows