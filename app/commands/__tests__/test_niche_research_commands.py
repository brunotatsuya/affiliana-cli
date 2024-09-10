from pathlib import Path
from unittest.mock import call
import inject
import pytest
from typer import Exit

from app.commands.niche_research_commands import (
    perform,
    perform_from_file,
    update_niches_amazon_commission_rates,
)
from app.domain import NicheResearch


class TestNicheResearchCommands:

    @pytest.fixture
    def niche_research(self):
        return inject.instance(NicheResearch)

    def test_should_perform_niche_research_when_providing_niche(
        self, niche_research: NicheResearch
    ):
        perform("cat toys")
        niche_research.fetch_data.assert_called_with("cat toys")

    def test_should_perform_niche_research_for_each_niche_when_providing_valid_file(
        self, niche_research: NicheResearch
    ):
        perform_from_file(
            Path(__file__).resolve().parent / "filefixtures" / "valid_nichefile.txt"
        )
        niche_research.fetch_data.assert_has_calls(
            [call("cat toys"), call("dog toys"), call("fish food")]
        )

    def test_should_raise_exception_when_providing_non_existing_file(self):
        with pytest.raises(Exit):
            perform_from_file("non_existing_file.txt")

    def test_should_start_update_amazon_commission_rate_passing_force_flag(
        self, niche_research: NicheResearch
    ):
        update_niches_amazon_commission_rates(True)
        niche_research.update_niches_amazon_commission_rates.assert_called_with(True)
