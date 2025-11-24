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
    Filters recipes by cuisine tag. Treats common "all"/"any" selections as no filter.
    """
    if cuisine is None:
        return df

    normalized = cuisine.strip().lower()
    if normalized in {"", "all", "all cuisines", "all cuisine", "any", "any cuisine", "none"}:
        return df

    return df[df["tags"].str.contains(normalized, case=False, na=False)]



def filter_by_time(df, max_minutes):
    """
    Keep recipes that can be cooked within max_minutes
    """
    if not max_minutes:
        return df
    return df[df["minutes"] <= max_minutes]
