from datetime import datetime, timezone

import pytest
from integrations.ubersuggest_api.formatters import (
    format_get_keyword_report,
    extract_and_filter_kws,
)


# Fixtures from conftest.py
def test_should_format_get_keyword_report_correctly_when_all_data_is_provided(
    keyword_info: dict,
    matching_keywords: dict,
    serp_analysis: dict,
    suggestions_report: dict,
):

    keyword_report = format_get_keyword_report(
        keyword_info, matching_keywords, serp_analysis, suggestions_report
    )

    # Check the keyword report info
    assert keyword_report.info.keyword == "cat toys"
    assert keyword_report.info.language == "en"
    assert keyword_report.info.loc_id == 2840
    assert keyword_report.info.competition == 1.0
    assert keyword_report.info.volume == 60500
    assert keyword_report.info.cpc == 1.31
    assert keyword_report.info.cpc_dollars == 1.31
    assert keyword_report.info.sd == 53
    assert keyword_report.info.type == "PRIMARY"
    assert keyword_report.info.updated_at == datetime(
        2024, 7, 4, 20, 49, 59, 0, timezone.utc
    )

    # Check the keyword report serp analysis
    assert keyword_report.serp_analysis.new_data == False
    assert keyword_report.serp_analysis.updated_at == datetime(2024, 1, 30)
    assert len(keyword_report.serp_analysis.serp_entries) == 100
    assert (
        keyword_report.serp_analysis.serp_entries[0].url
        == "http://www.chewy.com/b/toys-326"
    )
    assert (
        keyword_report.serp_analysis.serp_entries[0].title
        == "Cat Toys: Top Brands, Low Prices (Free Shipping)"
    )
    assert keyword_report.serp_analysis.serp_entries[0].domain == "chewy.com"
    assert keyword_report.serp_analysis.serp_entries[0].position == 1
    assert keyword_report.serp_analysis.serp_entries[0].type == "organic"
    assert keyword_report.serp_analysis.serp_entries[0].clicks == 17946
    assert keyword_report.serp_analysis.serp_entries[0].domain_authority == 75
    assert keyword_report.serp_analysis.serp_entries[0].facebook_shares == 172
    assert keyword_report.serp_analysis.serp_entries[0].pinterest_shares == 252
    assert keyword_report.serp_analysis.serp_entries[0].linkedin_shares == None
    assert keyword_report.serp_analysis.serp_entries[0].google_shares == None
    assert keyword_report.serp_analysis.serp_entries[0].reddit_shares == None
    assert (
        keyword_report.serp_analysis.serp_entries[-1].url
        == "http://books.google.com/books?dq=cat toys&hl=en&id=9FK5GiwivhMC&lpg=PA27&ots=QVgKNuzEtT&pg=PA27&sa=X&sig=ACfU3U1U7f0ND6rOVFtSjg4dybkR62_gyQ&source=bl&ved=2ahUKEwjY3cDIruuDAxXrxDgGHa-FBdsQ6AF6BQjTAxAD"
    )
    assert (
        keyword_report.serp_analysis.serp_entries[-1].title
        == "Cat Toys: How to Make Your Home a Feline Paradise"
    )
    assert keyword_report.serp_analysis.serp_entries[-1].domain == "books.google.com"
    assert keyword_report.serp_analysis.serp_entries[-1].position == 103
    assert keyword_report.serp_analysis.serp_entries[-1].type == "organic"
    assert keyword_report.serp_analysis.serp_entries[-1].clicks == None
    assert keyword_report.serp_analysis.serp_entries[-1].domain_authority == None
    assert keyword_report.serp_analysis.serp_entries[-1].facebook_shares == None
    assert keyword_report.serp_analysis.serp_entries[-1].pinterest_shares == None
    assert keyword_report.serp_analysis.serp_entries[-1].linkedin_shares == None
    assert keyword_report.serp_analysis.serp_entries[-1].google_shares == None
    assert keyword_report.serp_analysis.serp_entries[-1].reddit_shares == None

    # Check suggestions
    assert len(keyword_report.suggestions) == 65
    assert keyword_report.suggestions[0].keyword == "how make cat toys"
    assert keyword_report.suggestions[0].language == "en"
    assert keyword_report.suggestions[0].loc_id == 2840
    assert keyword_report.suggestions[0].competition == 0.29
    assert keyword_report.suggestions[0].volume == 720
    assert keyword_report.suggestions[0].cpc == 0.71
    assert keyword_report.suggestions[0].cpc_dollars == 0.71
    assert keyword_report.suggestions[0].sd == 27
    assert keyword_report.suggestions[0].pd == 28
    assert keyword_report.suggestions[0].type == "QUESTION"
    assert keyword_report.suggestions[0].updated_at == datetime(
        2023, 12, 26, 8, 29, 42, 0, timezone.utc
    )
    assert keyword_report.suggestions[-1].keyword == "plush cat toys"
    assert keyword_report.suggestions[-1].language == "en"
    assert keyword_report.suggestions[-1].loc_id == 2840
    assert keyword_report.suggestions[-1].competition == 0.99
    assert keyword_report.suggestions[-1].volume == 2900
    assert keyword_report.suggestions[-1].cpc == 0.8
    assert keyword_report.suggestions[-1].cpc_dollars == 0.8
    assert keyword_report.suggestions[-1].sd == 21
    assert keyword_report.suggestions[-1].pd == 99
    assert keyword_report.suggestions[-1].type == "MATCH"
    assert keyword_report.suggestions[-1].updated_at == datetime(
        2024, 7, 15, 19, 27, 32, 0, timezone.utc
    )


