from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class TypedKeyword(BaseModel):
    keyword: str
    type: str

class KeywordInfo(BaseModel):
    keyword: str
    language: str
    loc_id: int
    competition: float
    volume: int
    cpc: float
    cpc_dollars: float
    sd: int
    pd: int
    type: str
    updated_at: datetime

class KeywordSERPEntry(BaseModel):
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

class KeywordSERPAnalysis(BaseModel):
    serp_entries: List[KeywordSERPEntry]
    new_data: bool
    updated_at: datetime

class KeywordReport(BaseModel):
    info: KeywordInfo
    serp_analysis: KeywordSERPAnalysis
    suggestions: List[KeywordInfo]