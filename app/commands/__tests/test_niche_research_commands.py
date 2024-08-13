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

    def test_should_perform_niche_research_when_providing_niche(
        self, niche_research: NicheResearch
    ):
        perform("cat toys")
        assert niche_research.fetch_data.called_with("cat toys")

    def test_should_perform_niche_research_for_each_niche_when_providing_valid_file(
        self, niche_research: NicheResearch
    ):
        perform_from_file(
            Path(__file__).resolve().parent / "filefixtures" / "valid_nichefile.txt"
        )
        assert niche_research.fetch_data.called_with("cat toys")
        assert niche_research.fetch_data.called_with("dog toys")
        assert niche_research.fetch_data.called_with("fish food")

    def test_should_raise_exception_when_providing_non_existing_file(self):
        with pytest.raises(Exit):
            perform_from_file("non_existing_file.txt")