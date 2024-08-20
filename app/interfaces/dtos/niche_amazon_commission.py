from pydantic import BaseModel


class NicheAmazonCommission(BaseModel):
    niche: str
    category: str
    commission_rate: float
