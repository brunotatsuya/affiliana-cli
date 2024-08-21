from datetime import datetime
from typing import List
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


def extract_serp_entries(serp_entries: List, domains_metrics: dict) -> List:
    """
    Extracts SERP data from a list of SERP entries.

    Args:
        serp_entries (List): A list of SERP entries.
        domains_metrics (dict): A dict containing metrics data for domains.

    Returns:
        List: A list of SERP entries with correct key names.

    """
    extracted_entries = []

    for entry in serp_entries:
        domain_metrics_for_url = domains_metrics.get(entry["url"])

        domain_metrics_for_entry = (
            {
                "backlinks": domain_metrics_for_url["backlinks"],
                "referring_domains": domain_metrics_for_url["refdomains"],
                "nofollow_backlinks": domain_metrics_for_url["nofollow_backlinks"],
                "dofollow_backlinks": domain_metrics_for_url["dofollow_backlinks"],
            }
            if domain_metrics_for_url
            else {}
        )

        extracted_entries.append(
            entry
            | domain_metrics_for_entry
            | {
                "domain_authority": entry.get("domainAuthority") or None,
                "facebook_shares": entry.get("facebookShares") or None,
                "pinterest_shares": entry.get("pinterestShares") or None,
                "linkedin_shares": entry.get("linkedinShares") or None,
                "google_shares": entry.get("googleShares") or None,
                "reddit_shares": entry.get("redditShares") or None,
            }
        )

    return extracted_entries


def format_get_keyword_report(
    keyword_info: dict,
    matching_keywords: dict,
    serp_analysis: dict,
    domain_counts: dict,
    language: str,
    loc_id: int,
) -> KeywordReport:
    """
    Formats the keyword report data.

    Args:
        keyword_info (dict): Information about the keyword.
        matching_keywords (dict): Matching keywords.
        serp_analysis (dict): SERP (Search Engine Results Page) analysis data.
        domain_counts (dict): Count data for domains.
        language (str): The language of the keywords.
        loc_id (int): The location ID.

    Returns:
        KeywordReport: The formatted keyword report.

    """
    match_suggestions = extract_and_filter_kws(
        matching_keywords["suggestions"], language, loc_id, "MATCH"
    )

    serp_entries = extract_serp_entries(
        serp_analysis["serpEntries"], domain_counts["domain_data"]
    )

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
        "suggestions": match_suggestions,
    }

    return KeywordReport.model_validate(formatted_data)
