def format_niche_name(name: str) -> str:
    """
    Formats the niche name by removing any special characters and spaces.

    Args:
        name (str): The name of the niche to format.

    Returns:
        str: The formatted niche name.
    """
    use_space_for = ["-"]
    for char in use_space_for:
        name = name.replace(char, " ")
    return name.lower()
