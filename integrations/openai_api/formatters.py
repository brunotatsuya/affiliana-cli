from typing import List
from app.exceptions import DataFormatError
from app.interfaces.dtos.niche_amazon_commission import NicheAmazonCommission
from integrations.openai_api.constants import AMAZON_COMMISSION_TABLE


def format_get_amazon_commission_rate_for_niches(
    openai_response: str, prompted_niches: List[str]
) -> List[NicheAmazonCommission]:
    """
    Format the OpenAI response to retrieve commission rates for prompted niches.

    Args:
        openai_response (str): The OpenAI response containing the classifications.
        prompted_niches (List[str]): The list of prompted niches.

    Returns:
        List[NicheAmazonCommission]: A list of the classified niches
        with their respective commission rates.

    Raises:
        DataFormatError: If there is an error formatting the OpenAI response.
    """

    try:
        classifications = [idxs[-1] for idxs in openai_response.split(",")]
        products_classifications = []
        for idx, classification in enumerate(classifications):
            amazon_category = next(
                ac for ac in AMAZON_COMMISSION_TABLE if ac["index"] == classification
            )
            products_classifications.append(
                NicheAmazonCommission.model_validate(
                    {
                        "niche": prompted_niches[idx],
                        "category": amazon_category["category"],
                        "commission_rate": amazon_category["commission_rate"],
                    }
                )
            )
        return products_classifications
    except Exception as e:
        raise DataFormatError(f"Error formatting OpenAI response: {e}")
