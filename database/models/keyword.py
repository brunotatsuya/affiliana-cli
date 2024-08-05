import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

from .niche_keyword import NicheKeyword

from .suggestion_set import SuggestionSet

if TYPE_CHECKING:
    from .niche import Niche
    from .metrics_report import MetricsReport
    from .serp_analysis import SERPAnalysis


class KeywordTypeEnum(Enum):
    PRIMARY = "PRIMARY"
    SUGGESTION = "SUGGESTION"
    MATCH = "MATCH"


class Keyword(SQLModel, table=True):

    __tablename__ = "keywords"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str
    language: str
    loc_id: int
    type: Optional[KeywordTypeEnum] = None

    created_at: datetime.datetime

    niches: List["Niche"] = Relationship(
        back_populates="keywords", link_model=NicheKeyword
    )
    metrics_reports: List["MetricsReport"] = Relationship(back_populates="keyword")
    serp_analyses: List["SERPAnalysis"] = Relationship(back_populates="keyword")
    suggestion_sets: List["SuggestionSet"] = Relationship(back_populates="keyword")
