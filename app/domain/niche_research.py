import inject
from typing import List
from functional import seq

from monitoring import Logger, LogTypeEnum
from app.interfaces.dtos.keyword_report import TypedKeyword
from app.repositories.keywords_repository import KeywordsRepository
from app.repositories.niches_repository import NichesRepository
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

    def fetch_data(self, niche: str, subniche: str) -> None:
        """
        Fetches data related to the specified niche and subniche.

        Args:
            niche (str): The niche to fetch data for.
            subniche (str): The subniche to fetch data for.
        """
        # If the niche already has keywords, the method returns early without fetching any data
        db_niche = self.niches_repository.find_or_insert_niche(niche, subniche)
        if len(db_niche.keywords) > 0:
            self.logger.notify(
                f"Data for niche '{niche}' and subniche '{subniche}' already exists.",
                LogTypeEnum.DEBUG,
            )
            return

        # Define primary keyword
        primary_kw = "best " + subniche

        self.logger.notify(
           f"Generating and fetching suggestions for primary keyword '{primary_kw}'",
           LogTypeEnum.INFO,
        )

        # Build and fetch suggestion keywords
        #base_suggestion_keywords = self.get_base_keywords(primary_kw)
        #suggestions = [
        #    TypedKeyword(keyword=sk, type=)
        #    for bsk in base_suggestion_keywords
        #    for sk in self.google_suggest_client.get_suggestions(bsk.keyword)
        #]
        suggestions = [
           TypedKeyword(keyword=sk, type="SUGGESTION")
           for sk in self.google_suggest_client.get_suggestions(primary_kw)
        ]

        self.logger.notify(
            f"Fetching report for primary keyword '{primary_kw}'",
            LogTypeEnum.INFO,
        )

        # Fetch report for primary keyword
        primary_kw_report = self.ubersuggest_api_client.get_keyword_report(
            primary_kw, suggestions
        )

        self.logger.notify(
            f"Saving data in the database",
            LogTypeEnum.INFO,
        )

        # Save report to the database
        self.keywords_repository.upsert_keyword_report(primary_kw_report, db_niche.id)

        self.logger.notify(
            f"Finished fetching data for '{niche}' and subniche '{subniche}'",
            LogTypeEnum.SUCCESS,
        )

    def get_base_keywords(self, keyword: str) -> List[TypedKeyword]:
        """
        Generates a list of base keywords with their type for getting further suggestions.

        Args:
            keyword (str): The base keyword to generate suggestions for.

        Returns:
            List[TypedKeyword]: A list of typed base suggestion keywords.
        """
        question_base_keywords = (
            seq(self.get_question_base_keywords(keyword))
            .map(lambda kw: TypedKeyword(keyword=kw, type="QUESTION"))
            .to_list()
        )
        preposition_base_keywords = (
            seq(self.get_preposition_base_keywords(keyword))
            .map(lambda kw: TypedKeyword(keyword=kw, type="PREPOSITION"))
            .to_list()
        )
        comparison_base_keywords = (
            seq(self.get_comparison_base_keywords(keyword))
            .map(lambda kw: TypedKeyword(keyword=kw, type="COMPARISON"))
            .to_list()
        )
        suggestion_base_keywords = (
            seq(self.get_suggestion_base_keywords(keyword))
            .map(lambda kw: TypedKeyword(keyword=kw, type="SUGGESTION"))
            .to_list()
        )

        return [
            *question_base_keywords,
            *preposition_base_keywords,
            *comparison_base_keywords,
            *suggestion_base_keywords,
        ]

    def get_question_base_keywords(self, keyword: str) -> List[str]:
        """
        Generates a list of base question keywords for getting further suggestions.

        Args:
            keyword (str): The base keyword to generate suggestions for.

        Returns:
            List[str]: A list of base question suggestion keywords.
        """
        question_terms = [
            "why",
            "where",
            "can",
            "who",
            "which",
            "will",
            "when",
            "what",
            "are",
            "how",
            "how many",
            "how much",
            "how often",
        ]
        return [f"{term} {keyword}" for term in question_terms]

    def get_preposition_base_keywords(self, keyword: str) -> List[str]:
        """
        Generates a list of base preposition keywords for getting further suggestions.

        Args:
            keyword (str): The base keyword to generate suggestions for.

        Returns:
            List[str]: A list of base preposition suggestion keywords.
        """
        preposition_terms = ["is", "for", "near", "without", "to", "with"]
        return [f"{term} {keyword}" for term in preposition_terms]

    def get_comparison_base_keywords(self, keyword: str) -> List[str]:
        """
        Generates a list of base comparison keywords for getting further suggestions.

        Args:
            keyword (str): The base keyword to generate suggestions for.

        Returns:
            List[str]: A list of base comparison suggestion keywords.
        """
        comparison_terms = ["vs", "versus", "and", "like"]
        return [f"{keyword} {term}" for term in comparison_terms]

    def get_suggestion_base_keywords(self, keyword: str) -> List[str]:
        """
        Generates a list of base keywords for getting further suggestions.

        Args:
            keyword (str): The base keyword to generate suggestions for.

        Returns:
            List[str]: A list of base suggestion keywords.
        """
        numered_suggestions = [f"{keyword} {i}" for i in range(0, 11)]
        lettered_suggestions = [f"{keyword} {chr(97 + i)}" for i in range(0, 26)]
        return [keyword, f"{keyword} "] + numered_suggestions + lettered_suggestions
