from unittest.mock import Mock, call
import pytest
from app.domain.niche_research import NicheResearch
from app.interfaces.dtos.keyword_report import TypedKeyword

BASE_QUESTION_KEYWORDS = [
    TypedKeyword(keyword="why test keyword", type="QUESTION"),
    TypedKeyword(keyword="where test keyword", type="QUESTION"),
    TypedKeyword(keyword="can test keyword", type="QUESTION"),
    TypedKeyword(keyword="who test keyword", type="QUESTION"),
    TypedKeyword(keyword="which test keyword", type="QUESTION"),
    TypedKeyword(keyword="will test keyword", type="QUESTION"),
    TypedKeyword(keyword="when test keyword", type="QUESTION"),
    TypedKeyword(keyword="what test keyword", type="QUESTION"),
    TypedKeyword(keyword="are test keyword", type="QUESTION"),
    TypedKeyword(keyword="how test keyword", type="QUESTION"),
    TypedKeyword(keyword="how many test keyword", type="QUESTION"),
    TypedKeyword(keyword="how much test keyword", type="QUESTION"),
    TypedKeyword(keyword="how often test keyword", type="QUESTION"),
]

BASE_PREPOSITION_KEYWORDS = [
    TypedKeyword(keyword="is test keyword", type="PREPOSITION"),
    TypedKeyword(keyword="for test keyword", type="PREPOSITION"),
    TypedKeyword(keyword="near test keyword", type="PREPOSITION"),
    TypedKeyword(keyword="without test keyword", type="PREPOSITION"),
    TypedKeyword(keyword="to test keyword", type="PREPOSITION"),
    TypedKeyword(keyword="with test keyword", type="PREPOSITION"),
]

BASE_COMPARISON_KEYWORDS = [
    TypedKeyword(keyword="test keyword vs", type="COMPARISON"),
    TypedKeyword(keyword="test keyword versus", type="COMPARISON"),
    TypedKeyword(keyword="test keyword and", type="COMPARISON"),
    TypedKeyword(keyword="test keyword like", type="COMPARISON"),
]

BASE_SUGGESTION_KEYWORDS = [
    TypedKeyword(keyword="test keyword", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword ", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 0", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 1", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 2", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 3", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 4", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 5", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 6", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 7", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 8", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 9", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword 10", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword a", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword b", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword c", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword d", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword e", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword f", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword g", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword h", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword i", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword j", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword k", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword l", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword m", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword n", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword o", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword p", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword q", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword r", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword s", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword t", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword u", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword v", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword w", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword x", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword y", type="SUGGESTION"),
    TypedKeyword(keyword="test keyword z", type="SUGGESTION"),
]


class TestNicheResearch:
    @pytest.fixture
    def niche_research(self):
        return NicheResearch(Mock(), Mock(), Mock(), Mock())

    def test_should_generate_question_base_keywords_correctly(
        self, niche_research: NicheResearch
    ):
        keyword = "test keyword"
        expected = list(map(lambda tk: tk.keyword, BASE_QUESTION_KEYWORDS))
        assert niche_research.get_question_base_keywords(keyword) == expected

    def test_should_generate_preposition_base_keywords_correctly(
        self, niche_research: NicheResearch
    ):
        keyword = "test keyword"
        expected = list(map(lambda tk: tk.keyword, BASE_PREPOSITION_KEYWORDS))
        assert niche_research.get_preposition_base_keywords(keyword) == expected

    def test_should_generate_comparison_base_keywords_correctly(
        self, niche_research: NicheResearch
    ):
        keyword = "test keyword"
        expected = list(map(lambda tk: tk.keyword, BASE_COMPARISON_KEYWORDS))
        assert niche_research.get_comparison_base_keywords(keyword) == expected

    def test_should_generate_suggestion_base_keywords_correctly(
        self, niche_research: NicheResearch
    ):
        keyword = "test keyword"
        expected = list(map(lambda tk: tk.keyword, BASE_SUGGESTION_KEYWORDS))
        assert niche_research.get_suggestion_base_keywords(keyword) == expected

    def test_should_generate_base_keywords_correctly(
        self, niche_research: NicheResearch
    ):
        keyword = "test keyword"
        expected = (
            BASE_QUESTION_KEYWORDS
            + BASE_PREPOSITION_KEYWORDS
            + BASE_COMPARISON_KEYWORDS
            + BASE_SUGGESTION_KEYWORDS
        )
        assert niche_research.get_base_keywords(keyword) == expected

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

    def test_should_generate_base_suggestion_keywords_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.get_base_keywords = Mock(return_value=[])

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.get_base_keywords.assert_called_once_with("best Test Subniche")

    def test_should_fetch_keyword_suggestions_for_every_base_suggestion_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.get_base_keywords = Mock(return_value=BASE_SUGGESTION_KEYWORDS)
        niche_research.google_suggest_client.get_suggestions = Mock(return_value=[])

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.google_suggest_client.get_suggestions.assert_has_calls(
            [
                call(keyword)
                for keyword in list(
                    map(lambda tk: tk.keyword, BASE_SUGGESTION_KEYWORDS)
                )
            ]
        )

    def test_should_fetch_keyword_report_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.get_base_keywords = Mock(
            return_value=[
                TypedKeyword(keyword="what test keyword", type="QUESTION"),
                TypedKeyword(keyword="is test keyword", type="PREPOSITION"),
            ]
        )
        niche_research.google_suggest_client.get_suggestions = Mock(
            side_effect=[
                ["suggestion1", "suggestion2"],
                ["suggestion3", "suggestion4"],
            ]
        )

        # Act
        niche_research.fetch_data("Test Niche", "Test Subniche")

        # Assert
        niche_research.ubersuggest_api_client.get_keyword_report.assert_called_once_with(
            "best Test Subniche",
            [
                TypedKeyword(keyword="suggestion1", type="QUESTION"),
                TypedKeyword(keyword="suggestion2", type="QUESTION"),
                TypedKeyword(keyword="suggestion3", type="PREPOSITION"),
                TypedKeyword(keyword="suggestion4", type="PREPOSITION"),
            ],
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
