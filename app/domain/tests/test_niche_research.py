from unittest.mock import MagicMock, Mock, call
import pytest
from app.domain.niche_research import NicheResearch


class TestNicheResearch:
    @pytest.fixture
    def niche_research(self):
        return NicheResearch(Mock(), Mock(), Mock(), Mock())

    def test_should_not_fetch_data_if_niche_has_keywords(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = [
            "keyword1"
        ]

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.google_suggest_client.get_suggestions.assert_not_called()
        niche_research.ubersuggest_api_client.get_keyword_report.assert_not_called()
        niche_research.keywords_repository.upsert_keyword_report.assert_not_called()

    def test_should_format_name_correctly(self, niche_research: NicheResearch):
        assert niche_research.format_name("Test Niche") == "test niche"
        assert niche_research.format_name("Test Subniche") == "test subniche"

    def test_should_format_niche_and_subniche_names_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.google_suggest_client.get_suggestions = Mock(return_value=[])
        niche_research.format_name = MagicMock(return_value="example")

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.format_name.assert_has_calls(
            [call("Test Niche"), call("Test Subniche")]
        )

    def test_should_fetch_keyword_suggestions_for_primary_keyword_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.google_suggest_client.get_suggestions = Mock(return_value=[])

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.google_suggest_client.get_suggestions.assert_called_once_with(
            "best test subniche"
        )

    def test_should_upsert_keyword_report_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.id = 123
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.get_base_keywords = Mock(return_value=[])
        niche_research.google_suggest_client.get_suggestions = Mock(return_value=[])
        niche_research.ubersuggest_api_client.get_keyword_report = Mock(
            return_value={"data": "report"}
        )

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.keywords_repository.upsert_keyword_report.assert_called_once_with(
            {"data": "report"}, 123
        )
