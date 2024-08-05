import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .serp_analysis import SERPAnalysis


class SERPAnalysisItem(SQLModel, table=True):

    __tablename__ = "serp_analysis_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    serp_analysis_id: int = Field(default=None, foreign_key="serp_analyses.id")
    url: Optional[str] = None
    title: Optional[str] = None
    domain: Optional[str] = None
    position: Optional[int] = None
    type: Optional[str] = None
    clicks: Optional[int] = None
    domain_authority: Optional[int] = None
    facebook_shares: Optional[int] = None
    pinterest_shares: Optional[int] = None
    linkedin_shares: Optional[int] = None
    google_shares: Optional[int] = None
    reddit_shares: Optional[int] = None

    created_at: datetime.datetime

    analysis: "SERPAnalysis" = Relationship(back_populates="analysis_items")
