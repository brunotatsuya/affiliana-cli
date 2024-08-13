from datetime import datetime
import inject
import pytest
from sqlmodel import delete, select
from sqlalchemy.orm import joinedload

from app.interfaces.dtos.keyword_report import KeywordReport
from app.repositories.keywords_repository import KeywordsRepository
from database.connection import DatabaseConnection
from database.models import (
    Keyword,
    NicheKeyword,
    MetricsReport,
    Niche,
    SERPAnalysis,
    SERPAnalysisItem,
    SuggestionSet,
    SuggestionSetKeyword,
)


# keyword_report fixture coming from conftest.py
class TestKeywordsRepository:

    @pytest.fixture(scope="class")
    def database_connection(self):
        return inject.instance(DatabaseConnection)

    @pytest.fixture(scope="class")
    def keywords_respository(self):
        return KeywordsRepository()

    @pytest.fixture
    def niche(self, database_connection: DatabaseConnection):

        with database_connection.session() as session:
            niche = session.exec(
                select(Niche).where(Niche.name == "Test Niche")
            ).first()
            if not niche:
                niche = Niche(
                    name="Test Niche",
                    created_at=datetime.now(),
                )
                session.add(niche)
                session.commit()
                session.refresh(niche)
            return niche

    @pytest.fixture(autouse=True)
    def clean_all_tables(self, database_connection: DatabaseConnection):
        yield
        with database_connection.session() as session:
            session.exec(delete(SERPAnalysisItem))
            session.exec(delete(SERPAnalysis))
            session.exec(delete(SuggestionSetKeyword))
            session.exec(delete(SuggestionSet))
            session.exec(delete(MetricsReport))
            session.exec(delete(NicheKeyword))
            session.exec(delete(Keyword))
            session.exec(delete(Niche))
            session.commit()

    def test_should_associate_keyword_to_niche_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            db_niche_keyword = session.exec(
                select(NicheKeyword).where(NicheKeyword.keyword_id == keyword.id)
            ).first()
            assert db_niche_keyword.niche_id == niche.id

    def test_should_insert_new_keyword_when_upserting_report_if_keyword_not_exists(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            db_keyword = session.exec(
                select(Keyword).where(Keyword.keyword == keyword_report.info.keyword)
            ).first()
            assert db_keyword is not None
            assert keyword.keyword == db_keyword.keyword
            assert keyword.language == db_keyword.language
            assert keyword.loc_id == db_keyword.loc_id

    def test_should_not_insert_new_keyword_when_upserting_report_if_keyword_exists(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Insert the same keyword report again
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            db_keywords = session.exec(
                select(Keyword).where(Keyword.keyword == keyword_report.info.keyword)
            ).all()
            assert len(db_keywords) == 1

    def test_should_create_new_metrics_report_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Insert new keyword report
        keyword_report.info.cpc_dollars = 99.0
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            db_metrics_reports = session.exec(
                select(MetricsReport).where(MetricsReport.keyword_id == keyword.id)
            ).all()
            assert len(db_metrics_reports) == 2
            assert db_metrics_reports[0].cpc_dollars == 0.5
            assert db_metrics_reports[1].cpc_dollars == 99.0

    def test_should_create_new_serp_analysis_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Insert new keyword report
        keyword_report.serp_analysis.updated_at = "2021-01-02T00:00:00"
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            db_serp_analyses = session.exec(
                select(SERPAnalysis).where(SERPAnalysis.keyword_id == keyword.id)
            ).all()
            assert len(db_serp_analyses) == 2
            assert db_serp_analyses[0].created_at == datetime.fromisoformat(
                "2021-01-01T00:00:00"
            )
            assert db_serp_analyses[1].created_at == datetime.fromisoformat(
                "2021-01-02T00:00:00"
            )

    def test_should_create_serp_analysis_items_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            serp_analysis = session.exec(
                select(SERPAnalysis)
                .options(joinedload(SERPAnalysis.analysis_items))
                .where(SERPAnalysis.keyword_id == keyword.id)
            ).first()

            assert len(serp_analysis.analysis_items) == 2
            assert serp_analysis.analysis_items[0].url == "https://example.com"
            assert serp_analysis.analysis_items[1].url == "https://example2.com"

    def test_should_create_new_suggestion_set_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Insert new keyword report
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            db_suggestion_sets = session.exec(
                select(SuggestionSet).where(SuggestionSet.keyword_id == keyword.id)
            ).all()
            assert len(db_suggestion_sets) == 2

    def test_should_create_suggested_keywords_when_upserting_report_and_suggested_keywords_dont_exist(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            suggested_keywords = session.exec(
                select(Keyword).where(Keyword.type != "PRIMARY")
            ).all()

            assert len(suggested_keywords) == 3
            assert suggested_keywords[0].keyword == "match suggestion 1"
            assert suggested_keywords[1].keyword == "match suggestion 2"
            assert suggested_keywords[2].keyword == "match suggestion 3"

    def test_should_not_create_suggested_keywords_when_upserting_report_and_suggested_keywords_exist(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Insert a new keyword report
        keyword_report.suggestions[0].keyword = "match suggestion 4"
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            suggested_keywords = session.exec(
                select(Keyword).where(Keyword.type != "PRIMARY")
            ).all()

            assert len(suggested_keywords) == 4

    def test_should_create_new_metrics_report_for_suggested_keywords_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Insert a new report
        keyword_report.suggestions[0].keyword = "match suggestion 4"
        keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            match1 = session.exec(
                select(Keyword)
                .options(joinedload(Keyword.metrics_reports))
                .where(Keyword.keyword == "match suggestion 2")
            ).first()

            match5 = session.exec(
                select(Keyword)
                .options(joinedload(Keyword.metrics_reports))
                .where(Keyword.keyword == "match suggestion 4")
            ).first()

            assert len(match1.metrics_reports) == 2
            assert len(match5.metrics_reports) == 1

    def test_should_associate_suggested_keywords_to_suggestion_set_when_upserting_report(
        self,
        database_connection: DatabaseConnection,
        niche: Niche,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword report
        keyword = keywords_respository.upsert_keyword_report(keyword_report, niche.id)

        # Assert
        with database_connection.session() as session:
            suggestion_set = session.exec(
                select(SuggestionSet)
                .options(joinedload(SuggestionSet.suggested_keywords))
                .where(SuggestionSet.keyword_id == keyword.id)
            ).first()

            assert len(suggestion_set.suggested_keywords) == 3
            assert suggestion_set.suggested_keywords[0].keyword == "match suggestion 1"
            assert (
                suggestion_set.suggested_keywords[1].keyword == "match suggestion 2"
            )
            assert (
                suggestion_set.suggested_keywords[2].keyword == "match suggestion 3"
            )

    def test_should_return_existing_keyword_when_searching(
        self,
        database_connection: DatabaseConnection,
        keywords_respository: KeywordsRepository,
        keyword_report: KeywordReport,
    ):
        # Insert the keyword
        keyword = Keyword(
            keyword=keyword_report.info.keyword,
            language=keyword_report.info.language,
            loc_id=keyword_report.info.loc_id,
            type=keyword_report.info.type,
            created_at=datetime.now(),
        )
        with database_connection.session() as session:
            session.add(keyword)
            session.commit()
            session.refresh(keyword)

        # Find the keyword
        searched_keyword = keywords_respository.find_keyword(
            keyword_report.info.keyword,
            keyword_report.info.language,
            keyword_report.info.loc_id,
        )

        # Assert
        assert searched_keyword == keyword

    def test_should_return_none_when_searching_for_non_existing_keyword(
        self, keywords_respository: KeywordsRepository
    ):
        # Find the keyword
        searched_keyword = keywords_respository.find_keyword("non-existing", "en", 2840)

        # Assert
        assert searched_keyword is None
