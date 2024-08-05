import datetime
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .keyword import Keyword


class MetricsReport(SQLModel, table=True):

    __tablename__ = "metrics_reports"

    id: Optional[int] = Field(default=None, primary_key=True)
    keyword_id: int = Field(default=None, foreign_key="keywords.id")
    competition: float
    volume: int
    cpc: float
    cpc_dollars: float
    sd: int
    pd: int

    created_at: datetime.datetime

    keyword: "Keyword" = Relationship(back_populates="metrics_reports")
