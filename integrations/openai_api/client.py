import inject
from typing import List
from openai import OpenAI
from openai.types.chat import ChatCompletion

from app.interfaces.dtos.niche_amazon_commission import NicheAmazonCommission
from config.config import Config
from integrations.openai_api.constants import AMAZON_COMMISSION_TABLE, DEFAULT_MODEL
from integrations.openai_api.formatters import (
    format_get_amazon_commission_rate_for_niches,
    format_get_niche_ideas,
)


class OpenAIApiClient:
    """
    A client for interacting with the OpenAI API.
    """

    @inject.autoparams()
    def __init__(self, config: Config):
        self.config = config
        self.client = self.__create_client()

    def __create_client(self) -> OpenAI:
        """
        Creates an OpenAI library client instance.

        Returns:
            OpenAI: An OpenAI library client instance.
        """
        return OpenAI(api_key=self.config.OPENAI_API_KEY)

    def __make_single_interaction(self, prompt: str) -> ChatCompletion:
        """
        Makes a single interaction with the OpenAI API.

        Args:
            prompt (str): The prompt to send to the API, as of the user POV.

        Returns:
            ChatCompletion: The response from the API.
        """

        return self.client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}], model=DEFAULT_MODEL
        )

    def get_niche_ideas(self) -> List[str]:
        """
        Leverage AI to generate niche ideas.

        Returns:
            List[str]: A list of niche ideas.
        """

        prompt = (
            "Present 200 niches, respecting the following requirements:"
            + "\n1. The niche should be attractive on the United States so you can construct an affiliate business through a blog website ranked organically on Google."
            + "\n2. The niche should be low competitive. It is expected to be relatively easy to rank on Google search through SEO organically."
            + "\n3. The niche cannot be seasonal and should have good longevity."
            + "\n4. The niche should not evolve fast, meaning, should not be frequently updated."
            + "\n5. The volume for organic traffic considering buy intent keywords should be between 1k and 10k per month."
            + "\n6. The products to sell as an affiliate should be something you can buy in Amazon, but above the 100 dollars."
            + "\n\nDo not use 'for' specific audience or other qualifier/adjectives like 'high-end', 'luxury', 'high-quality', etc. Keep it clean."
            + "\nYour response should be given in a single string in the format: niche1,niche2,niche3,..."
        )

        response = self.__make_single_interaction(prompt=prompt)
        
        return format_get_niche_ideas(openai_response=response.choices[0].message.content)

    def get_amazon_commission_rate_for_niches(
        self, niches: List[str]
    ) -> List[NicheAmazonCommission]:
        """
        Leverage AI to classify a niche on amazon categories and return the commission rate.

        Args:
            niches (List[str]): A list of niches.

        Returns:
            List[NicheAmazonCommission]: A list of the classified niches
            with their respective commission rates.
        """

        amazon_categories_prompt_table = "\n".join(
            [
                f"{category['index']}. {category['category']}"
                for category in AMAZON_COMMISSION_TABLE
            ]
        )

        prompt = (
            f"{amazon_categories_prompt_table}"
            + "\n\nGiven the table above, classify the following products below:"
            + "\n"
            + "\n".join([f"{number}. {n}" for (number, n) in enumerate(niches)])
            + "\n\nYour response should be given in the following format: 0A,1B..."
        )

        response = self.__make_single_interaction(prompt=prompt)

        return format_get_amazon_commission_rate_for_niches(
            openai_response=response.choices[0].message.content, prompted_niches=niches
        )
