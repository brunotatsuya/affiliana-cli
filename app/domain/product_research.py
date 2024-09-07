import inject

from app.domain.utils import format_niche_name
from app.exceptions import DataFormatError
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

    def fetch_amazon_products_for_candidates(self) -> None:
        """
        Fetches Amazon products for all niche candidates.
        """

        self.logger.notify(
            "Calculating niche candidates",
            LogTypeEnum.INFO,
        )

        niches = self.niches_repository.get_niche_candidates(700, 30)

        for niche in niches:
            if self.amazon_products_repository.get_amazon_products_for_niche(niche.id):
                self.logger.notify(
                    f"Skipping niche '{niche.name}' because it already has products fetched",
                    LogTypeEnum.DEBUG,
                )
                continue

            try:
                self.fetch_amazon_products_for_niche(niche.name)
            except DataFormatError as e:
                self.logger.notify(
                    f"Error while fetching products for niche '{niche.name}': {str(e)}",
                    LogTypeEnum.ERROR,
                )
