def filter_by_diet(df, allowed_tags):
    """
    Keeps recipes that contain ANY of the allowed dietary tags.
    allowed_tags: list of dietary tags (e.g., ["vegetarian", "vegan"])
    """
    if not allowed_tags:
        return df
    return df[df["tags"].str.contains("|".join(allowed_tags), case=False, na=False)]


def filter_by_cuisine(df, cuisine):
    """
    Keeps recipes whose tags match the desired cuisine.
    Example: cuisine="indian"
    """
    if not cuisine:
        return df
    return df[df["tags"].str.contains(cuisine, case=False, na=False)]


def filter_by_time(df, max_minutes):
    """
    Keep recipes that can be cooked within max_minutes
    """
    if not max_minutes:
        return df
    return df[df["minutes"] <= max_minutes]
