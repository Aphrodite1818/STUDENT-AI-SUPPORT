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


def validate_password_strength(password: str) -> None:
    """Enforce a minimum password baseline for first-login password changes."""

    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long")

    if password.lower() == password or password.upper() == password:
        raise ValueError("Password must include both uppercase and lowercase letters")

    if not re.search(r"\d", password):
        raise ValueError("Password must include at least one number")
