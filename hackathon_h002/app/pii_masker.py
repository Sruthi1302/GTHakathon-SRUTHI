import re


PHONE_REGEX = re.compile(r"\b\d{10}\b")
EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
ADDRESS_REGEX = re.compile(r"\d+\s+\w+\s+(Street|St|Road|Rd|Nagar|Colony)", re.IGNORECASE)


def redact_pii(text: str) -> str:
    """Replace simple PII with tokens before processing."""
    if not text:
        return text
    text = PHONE_REGEX.sub("[PHONE]", text)
    text = EMAIL_REGEX.sub("[EMAIL]", text)
    text = ADDRESS_REGEX.sub("[ADDRESS]", text)
    return text
