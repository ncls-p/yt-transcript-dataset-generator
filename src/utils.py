"""General text utilities for the project."""


def sanitize_transcript(text: str) -> str:
    """
    Remove line breaks and excessive whitespace from transcript text.
    """
    if not text:
        return ""
    return " ".join(text.split())
