from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AmazonProductSnapshot(BaseModel):
    asin: str
    title: str
    is_sponsored: bool
    price_usd: float
    rating: Optional[float] = None
    reviews: Optional[int] = None
    bought_last_month: Optional[int] = None
    seen_at: Optional[datetime] = datetime.now()
