#======================================#
#            validators.py             #
#======================================#
"""this file contains reusable functions for handling and validating specific data formats"""



import re



def generate_slug(school_name: str) -> str:
    """GENERATES A URL-FRIENDLY SLUG FROM A SCHOOL NAME

    input : must be a string, e.g. "Greenfield Lagos"

    output: a URL-friendly slug, e.g. "greenfield-lagos"

    how it works:
    1. lowercases the string
    2. removes special characters (anything that's not a word char, space, or hyphen)
    3. replaces spaces and underscores with hyphens
    4. collapses multiple hyphens into one
    5. trims leading/trailing hyphens
    """
    slug = school_name.lower()
    
    slug = re.sub(r"[^\w\s-]", "", slug)   # remove special chars [^] not in 

    slug = re.sub(r"[\s_]+", "-", slug)     # spaces or underscores → hyphens + means one or more char in a row

    slug = re.sub(r"-+", "-", slug)         # collapse multiple hyphens

    return slug.strip("-")