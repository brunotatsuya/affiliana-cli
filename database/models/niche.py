import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from .niche_amazon_product import NicheAmazonProduct
from .niche_keyword import NicheKeyword


if TYPE_CHECKING:
    from .keyword import Keyword
    from .amazon_product import AmazonProduct


class Niche(SQLModel, table=True):

    __tablename__ = "niches"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    amazon_commission_rate: Optional[float]

    created_at: datetime.datetime

    keywords: List["Keyword"] = Relationship(
        back_populates="niches", link_model=NicheKeyword
    )

    amazon_products: List["AmazonProduct"] = Relationship(
        back_populates="niches", link_model=NicheAmazonProduct
    )
