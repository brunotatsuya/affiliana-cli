from datetime import datetime
import pytest

from app.interfaces.dtos.amazon_product_snapshot import AmazonProductSnapshot
from app.interfaces.dtos.keyword_report import KeywordReport


@pytest.fixture
def keyword_report():
    return KeywordReport.model_validate(
        {
            "info": {
                "keyword": "test keyword",
                "language": "en",
                "loc_id": 2840,
                "competition": 0.5,
                "volume": 1000,
                "cpc": 0.5,
                "cpc_dollars": 0.5,
                "sd": 100,
                "pd": 100,
                "type": "PRIMARY",
                "updated_at": "2021-01-01T00:00:00",
            },
            "serp_analysis": {
                "serp_entries": [
                    {
                        "url": "https://example.com",
                        "title": "Example",
                        "domain": "example.com",
                        "position": 1,
                        "type": "organic",
                        "clicks": 100,
                        "domain_authority": 50,
                        "facebook_shares": 100,
                        "pinterest_shares": 100,
                        "linkedin_shares": 100,
                        "google_shares": 100,
                        "reddit_shares": 100,
                    },
                    {
                        "url": "https://example2.com",
                        "title": "Example2",
                        "domain": "example2.com",
                        "position": 2,
                        "type": "organic",
                        "clicks": 101,
                        "domain_authority": 51,
                        "facebook_shares": 101,
                        "pinterest_shares": 101,
                        "linkedin_shares": 101,
                        "google_shares": 101,
                        "reddit_shares": 101,
                    },
                ],
                "new_data": True,
                "updated_at": "2021-01-01T00:00:00",
            },
            "suggestions": [
                {
                    "keyword": "match suggestion 1",
                    "language": "en",
                    "loc_id": 2840,
                    "competition": 0.5,
                    "volume": 1000,
                    "cpc": 0.5,
                    "cpc_dollars": 0.5,
                    "sd": 100,
                    "pd": 100,
                    "type": "MATCH",
                    "updated_at": "2021-01-01T00:00:00",
                },
                {
                    "keyword": "match suggestion 2",
                    "language": "en",
                    "loc_id": 2840,
                    "competition": 0.5,
                    "volume": 1000,
                    "cpc": 0.5,
                    "cpc_dollars": 0.5,
                    "sd": 100,
                    "pd": 100,
                    "type": "MATCH",
                    "updated_at": "2021-01-01T00:00:00",
                },
                {
                    "keyword": "match suggestion 3",
                    "language": "en",
                    "loc_id": 2840,
                    "competition": 0.5,
                    "volume": 1000,
                    "cpc": 0.5,
                    "cpc_dollars": 0.5,
                    "sd": 100,
                    "pd": 100,
                    "type": "MATCH",
                    "updated_at": "2021-01-01T00:00:00",
                },
            ],
        }
    )

@pytest.fixture
def amazon_product_snapshot():
    return AmazonProductSnapshot.model_validate(
        {
            "asin": "B07H8L85PS",
            "title": "Test Product",
            "is_sponsored": True,
            "price_usd": 100.0,
            "rating": 4.5,
            "reviews": 1000,
            "bought_last_month": 1000,
            "seen_at": datetime(2021, 1, 1),
        }
    )