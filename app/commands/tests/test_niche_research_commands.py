from pathlib import Path
from unittest.mock import MagicMock
import inject
import pytest
from typer import Exit

from app.commands.niche_research_commands import perform, perform_from_file
from app.domain.niche_research import NicheResearch


class TestNicheResearchCommands:

    @pytest.fixture
    def niche_research(self):
        return inject.instance(NicheResearch)

    def test_should_perform_niche_research_when_providing_niche_and_subniche(
        self, niche_research: NicheResearch
    ):
        perform("cats", "cat toys")
        assert niche_research.fetch_data.called_with("cats", "cat toys")

    def test_should_perform_niche_research_for_each_niche_and_subniche_pair_when_providing_valid_file(
        self, niche_research: NicheResearch
    ):
        perform_from_file(
            Path(__file__).resolve().parent / "filefixtures" / "valid_nichefile.txt"
        )
        assert niche_research.fetch_data.called_with("cats", "cat toys")
        assert niche_research.fetch_data.called_with("dogs", "dog toys")
        assert niche_research.fetch_data.called_with("fish", "fish food")

    def test_should_raise_exception_when_providing_non_existing_file(self):
        with pytest.raises(Exit):
            perform_from_file("non_existing_file.txt")

    def test_should_raise_exception_when_providing_invalid_file_format(self):
        with pytest.raises(Exit):
            perform_from_file(
                Path(__file__).resolve().parent
                / "filefixtures"
                / "invalid_nichefile.txt",
                logger=MagicMock(),
            )
