import pytest
from unittest.mock import Mock, patch

from app.domain import NicheResearch
from app.interfaces.dtos.niche_amazon_commission import NicheAmazonCommission


@pytest.fixture
def niche_research():
    return NicheResearch(Mock(), Mock(), Mock(), Mock(), Mock())


class TestNicheResearchFetchData:
    def test_should_not_fetch_data_if_niche_has_keywords(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = [
            "keyword1"
        ]

        # Act
        niche_research.fetch_data("Test Niche")

        # Assert
        niche_research.ubersuggest_api_client.get_keyword_report.assert_not_called()
        niche_research.keywords_repository.upsert_keyword_report.assert_not_called()

    def test_should_format_niche_name_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks

        with patch("app.domain.niche_research.format_niche_name") as format_niche_name:
            niche_research.fetch_data("Test Niche")
            format_niche_name.assert_called_once_with("Test Niche")

    def test_should_upsert_keyword_report_when_fetching_new_niche(
        self, niche_research: NicheResearch
    ):
        # Make sure the niche has no keywords
        niche_research.niches_repository.find_or_insert_niche.return_value.id = 123
        niche_research.niches_repository.find_or_insert_niche.return_value.keywords = []

        # Setup mocks
        niche_research.get_base_keywords = Mock(return_value=[])
        niche_research.ubersuggest_api_client.get_keyword_report = Mock(
            return_value={"data": "report"}
        )

        # Act
        niche_research.fetch_data("Test Niche")

        # Assert
        niche_research.keywords_repository.upsert_keyword_report.assert_called_once_with(
            {"data": "report"}, 123
        )


class TestNicheResearchUpdateNichesAmazonCommissionRates:
    def test_should_only_use_niches_with_no_commission_if_force_flag_is_false(
        self, niche_research: NicheResearch
    ):
        # Setup mocks
        niche_research.niches_repository.get_niches_names_with_no_amazon_commission_rate = Mock(
            return_value=[]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches = Mock(
            return_value=[]
        )

        # Act
        niche_research.update_niches_amazon_commission_rates(force=False)

        # Assert
        niche_research.niches_repository.get_niches_names_with_no_amazon_commission_rate.assert_called_once_with()
        niche_research.niches_repository.get_all_niches_names.assert_not_called()

    def test_should_use_all_niches_if_force_flag_is_true(
        self, niche_research: NicheResearch
    ):
        # Setup mocks
        niche_research.niches_repository.get_all_niches_names = Mock(return_value=[])
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches = Mock(
            return_value=[]
        )

        # Act
        niche_research.update_niches_amazon_commission_rates(force=True)

        # Assert
        niche_research.niches_repository.get_niches_names_with_no_amazon_commission_rate.assert_not_called()
        niche_research.niches_repository.get_all_niches_names.assert_called_once_with()

    def test_should_fetch_commissions_for_all_considered_niches(
        self, niche_research: NicheResearch
    ):
        # Setup mocks
        niche_research.niches_repository.get_all_niches_names = Mock(
            return_value=["Cat toys", "Pasta makers", "Dog toys", "Chef knives"]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches = Mock(
            return_value=[]
        )

        # Act
        niche_research.update_niches_amazon_commission_rates(force=True)

        # Assert
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches.assert_called_once_with(
            ["Cat toys", "Pasta makers", "Dog toys", "Chef knives"]
        )

    def test_should_chunk_fetch_commissions_request_for_every_50_niches(
        self, niche_research: NicheResearch
    ):
        # Setup mocks
        niches = [f"niche_{i}" for i in range(217)]
        niche_research.niches_repository.get_all_niches_names = Mock(
            return_value=niches
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches = Mock(
            return_value=[]
        )

        # Act
        niche_research.update_niches_amazon_commission_rates(force=True)

        # Assert
        assert (
            niche_research.openai_api_client.get_amazon_commission_rate_for_niches.call_count
            == 5
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches.assert_any_call(
            niches[:50]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches.assert_any_call(
            niches[50:100]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches.assert_any_call(
            niches[100:150]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches.assert_any_call(
            niches[150:200]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches.assert_any_call(
            niches[200:]
        )

    def test_should_update_commission_rate_for_each_niche(
        self, niche_research: NicheResearch
    ):
        # Setup mocks
        commissions_fetched = [
            NicheAmazonCommission(
                niche="Cat toys", category="Pets", commission_rate=4.5
            ),
            NicheAmazonCommission(
                niche="Pasta makers", category="Kitchen", commission_rate=3
            ),
            NicheAmazonCommission(niche="Dog toys", category="Pets", commission_rate=4),
            NicheAmazonCommission(
                niche="Chef knives", category="Kitchen", commission_rate=2.5
            ),
        ]

        niche_research.niches_repository.get_all_niches_names = Mock(
            return_value=["Cat toys", "Pasta makers", "Dog toys", "Chef knives"]
        )
        niche_research.openai_api_client.get_amazon_commission_rate_for_niches = Mock(
            return_value=commissions_fetched
        )

        # Act
        niche_research.update_niches_amazon_commission_rates(force=True)

        # Assert
        niche_research.niches_repository.update_niches_amazon_commission_rates.assert_called_once_with(
            commissions_fetched
        )
