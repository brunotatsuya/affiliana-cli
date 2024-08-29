from bs4 import BeautifulSoup
from functional import seq

from app.exceptions import DataFormatError
from app.interfaces.dtos.amazon_product_snapshot import AmazonProductSnapshot


def format_search(html: str) -> list[AmazonProductSnapshot]:
    """
    Extracts product information from HTML and returns a list of dictionaries.

    Args:
        html (str): The HTML content to extract product information from.

    Returns:
        products (List[AmazonProductSnapshot]): A list of products snapshots containing product information at that moment.

    Raises:
        DataFormatError: If there is an error while extracting data from the HTML.
    """
    products = []

    try:
        soup = BeautifulSoup(html, features="html.parser")
        # Get all divs that have "data-asin" attribute
        html_products = soup.find_all("div", {"data-asin": True})
        # Filter out products that have "data-asin" attribute equal to ""
        html_products = [p for p in html_products if p["data-asin"]]
        # Loop through each product and extract the that
        for p in html_products:
            p_data = {}

            p_data["asin"] = p["data-asin"]

            # For the title, find a div that have the "data-cy" attribute equal to "title-recipe"
            # Then find the first "h2" tag, and inside of it, the first "span" tag. Its inner text is the title
            title_recipe_div = p.find("div", {"data-cy": "title-recipe"})
            p_data["title"] = title_recipe_div.find("h2").find("span").text
            # Try to find a div that have "a-row a-spacing-micro" class
            # If this div is found, then the product is sponsored
            p_data["is_sponsored"] = (
                title_recipe_div.find("div", {"class": "a-row a-spacing-micro"})
                is not None
            )

            # For the price, find a div that have the "data-cy" attribute equal to "price-recipe"
            # Then find the first "span" tag that have the "a-price-whole" class. Its inner text is integer part of the price
            # If there is a "a-price-fraction" class, then there is a decimal part of the price
            price_recipe_div = p.find("div", {"data-cy": "price-recipe"})
            price_span = price_recipe_div.find("span", {"class": "a-price-whole"})
            if not price_span:
                continue
            price = float(price_span.text)
            price_fraction = price_recipe_div.find(
                "span", {"class": "a-price-fraction"}
            )
            if price_fraction:
                price += float(price_fraction.text) / 100
            p_data["price_usd"] = price

            # For the rating, find a div that have the "data-cy" attribute equal to "reviews-block"
            # Then find the first "span" tag that has the aria-label attribute. Its value is the rating in a string format
            reviews_block_div = p.find("div", {"data-cy": "reviews-block"})
            if reviews_block_div:
                p_data["rating"] = float(
                    reviews_block_div.find("span", {"aria-label": True})[
                        "aria-label"
                    ].split(" ")[0]
                )

                # For the reviews, find the last "span" tag that contains "a-size-base s-underline-text" class within the reviews_block_div. Its inner text is a number with commas that contains the number of reviews
                reviews_data = reviews_block_div.find_all(
                    "span", {"class": "a-size-base s-underline-text"}
                )
                if not reviews_data:
                    continue
                p_data["reviews"] = int(reviews_data[-1].text.replace(",", ""))

                # For the bought last month, find the last "span" tag within the reviews_block_div. Its inner text is a string that contains the number of bought last month
                bought_last_month = reviews_block_div.find_all("span")[-1].text.split(
                    " "
                )[0]
                # We have to convert "K" to "000" and "M" to "000000"
                bought_last_month = bought_last_month.replace("K", "000").replace(
                    "M", "000000"
                )
                # Then we have to remove all non-numeric characters from the string
                p_data["bought_last_month"] = int(
                    "".join(filter(str.isdigit, bought_last_month))
                )

            products.append(p_data)

        # Remove duplicates using asin key, keep the first occurrence
        products = {p["asin"]: p for p in list(reversed(products))}.values()
        return seq(products).map(AmazonProductSnapshot.model_validate).to_list()
    except Exception as e:
        raise DataFormatError(f"Failed to extract data from HTML: {e}")
