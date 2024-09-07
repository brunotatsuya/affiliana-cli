import inject

from monitoring import Logger, LogTypeEnum
from app.exceptions import NoDataFromSourceException
from app.domain.utils import format_niche_name
from app.repositories import KeywordsRepository, NichesRepository
from integrations import UbersuggestAPIClient, OpenAIApiClient


class NicheResearch:
    """
    Class representing the Niche Research functionality.
    """

    @inject.autoparams()
    def __init__(
        self,
        niches_repository: NichesRepository,
        keywords_repository: KeywordsRepository,
        uberssugest_api_client: UbersuggestAPIClient,
        openai_api_client: OpenAIApiClient,
        logger: Logger,
    ):
        self.niches_repository = niches_repository
        self.keywords_repository = keywords_repository
        self.ubersuggest_api_client = uberssugest_api_client
        self.openai_api_client = openai_api_client
        self.logger = logger

    def fetch_data(self, niche: str) -> None:
        """
        Fetches data related to the specified niche.

        Args:
            niche (str): The niche to fetch data for.
        """
        # Prepare niche name
        niche = format_niche_name(niche)

        # If the niche already has keywords, the method returns early without fetching any data
        db_niche = self.niches_repository.find_or_insert_niche(niche)
        if len(db_niche.keywords) > 0:
            self.logger.notify(
                f"Data for niche '{niche}' already exists.",
                LogTypeEnum.DEBUG,
            )
            return

        # Define primary keyword
        primary_kw = "best " + niche

        # Fetch report for primary keyword
        self.logger.notify(
            f"Fetching report for primary keyword '{primary_kw}'",
            LogTypeEnum.INFO,
        )

        try:
            primary_kw_report = self.ubersuggest_api_client.get_keyword_report(
                primary_kw
            )
        except NoDataFromSourceException as e:
            self.logger.notify(e, LogTypeEnum.WARNING)
            return
        except Exception as e:
            self.logger.notify(e, LogTypeEnum.ERROR)
            return

        # Save report to the database
        self.logger.notify(
            f"Saving data in the database",
            LogTypeEnum.INFO,
        )

        self.keywords_repository.upsert_keyword_report(primary_kw_report, db_niche.id)

        self.logger.notify(
            f"Finished fetching data for '{niche}'",
            LogTypeEnum.SUCCESS,
        )

    def update_niches_amazon_commission_rates(self, force: bool) -> None:
        """
        Update the Amazon commission rates for niches in the database.

        Args:
            force (bool): If true fetches commission rates for all niches,
            otherwise only for niches with no commission rate.
        """
        # Get niches names
        if force:
            niches = self.niches_repository.get_all_niches_names()
        else:
            niches = (
                self.niches_repository.get_niches_names_with_no_amazon_commission_rate()
            )

        if not niches:
            self.logger.notify(
                "No niches to update Amazon commission rates.",
                LogTypeEnum.DEBUG,
            )
            return

        # Fetch commission rates on batches of 50
        commission_rates = []
        for i in range(0, len(niches), 50):
            # Update commission rates
            self.logger.notify(
                f"Making interaction with OpenAI API for niches {i} to {i+50}",
                LogTypeEnum.INFO,
            )

            try:
                commission_rates += (
                    self.openai_api_client.get_amazon_commission_rate_for_niches(
                        niches[i : i + 50]
                    )
                )
            except Exception as e:
                self.logger.notify(
                    f"Failed getting commission rates for niches: {e}",
                    LogTypeEnum.ERROR,
                )

        # Update commission rates
        self.logger.notify(
            f"Saving commissions in the database",
            LogTypeEnum.INFO,
        )

        self.niches_repository.update_niches_amazon_commission_rates(commission_rates)

        self.logger.notify(
            f"Finished updating Amazon commission rates for niches.",
            LogTypeEnum.SUCCESS,
        )

    def fetch_data_from_gpt_ideas(self) -> None:
        """
        Fetch data for niches from GPT ideas.
        """
        self.logger.notify(
            f"Making interaction with OpenAI API for ideas",
            LogTypeEnum.INFO,
        )

        niche_ideas = self.openai_api_client.get_niche_ideas()

        for niche in niche_ideas:
            self.fetch_data(niche)
