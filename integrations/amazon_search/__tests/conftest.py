from pathlib import Path
import pytest

webfixtures_folder = Path(__file__).resolve().parent / "webfixtures"

@pytest.fixture(scope="module")
def amazon_search() -> dict:
    with open(webfixtures_folder / "amazon_search.html", "r") as file:
        amazon_search = file.read()
    return amazon_search