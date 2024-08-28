from unittest.mock import Mock, patch
import pytest

from integrations.openai_api.client import OpenAIApiClient


class TestOpenAIApiClient:

    @pytest.fixture(scope="class")
    def openai_api_client(self):
        with patch("integrations.openai_api.client.OpenAI"):
            return OpenAIApiClient()

    def test_should_create_openai_library_client_on_init(
        self, openai_api_client: OpenAIApiClient
    ):
        assert openai_api_client.client is not None

    def test_should_make_a_single_transaction_using_openai_api(
        self, openai_api_client: OpenAIApiClient
    ):
        openai_api_client.client.chat.completions.create = Mock()

        openai_api_client._OpenAIApiClient__make_single_interaction("prompt")

        openai_api_client.client.chat.completions.create.assert_called_once_with(
            messages=[{"role": "user", "content": "prompt"}], model="gpt-4o-mini"
        )

    def test_should_construct_prompt_correctly_when_getting_amazon_commission_rate_for_niches(
        self, openai_api_client: OpenAIApiClient
    ):
        niches = ["niche1", "niche2"]

        openai_api_client._OpenAIApiClient__make_single_interaction = Mock()
        openai_api_client._OpenAIApiClient__make_single_interaction.return_value.choices = [
            Mock(message=Mock(content="0A,1B"))
        ]

        openai_api_client.get_amazon_commission_rate_for_niches(niches)

        openai_api_client._OpenAIApiClient__make_single_interaction.assert_called_once_with(
            prompt=(
                "A. Physical Books, Kitchen, Automotive"
                + "\nB. Apparel, Jewelry, Luggage, Shoes, Watches, Ring Devices, Handbags, Accessories"
                + "\nC. Toys, Furniture, Home, Home Improvement, Pets, Beauty, Musical Instruments, Outdoors, Tools, Sports, Baby"
                + "\nD. PC Components"
                + "\nE. Any other product"
                + "\n\nGiven the table above, classify the following products below:"
                + "\n0. niche1"
                + "\n1. niche2"
                + "\n\nYour response should be given in the following format: 0A,1B..."
            )
        )

    def test_should_format_response_when_getting_amazon_commission_rate_for_niches(
        self, openai_api_client: OpenAIApiClient
    ):
        openai_api_client._OpenAIApiClient__make_single_interaction = Mock()
        openai_api_client._OpenAIApiClient__make_single_interaction.return_value.choices = [
            Mock(message=Mock(content="0A,1B"))
        ]

        with patch(
            "integrations.openai_api.client.format_get_amazon_commission_rate_for_niches"
        ) as format_get_amazon_commission_rate_for_niches:
            openai_api_client.get_amazon_commission_rate_for_niches(
                ["niche1", "niche2"]
            )
            format_get_amazon_commission_rate_for_niches.assert_called_once_with(
                openai_response="0A,1B", prompted_niches=["niche1", "niche2"]
            )
