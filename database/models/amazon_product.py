import datetime
from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel

from .niche_amazon_product import NicheAmazonProduct

if TYPE_CHECKING:
    from .niche import Niche


class AmazonProduct(SQLModel, table=True):

    __tablename__ = "amazon_products"

    asin: str = Field(primary_key=True)
    title: str
    price_usd: float
    rating: float
    reviews: int
    url: str
    seen_at: datetime.datetime

    niches: List["Niche"] = Relationship(
        back_populates="amazon_products", link_model=NicheAmazonProduct
    )
