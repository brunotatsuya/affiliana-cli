import inject

from app.domain import NicheResearch, ProductResearch


class Ideation:
    """
    This class is responsible for handle Ideation functionalities.
    """

    @inject.autoparams()
    def __init__(
        self, niche_research: NicheResearch, product_research: ProductResearch
    ):
        self.niche_research = niche_research
        self.product_research = product_research

    def start_gsa_data_collector(self) -> None:
        """
        Collects data for the GSA strategy.
        """
        while True:
            self.__collect_data_for_gsa()

    def __collect_data_for_gsa(self) -> None:
        """
        Collects data for the GSA strategy.
        """
        self.niche_research.fetch_data_from_gpt_ideas()
        self.niche_research.update_niches_amazon_commission_rates(force=False)
        self.product_research.fetch_amazon_products_for_candidates()
