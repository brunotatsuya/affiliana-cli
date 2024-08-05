import inject
from functional import seq
from datetime import datetime
from sqlmodel import select
from sqlalchemy.orm import joinedload

from app.interfaces.dtos.keyword_report import KeywordReport
from database.connection import DatabaseConnection
from database.models import (
    Keyword,
    MetricsReport,
    SERPAnalysisItem,
    SERPAnalysis,
    SuggestionSet,
)
from .base_repository import BaseRepository
from .niches_repository import NichesRepository


class KeywordsRepository(BaseRepository):
    """
    Repository class for managing keywords in the database.
    """

    @inject.autoparams()
    def __init__(self, conn: DatabaseConnection, niches_repo: NichesRepository):
        super().__init__(conn)
        self.niches_repo = niches_repo

    def upsert_keyword_report(
        self, keyword_report: KeywordReport, niche_id: int
    ) -> Keyword:
        """
        Inserts or updates a new keyword report into the database.

        Args:
            keyword_report (KeywordReport): The keyword report to insert.
            niche_id (int): The ID of the niche associated with the keyword.

        Returns:
            Keyword: The inserted keyword object.

        Raises:
            Exception: If an error occurs during the insertion process.
        """
        # Find the niche
        db_niche = self.niches_repo.find_niche_by_id(niche_id)
        if not db_niche:
            raise Exception(f"Niche with ID {niche_id} not found.")

        with self.conn.session() as session:

            # Check if the keyword already exists in the database
            keyword = self.find_keyword(
                keyword_report.info.keyword,
                keyword_report.info.language,
                keyword_report.info.loc_id,
            )

            # If not exists, then create a new keyword
            if not keyword:
                keyword = Keyword(
                    keyword=keyword_report.info.keyword,
                    language=keyword_report.info.language,
                    loc_id=keyword_report.info.loc_id,
                    type=keyword_report.info.type,
                    created_at=datetime.now(),
                    niches=[db_niche],
                )

            # Construct a new metrics report
            metrics_report = MetricsReport(
                competition=keyword_report.info.competition,
                volume=keyword_report.info.volume,
                cpc=keyword_report.info.cpc,
                cpc_dollars=keyword_report.info.cpc_dollars,
                sd=keyword_report.info.sd,
                pd=keyword_report.info.pd,
                created_at=keyword_report.info.updated_at,
                keyword=keyword,
            )

            # Construct a new serp analysis
            serp_analysis = SERPAnalysis(
                created_at=keyword_report.serp_analysis.updated_at,
                keyword=keyword,
            )

            serp_analysis_items = (
                seq(keyword_report.serp_analysis.serp_entries)
                .map(
                    lambda entry: SERPAnalysisItem(
                        url=entry.url,
                        title=entry.title,
                        domain=entry.domain,
                        position=entry.position,
                        type=entry.type,
                        clicks=entry.clicks,
                        domain_authority=entry.domain_authority,
                        facebook_shares=entry.facebook_shares,
                        pinterest_shares=entry.pinterest_shares,
                        linkedin_shares=entry.linkedin_shares,
                        google_shares=entry.google_shares,
                        reddit_shares=entry.reddit_shares,
                        created_at=keyword_report.serp_analysis.updated_at,
                        serp_analysis=serp_analysis,
                    )
                )
                .to_list()
            )

            # Construct new suggestion set
            suggestion_set = SuggestionSet(
                created_at=keyword_report.info.updated_at,
                keyword=keyword,
            )

            # For every suggested keyword, upsert the keyword, create the metrics
            # report and add it to the suggestion set
            for sk in keyword_report.suggestions:
                suggestion_keyword = self.find_keyword(
                    sk.keyword, sk.language, sk.loc_id
                )

                if not suggestion_keyword:
                    suggestion_keyword = Keyword(
                        keyword=sk.keyword,
                        language=sk.language,
                        loc_id=sk.loc_id,
                        type=sk.type,
                        created_at=datetime.now(),
                    )

                suggestion_metrics_report = MetricsReport(
                    competition=sk.competition,
                    volume=sk.volume,
                    cpc=sk.cpc,
                    cpc_dollars=sk.cpc_dollars,
                    sd=sk.sd,
                    pd=sk.pd,
                    created_at=sk.updated_at,
                    keyword=suggestion_keyword,
                )

                suggestion_keyword.metrics_reports.append(suggestion_metrics_report)
                suggestion_set.suggested_keywords.append(suggestion_keyword)

            # Establish relationships between the entities
            serp_analysis.analysis_items = serp_analysis_items
            keyword.metrics_reports.append(metrics_report)
            keyword.serp_analyses.append(serp_analysis)
            keyword.suggestion_sets.append(suggestion_set)

            try:
                session.add(keyword)
                session.commit()
                session.refresh(keyword)
                return keyword
            except Exception as e:
                session.rollback()
                raise e

    def find_keyword(self, keyword: str, language: str, loc_id: int) -> Keyword:
        """
        Find a keyword in the database based on the given parameters.

        Args:
            keyword (str): The keyword to search for.
            language (str): The language of the keyword.
            loc_id (int): The location ID associated with the keyword.

        Returns:
            Keyword: The found keyword object, or None if not found.
        """
        with self.conn.session() as session:
            statement = (
                select(Keyword)
                .options(joinedload(Keyword.metrics_reports))
                .options(joinedload(Keyword.serp_analyses))
                .options(joinedload(Keyword.suggestion_sets))
                .where(
                    Keyword.keyword == keyword,
                    Keyword.language == language,
                    Keyword.loc_id == loc_id,
                )
            )
            return session.exec(statement).first()
