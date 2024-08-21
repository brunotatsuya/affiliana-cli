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
def domain_counts() -> dict:
    with open(webfixtures_folder / "domain_counts.json", "r") as file:
        domain_counts = json.load(file)
    return domain_counts