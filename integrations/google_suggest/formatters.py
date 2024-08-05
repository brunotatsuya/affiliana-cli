from typing import List


def format_get_suggestions(data: List) -> List[str]:
    """
    Formats the data returned by the get_suggestions function.

    Args:
        data (List): The data returned by the get_suggestions function.

    Returns:
        List[str]: The formatted suggestions extracted from the data.

    """
    return data[1]
