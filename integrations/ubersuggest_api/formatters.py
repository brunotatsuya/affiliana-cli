from datetime import datetime
from typing import List, Optional
from functional import seq

from app.interfaces.dtos.keyword_report import KeywordReport


from typing import List
from datetime import datetime


def extract_and_filter_kws(kws_list: List, language: str, loc_id: int, tp: str):
    """
    Extracts and filters keyword information from a list of keyword info dictionaries.

    Args:
        kws_list (List): A list of keyword info dictionaries.
        language (str): The language of the keywords.
        loc_id (int): The location ID.
        tp (str): The type of keywords.

    Returns:
        List: A list of filtered keyword info dictionaries with correct key names and added fields.

    """
    return (
        seq(kws_list)
        .filter(lambda kw_info: "volume" in kw_info)
        .map(
            lambda s: s
            | {
                "language": language,
                "loc_id": loc_id,
                "type": tp,
                "cpc_dollars": s["cpcDollars"],
                "updated_at": s["updated_at"] if s["updated_at"] else datetime.now(),
            }
        )
        .to_list()
    )


def extract_serp_entries(serp_entries: List) -> List:
    """
    Extracts SERP data from a list of SERP entries.

    Args:
        serp_entries (List): A list of SERP entries.

    Returns:
        List: A list of SERP entries with correct key names.

    """
    return (
        seq(serp_entries)
        .map(
            lambda e: e
            | {
                "domain_authority": (
                    e.get("domainAuthority") if e.get("domainAuthority") else None
                ),
                "facebook_shares": (
                    e.get("facebookShares") if e.get("facebookShares") else None
                ),
                "pinterest_shares": (
                    e.get("pinterestShares") if e.get("pinterestShares") else None
                ),
                "linkedin_shares": (
                    e.get("linkedinShares") if e.get("linkedinShares") else None
                ),
                "google_shares": (
                    e.get("googleShares") if e.get("googleShares") else None
                ),
                "reddit_shares": (
                    e.get("redditShares") if e.get("redditShares") else None
                ),
            }
        )
        .to_list()
    )


def format_get_keyword_report(
    keyword_info: dict,
    matching_keywords: dict,
    serp_analysis: dict,
    suggestions_report: Optional[dict],
    language: str,
    loc_id: int,
) -> KeywordReport:
    """
    Formats the keyword report data.

    Args:
        keyword_info (dict): Information about the keyword.
        matching_keywords (dict): Matching keywords.
        serp_analysis (dict): SERP (Search Engine Results Page) analysis data.
        suggestions_report (dict, optional): Suggestions report for the keyword.~
        language (str): The language of the keywords.
        loc_id (int): The location ID.

    Returns:
        KeywordReport: The formatted keyword report.

    """
    all_suggestions = extract_and_filter_kws(
        matching_keywords["suggestions"], language, loc_id, "MATCH"
    )

    suggestions = suggestions_report["report"] if suggestions_report else None

    if suggestions:
        all_suggestions += extract_and_filter_kws(
            suggestions["suggestions"]["keywords"], language, loc_id, "SUGGESTION"
        )

    serp_entries = extract_serp_entries(serp_analysis["serpEntries"])

    formatted_data = {
        "info": {
            "keyword": keyword_info["keywordInfo"]["keyword"],
            "language": language,
            "loc_id": loc_id,
            "competition": keyword_info["keywordInfo"]["competition"],
            "volume": keyword_info["keywordInfo"]["volume"],
            "cpc": keyword_info["keywordInfo"]["cpc"],
            "cpc_dollars": keyword_info["keywordInfo"]["cpcDollars"],
            "sd": keyword_info["keywordInfo"]["sd"],
            "pd": keyword_info["keywordInfo"]["pd"],
            "type": "PRIMARY",
            "updated_at": (
                keyword_info["keywordInfo"]["updated_at"]
                if keyword_info["keywordInfo"]["updated_at"]
                else datetime.now()
            ),
        },
        "serp_analysis": {
            "new_data": serp_analysis["newData"],
            "updated_at": serp_analysis["updated_at"],
            "serp_entries": serp_entries,
        },
        "suggestions": all_suggestions,
    }

    return KeywordReport.model_validate(formatted_data)