@pytest.mark.parametrize(
    ("takeout_prop", "target_dict"),
    [
        ("keyword", 'keyword_info["keywordInfo"]'),
        ("locId", "keyword_info"),
        ("competition", 'keyword_info["keywordInfo"]'),
        ("volume", 'keyword_info["keywordInfo"]'),
        ("cpc", 'keyword_info["keywordInfo"]'),
        ("cpcDollars", 'keyword_info["keywordInfo"]'),
        ("sd", 'keyword_info["keywordInfo"]'),
        ("pd", 'keyword_info["keywordInfo"]'),
        ("updated_at", 'keyword_info["keywordInfo"]'),
        ("newData", "serp_analysis"),
        ("updated_at", "serp_analysis"),
        ("serpEntries", "serp_analysis"),
        ("report", "suggestions_report"),
        ("questions", 'suggestions_report["report"]'),
        ("prepositions", 'suggestions_report["report"]'),
        ("comparisons", 'suggestions_report["report"]'),
        ("suggestions", 'suggestions_report["report"]'),
        ("suggestions", "matching_keywords"),
        ("keywords", 'suggestions_report["report"]["questions"]'),
        ("keywords", 'suggestions_report["report"]["prepositions"]'),
        ("keywords", 'suggestions_report["report"]["comparisons"]'),
        ("keywords", 'suggestions_report["report"]["suggestions"]'),
    ],
)
def test_should_raise_exception_if_any_data_is_missing(
    takeout_prop: str,
    target_dict: str,
    keyword_info: dict,
    matching_keywords: dict,
    serp_analysis: dict,
    suggestions_report: dict,
):
    eval(f"{target_dict}.pop('{takeout_prop}')")
    with pytest.raises(Exception):
        format_get_keyword_report(
            keyword_info, matching_keywords, serp_analysis, suggestions_report
        )


def test_should_filter_out_suggestion_keywords_without_volume(suggestions_report: dict):
    suggestion_keywords = suggestions_report["report"]["questions"]["keywords"]

    filtered_keywords = extract_and_filter_kws(
        suggestion_keywords, "en", 2840, "QUESTION"
    )

    assert len(filtered_keywords) == 5
