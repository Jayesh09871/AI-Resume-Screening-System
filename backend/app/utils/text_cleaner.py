import re
import unicodedata
from typing import List, Optional, Tuple


def normalize_whitespace(text: str) -> str:
    """Normalize irregular spaces, tabs, and duplicate empty lines."""
    if not text:
        return ""
    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)
    # Replace non-breaking spaces
    text = text.replace("\u00a0", " ").replace("\r\n", "\n").replace("\r", "\n")
    # Replace multiple spaces with a single space per line
    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    # Remove excessive blank lines (max 2 consecutive newlines)
    cleaned_text = "\n".join(lines)
    cleaned_text = re.sub(r"\n{3,}", "\n\n", cleaned_text)
    return cleaned_text.strip()


def extract_emails(text: str) -> List[str]:
    """Extract email addresses using regex."""
    email_pattern = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b"
    matches = re.findall(email_pattern, text)
    # Return unique emails maintaining order
    seen = set()
    return [m for m in matches if not (m.lower() in seen or seen.add(m.lower()))]


def extract_phones(text: str) -> List[str]:
    """Extract phone numbers in various formats."""
    phone_pattern = r"(?:(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,4}\)?[\s-]?)?\d{3,5}[\s-]?\d{3,5}(?:[\s-]?\d{1,5})?)"
    potential_matches = re.findall(phone_pattern, text)
    valid_phones = []
    for match in potential_matches:
        cleaned = re.sub(r"[^\d+]", "", match)
        # Filter out short numbers or zip codes, valid phone usually 10-15 digits
        if 10 <= len(cleaned) <= 15:
            valid_phones.append(match.strip())
    # Return unique phone numbers
    seen = set()
    return [p for p in valid_phones if not (p in seen or seen.add(p))]


def extract_urls(text: str) -> List[str]:
    """Extract URLs including LinkedIn, GitHub, portfolio links."""
    url_pattern = r"(https?://[^\s,]+|www\.[^\s,]+|(?:linkedin\.com|github\.com)/[^\s,]+)"
    matches = re.findall(url_pattern, text, re.IGNORECASE)
    cleaned_urls = []
    seen = set()
    for url in matches:
        url = url.rstrip(".,);")
        if not url.startswith("http"):
            url = f"https://{url}"
        if url.lower() not in seen:
            seen.add(url.lower())
            cleaned_urls.append(url)
    return cleaned_urls


def split_into_sentences(text: str) -> List[str]:
    """Split text into coherent sentences or bullet points for semantic analysis."""
    lines = text.split("\n")
    sentences = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        # Check if line contains bullet markers
        sub_lines = re.split(r"(?<=[.!?])\s+|[•\-*▪]\s+", line)
        for s in sub_lines:
            s_clean = s.strip(" •-*▪\t\r\n")
            if len(s_clean) > 10:  # Minimum useful length for semantic analysis
                sentences.append(s_clean)
    return sentences
