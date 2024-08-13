import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from .niche_keyword import NicheKeyword


if TYPE_CHECKING:
    from .keyword import Keyword


class Niche(SQLModel, table=True):

    __tablename__ = "niches"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str

    created_at: datetime.datetime

    keywords: List["Keyword"] = Relationship(
        back_populates="niches", link_model=NicheKeyword
    )
