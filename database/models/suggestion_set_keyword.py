from typing import Optional
from sqlmodel import Field, SQLModel


class SuggestionSetKeyword(SQLModel, table=True):

    __tablename__ = "suggestion_sets_keywords"

    suggestion_set_id: Optional[int] = Field(
        default=None, foreign_key="suggestion_sets.id", primary_key=True
    )
    keyword_id: Optional[int] = Field(
        default=None, foreign_key="keywords.id", primary_key=True
    )
