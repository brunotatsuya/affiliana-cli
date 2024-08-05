import json
from pathlib import Path
import pytest

webfixtures_folder = Path(__file__).resolve().parent / "webfixtures"


@pytest.fixture
def search() -> dict:
    with open(webfixtures_folder / "search.json", "r") as file:
        keyword_info = json.load(file)
    return keyword_info
