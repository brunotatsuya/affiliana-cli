from typing import Optional
from sqlmodel import Field, SQLModel


class NicheKeyword(SQLModel, table=True):

    __tablename__ = "niches_keywords"

    niche_id: Optional[int] = Field(
        default=None, foreign_key="niches.id", primary_key=True
    )
    keyword_id: Optional[int] = Field(
        default=None, foreign_key="keywords.id", primary_key=True
    )
