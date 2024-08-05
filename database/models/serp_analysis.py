import datetime
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .keyword import Keyword
    from .serp_analysis_item import SERPAnalysisItem


class SERPAnalysis(SQLModel, table=True):

    __tablename__ = "serp_analyses"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword_id: int = Field(default=None, foreign_key="keywords.id")

    created_at: datetime.datetime

    keyword: "Keyword" = Relationship(back_populates="serp_analyses")
    analysis_items: List["SERPAnalysisItem"] = Relationship(back_populates="analysis")
