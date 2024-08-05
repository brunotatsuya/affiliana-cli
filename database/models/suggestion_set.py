import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from .suggestion_set_keyword import SuggestionSetKeyword

if TYPE_CHECKING:
    from .keyword import Keyword


class SuggestionSet(SQLModel, table=True):

    __tablename__ = "suggestion_sets"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword_id: int = Field(default=None, foreign_key="keywords.id")

    created_at: datetime.datetime

    keyword: "Keyword" = Relationship(back_populates="suggestion_sets")
    suggested_keywords: List["Keyword"] = Relationship(link_model=SuggestionSetKeyword)