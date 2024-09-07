from typing import Annotated, Optional
import inject
from monitoring import Logger, LogTypeEnum
from typer import Argument, Typer, Exit

from app.domain import NicheResearch

niche_research_typer = Typer()


@niche_research_typer.command("perform")
def perform_command(
    niche: Annotated[str, Argument(help="The main niche to perform research on.")]
):
    """Perform niche research for the given niche."""
    perform(niche)


@niche_research_typer.command("perform_from_file")
def perform_from_file_command(
    filepath: Annotated[
        str,
        Argument(help="The path to the file containing a niche per line."),
    ]
):
    """
    Perform niche research based on niches provided in a file.
    """
    perform_from_file(filepath)


@niche_research_typer.command("perform_from_gpt_ideas")
def perform_from_gpt_ideas_command(
    iterations: Annotated[
        Optional[int],
        Argument(
            help="The number of times we want to reach GPT to get niche ideas. Every time we get 200 ideas."
        ),
    ] = 1
):
    """
    Perform niche research based on niches provided in a file.
    """
    perform_from_gpt_ideas(iterations)


@niche_research_typer.command("update_niches_amazon_commission_rates")
def update_niches_amazon_commission_rates_command(
    force: Annotated[
        Optional[bool],
        Argument(
            help="Force flag. If true, will update the commission rate for all niches on the database. If false, only those without a commission rate will be updated."
        ),
    ] = False
):
    """
    Update the Amazon commission rates for all niches.
    """
    update_niches_amazon_commission_rates(force)


@inject.params(niche_research=NicheResearch)
def perform(niche: str, niche_research: NicheResearch):
    niche_research.fetch_data(niche)


@inject.params(niche_research=NicheResearch, logger=Logger)
def perform_from_file(filepath: str, niche_research: NicheResearch, logger: Logger):
    niches = []
    try:
        with open(filepath, "r") as file:
            for line in file:
                niche = line.strip()
                niches.append(niche)
    except FileNotFoundError:
        logger.notify(
            "File not found. Please provide a valid file path.", LogTypeEnum.ERROR
        )
        raise Exit(code=1)

    for niche in niches:
        niche_research.fetch_data(niche)


@inject.params(niche_research=NicheResearch)
def update_niches_amazon_commission_rates(force: bool, niche_research: NicheResearch):
    niche_research.update_niches_amazon_commission_rates(force)


@inject.params(niche_research=NicheResearch)
def perform_from_gpt_ideas(iterations: int, niche_research: NicheResearch):
    niche_research.fetch_data_from_gpt_ideas(iterations)
