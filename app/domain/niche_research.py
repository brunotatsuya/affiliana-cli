import inject

from monitoring import Logger, LogTypeEnum
from app.exceptions import NoDataFromSourceException, DataFetchError
from app.domain.utils import format_niche_name
from app.interfaces.dtos.keyword_report import TypedKeyword
from app.repositories import KeywordsRepository, NichesRepository
from integrations import GoogleSuggestClient, UbersuggestAPIClient


class NicheResearch:
    """
    Class representing the Niche Research functionality.
    """

    @inject.autoparams()
    def __init__(
        self,
        niches_repository: NichesRepository,
        keywords_repository: KeywordsRepository,
        google_suggest_client: GoogleSuggestClient,
        uberssugest_api_client: UbersuggestAPIClient,
        logger: Logger,
    ):
        self.niches_repository = niches_repository
        self.keywords_repository = keywords_repository
        self.google_suggest_client = google_suggest_client
        self.ubersuggest_api_client = uberssugest_api_client
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

        # Build and fetch suggestion keywords
        self.logger.notify(
            f"Generating and fetching suggestions for primary keyword '{primary_kw}'",
            LogTypeEnum.INFO,
        )

        try:
            suggestions = self.google_suggest_client.get_suggestions(primary_kw)
        except DataFetchError as e:
            self.logger.notify(e, LogTypeEnum.ERROR)
            return

        suggestions = [
            TypedKeyword(keyword=sk, type="SUGGESTION") for sk in suggestions
        ]

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
        except DataFetchError as e:
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

