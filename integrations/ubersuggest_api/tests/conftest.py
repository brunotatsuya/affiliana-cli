import json
from pathlib import Path
import pytest

webfixtures_folder = Path(__file__).resolve().parent / "webfixtures"


@pytest.fixture
def keyword_info() -> dict:
    with open(webfixtures_folder / "keyword_info.json", "r") as file:
        keyword_info = json.load(file)
    return keyword_info


@pytest.fixture
def matching_keywords() -> dict:
    with open(webfixtures_folder / "match_keywords.json", "r") as file:
        matching_keywords = json.load(file)
    return matching_keywords


@pytest.fixture
def serp_analysis() -> dict:
    with open(webfixtures_folder / "serp_analysis.json", "r") as file:
        serp_analysis = json.load(file)
    return serp_analysis


@pytest.fixture
def suggestions_report() -> dict:
    with open(
        webfixtures_folder / "keyword_suggestions_info_task_status.json", "r"
    ) as file:
        suggestions = json.load(file)
    return suggestions
