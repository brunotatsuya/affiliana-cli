import inject

from app.domain.utils import format_niche_name
from monitoring import Logger, LogTypeEnum
from integrations import AmazonSearchClient
from app.repositories import AmazonProductsRepository, NichesRepository


class ProductResearch:
    """
    This class is responsible for handle Product Research functionalities.
    """

    @inject.autoparams()
    def __init__(
        self,
        amazon_products_repository: AmazonProductsRepository,
        niches_repository: NichesRepository,
        amazon_search_client: AmazonSearchClient,
        logger: Logger,
    ):
        self.amazon_products_repository = amazon_products_repository
        self.niches_repository = niches_repository
        self.amazon_search_client = amazon_search_client
        self.logger = logger

    def fetch_amazon_products_for_niche(self, niche: str) -> None:
        """
        Fetches Amazon products related to the specified niche.

        Args:
            niche (str): The niche to fetch products for.
        """

        # Prepare niche name
        niche = format_niche_name(niche)

        db_niche = self.niches_repository.find_or_insert_niche(niche)

        # Live search on amazon
        self.logger.notify(
            f"Live search products on Amazon for niche '{niche}'",
            LogTypeEnum.INFO,
        )
        snapshots = self.amazon_search_client.get_products_for_keyword(niche)

        # Upsert the snapshots
        self.logger.notify(
            f"Saving data in the database",
            LogTypeEnum.INFO,
        )
        for snapshot in snapshots:
            self.amazon_products_repository.upsert_amazon_product(snapshot, db_niche.id)

        self.logger.notify(
            f"Finished fetching amazon products for '{niche}'",
            LogTypeEnum.SUCCESS,
        )
