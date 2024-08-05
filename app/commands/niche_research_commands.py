from typing import Annotated
import inject
from monitoring import Logger, LogTypeEnum
from typer import Argument, Typer, Exit

from app.domain.niche_research import NicheResearch

niche_research_typer = Typer()


@niche_research_typer.command("perform")
def perform_command(
    niche: Annotated[str, Argument(help="The main niche to perform research on.")],
    subniche: Annotated[str, Argument(help="The subniche to perform research on.")],
):
    """Perform niche research for the given niche and subniche."""
    perform(niche, subniche)


@niche_research_typer.command("perform_from_file")
def perform_from_file_command(
    filepath: Annotated[
        str,
        Argument(help="The path to the file containing pairs of niche and subniche."),
    ]
):
    """
    Perform niche research based on pairs of niche and subniche provided in a file.
    """
    perform_from_file(filepath)


@inject.params(niche_research=NicheResearch)
def perform(niche: str, subniche: str, niche_research: NicheResearch):
    niche_research.fetch_data(niche, subniche)


@inject.params(niche_research=NicheResearch, logger=Logger)
def perform_from_file(filepath: str, niche_research: NicheResearch, logger: Logger):
    pairs = []
    try:
        with open(filepath, "r") as file:
            try:
                for line in file:
                    niche, subniche = line.strip().split(",")
                    pairs.append((niche, subniche))
            except:
                logger.notify(
                    "Invalid file format. Please provide a file with a pair of niche and subniche per line.",
                    LogTypeEnum.ERROR,
                )
                raise Exit(code=1)
    except FileNotFoundError:
        logger.notify(
            "File not found. Please provide a valid file path.", LogTypeEnum.ERROR
        )
        raise Exit(code=1)

    for niche, subniche in pairs:
        niche_research.fetch_data(niche, subniche)