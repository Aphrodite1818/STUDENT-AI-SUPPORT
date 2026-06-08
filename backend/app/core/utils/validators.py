#======================================#
#            validators.py             #
#======================================#
"""Reusable helpers for validating and normalizing application data."""



import re



def generate_slug(school_name: str) -> str:
    """Convert a school name into a URL-friendly slug."""
    slug = school_name.lower()
    
    slug = re.sub(r"[^\w\s-]", "", slug)   # remove special chars [^] not in 

    slug = re.sub(r"[\s_]+", "-", slug)     # spaces or underscores → hyphens + means one or more char in a row

    slug = re.sub(r"-+", "-", slug)         # collapse multiple hyphens

    return slug.strip("-")
