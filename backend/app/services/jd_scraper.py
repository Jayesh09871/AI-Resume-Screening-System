import re
import json
import ipaddress
from urllib.parse import urlparse
from typing import Dict, Any, Optional, List
import httpx
from bs4 import BeautifulSoup, Tag
from backend.app.utils.logger import logger


class JDScraperError(Exception):
    """Custom exception raised when job description scraping fails."""
    pass


class JobDescriptionScraper:
    """
    Production-grade Job Description URL Scraper.
    Supports Schema.org JobPosting JSON-LD, Greenhouse, Lever, Ashby, Workable,
    LinkedIn, Indeed, and generic company career pages.
    Includes SSRF prevention and deterministic text cleanup.
    """

    REQUEST_TIMEOUT = 12.0
    MAX_REDIRECTS = 5
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
    }

    @classmethod
    def validate_url(cls, url: str) -> str:
        """
        Validate URL format and prevent Server-Side Request Forgery (SSRF).
        Rejects localhost, local networks, AWS metadata, and invalid schemes.
        """
        if not url or not isinstance(url, str):
            raise JDScraperError("Please provide a valid URL string.")

        url = url.strip()
        parsed = urlparse(url)

        if parsed.scheme not in ("http", "https"):
            raise JDScraperError("URL must begin with http:// or https://")

        hostname = parsed.hostname
        if not hostname:
            raise JDScraperError("Invalid URL: Missing hostname.")

        # Check for banned localhost / local names
        banned_hostnames = {"localhost", "127.0.0.1", "0.0.0.0", "::1", "metadata.google.internal"}
        if hostname.lower() in banned_hostnames:
            raise JDScraperError("Access to internal/localhost addresses is prohibited.")

        # Check for private IP addresses
        try:
            ip = ipaddress.ip_address(hostname)
            if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved:
                raise JDScraperError("Access to private/local network IP addresses is prohibited.")
        except ValueError:
            # Hostname is a domain name (e.g. greenhouse.io), which is allowed
            pass

        return url

    @classmethod
    def fetch_html(cls, url: str) -> str:
        """Fetch the raw HTML of the job posting using httpx."""
        validated_url = cls.validate_url(url)
        try:
            with httpx.Client(
                headers=cls.HEADERS,
                timeout=cls.REQUEST_TIMEOUT,
                follow_redirects=True,
                max_redirects=cls.MAX_REDIRECTS,
            ) as client:
                response = client.get(validated_url)

                if response.status_code == 404:
                    raise JDScraperError("Job posting not found (HTTP 404). Please verify the link.")
                elif response.status_code == 403:
                    raise JDScraperError(
                        "The job board protected this posting with a bot check (HTTP 403). "
                        "Please copy and paste the job description text directly."
                    )
                elif response.status_code >= 400:
                    raise JDScraperError(f"Failed to fetch job posting (HTTP {response.status_code}).")

                content_type = response.headers.get("content-type", "").lower()
                if "html" not in content_type and "text" not in content_type:
                    raise JDScraperError(f"Unsupported content type '{content_type}'. Must be a web page.")

                return response.text
        except httpx.TimeoutException:
            raise JDScraperError("Connection timed out while fetching the job URL. Please try again.")
        except httpx.RequestError as e:
            logger.error(f"HTTP request error fetching {url}: {e}")
            raise JDScraperError(f"Network error while connecting to job URL: {str(e)}")

    @classmethod
    def extract_from_json_ld(cls, soup: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """
        Check for Schema.org 'JobPosting' structured data.
        Common on LinkedIn, Greenhouse, Lever, Ashby, and enterprise career portals.
        """
        for script in soup.find_all("script", type="application/ld+json"):
            if not script.string:
                continue
            try:
                data = json.loads(script.string.strip())
            except Exception:
                continue

            # Can be a single dict or a list of dicts, or contained in @graph
            candidates = []
            if isinstance(data, dict):
                if "@graph" in data and isinstance(data["@graph"], list):
                    candidates.extend(data["@graph"])
                else:
                    candidates.append(data)
            elif isinstance(data, list):
                candidates.extend(data)

            for item in candidates:
                if not isinstance(item, dict):
                    continue
                type_val = item.get("@type", "")
                is_job = (
                    type_val == "JobPosting"
                    or (isinstance(type_val, list) and "JobPosting" in type_val)
                )

                if is_job and item.get("description"):
                    raw_desc = str(item.get("description", ""))
                    # HTML inside JSON-LD needs to be parsed and cleaned
                    desc_soup = BeautifulSoup(raw_desc, "html.parser")
                    cleaned_text = cls._clean_soup_text(desc_soup)

                    if len(cleaned_text.split()) >= 15:
                        title = item.get("title") or item.get("name") or ""
                        company = ""
                        org = item.get("hiringOrganization")
                        if isinstance(org, dict):
                            company = org.get("name", "")
                        elif isinstance(org, str):
                            company = org

                        return {
                            "title": title.strip(),
                            "company": company.strip(),
                            "jd_text": cleaned_text,
                            "source": "schema.org/JobPosting"
                        }
        return None

    @classmethod
    def extract_from_specialized_selectors(cls, soup: BeautifulSoup, url: str) -> Optional[Dict[str, Any]]:
        """Extract content using specialized DOM selectors for popular ATS platforms."""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        title = ""
        company = ""
        content_el: Optional[Tag] = None

        # 1. Greenhouse (boards.greenhouse.io or embedded)
        if "greenhouse.io" in domain or soup.find(id="gh_jid") or soup.find(class_="app-title"):
            title_el = soup.find(class_="app-title") or soup.select_one("#header h1")
            if title_el:
                title = title_el.get_text(strip=True)
            company_el = soup.find(class_="company-name")
            if company_el:
                company = company_el.get_text(strip=True).lstrip("at ").strip()
            content_el = soup.find(id="content") or soup.find(id="main_fields") or soup.find(class_="job__description")

        # 2. Lever (jobs.lever.co)
        elif "lever.co" in domain or soup.find(class_="posting-headline"):
            title_el = soup.select_one(".posting-headline h2") or soup.find("h2")
            if title_el:
                title = title_el.get_text(strip=True)
            content_el = soup.find(class_="section-page") or soup.find(class_="posting-sections")

        # 3. Ashby (jobs.ashbyhq.com)
        elif "ashbyhq.com" in domain:
            title_el = soup.find("h1")
            if title_el:
                title = title_el.get_text(strip=True)
            content_el = soup.select_one('[data-testid="job-details"]') or soup.find(class_="ashby-job-posting-container")

        # 4. Workable (apply.workable.com)
        elif "workable.com" in domain:
            title_el = soup.select_one('[data-ui="job-title"]') or soup.find("h1")
            if title_el:
                title = title_el.get_text(strip=True)
            content_el = soup.select_one('[data-ui="job-description"]') or soup.find("section")

        # 5. LinkedIn public job posting
        elif "linkedin.com" in domain:
            title_el = soup.find(class_="topcard__title") or soup.find("h1")
            if title_el:
                title = title_el.get_text(strip=True)
            company_el = soup.find(class_="topcard__org-name-link") or soup.find(class_="topcard__flavor")
            if company_el:
                company = company_el.get_text(strip=True)
            content_el = (
                soup.find(class_="show-more-less-html__markup")
                or soup.find(class_="description__text")
                or soup.find(class_="jobs-description__content")
            )

        # 6. Indeed
        elif "indeed.com" in domain:
            title_el = soup.find(class_="jobsearch-JobInfoHeader-title") or soup.find("h1")
            if title_el:
                title = title_el.get_text(strip=True)
            content_el = soup.find(id="jobDescriptionText")

        if content_el:
            cleaned = cls._clean_soup_text(content_el)
            if len(cleaned.split()) >= 15:
                return {
                    "title": title,
                    "company": company,
                    "jd_text": cleaned,
                    "source": f"ats_selector:{domain}"
                }

        return None

    @classmethod
    def extract_from_heuristics(cls, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Generic fallback: remove noise elements, search for job-related containers,
        or find the element with the highest text density.
        """
        # Remove noisy tags
        for tag_name in [
            "script", "style", "nav", "footer", "header", "aside",
            "noscript", "svg", "form", "iframe", "button"
        ]:
            for el in soup.find_all(tag_name):
                el.decompose()

        # Find potential title
        title = ""
        h1 = soup.find("h1")
        if h1:
            title = h1.get_text(strip=True)

        # Look for semantic job containers by common class/id patterns
        patterns = [
            re.compile(r"job[-_]?desc", re.I),
            re.compile(r"posting[-_]?content", re.I),
            re.compile(r"job[-_]?detail", re.I),
            re.compile(r"careers?[-_]?content", re.I),
            re.compile(r"description", re.I),
        ]

        best_el: Optional[Tag] = None
        best_word_count = 0

        # Try matching container classes/ids
        for p in patterns:
            for el in soup.find_all(attrs={"class": p}):
                text = cls._clean_soup_text(el)
                wc = len(text.split())
                if wc > best_word_count:
                    best_word_count = wc
                    best_el = el
            for el in soup.find_all(attrs={"id": p}):
                text = cls._clean_soup_text(el)
                wc = len(text.split())
                if wc > best_word_count:
                    best_word_count = wc
                    best_el = el

        # If still nothing, try <main> or <article>
        if not best_el or best_word_count < 40:
            for tag in soup.find_all(["article", "main"]):
                text = cls._clean_soup_text(tag)
                wc = len(text.split())
                if wc > best_word_count:
                    best_word_count = wc
                    best_el = tag

        # If still nothing, inspect body directly
        if not best_el or best_word_count < 40:
            best_el = soup.body or soup

        cleaned = cls._clean_soup_text(best_el) if best_el else ""
        return {
            "title": title,
            "company": "",
            "jd_text": cleaned,
            "source": "heuristic_fallback"
        }

    @classmethod
    def _clean_soup_text(cls, element: Tag) -> str:
        """Convert HTML element into clean readable plaintext with bullet point preservation."""
        if not element:
            return ""

        # Make a copy so modifications don't mutate original
        import copy
        el = copy.copy(element)

        # Convert list items to markdown bullets
        for li in el.find_all("li"):
            li.replace_with(f"\n- {li.get_text().strip()}")

        # Ensure headings and paragraphs start on new lines
        for tag in el.find_all(["h1", "h2", "h3", "h4", "h5", "h6", "p", "div", "br"]):
            tag.insert_before("\n")

        raw_text = el.get_text()

        # Clean consecutive blank lines and whitespace
        lines = [line.strip() for line in raw_text.splitlines()]
        cleaned_lines = []
        for line in lines:
            if line:
                cleaned_lines.append(line)
            elif cleaned_lines and cleaned_lines[-1] != "":
                cleaned_lines.append("")

        return "\n".join(cleaned_lines).strip()

    @classmethod
    def scrape(cls, url: str) -> Dict[str, Any]:
        """
        Orchestrate complete scraping process:
        1. Validate URL & prevent SSRF
        2. Fetch HTML
        3. Attempt Tier 1 (Schema.org JSON-LD)
        4. Attempt Tier 2 (Platform-specific DOM selectors)
        5. Attempt Tier 3 (Heuristic content extraction)
        6. Format & validate output
        """
        logger.info(f"Initiating Job Description scrape for URL: {url}")
        html = cls.fetch_html(url)
        soup = BeautifulSoup(html, "html.parser")

        # Tier 1: Schema.org
        result = cls.extract_from_json_ld(soup)
        if not result or len(result.get("jd_text", "").split()) < 15:
            # Tier 2: Specialized selectors
            result = cls.extract_from_specialized_selectors(soup, url)

        if not result or len(result.get("jd_text", "").split()) < 15:
            # Tier 3: Heuristics
            result = cls.extract_from_heuristics(soup)

        jd_text = result.get("jd_text", "")
        word_count = len(jd_text.split())

        if word_count < 15:
            raise JDScraperError(
                "Could not extract sufficient job description text from this URL (under 15 words). "
                "The page may be behind a login wall, bot protection, or require client-side JavaScript. "
                "Please copy and paste the job description text directly."
            )

        title = result.get("title", "").strip()
        company = result.get("company", "").strip()

        # Format header into JD text if title or company was identified and not already leading
        header_prefix = ""
        if title and company and title.lower() not in jd_text[:120].lower():
            header_prefix = f"{title} at {company}\n\n"
        elif title and title.lower() not in jd_text[:100].lower():
            header_prefix = f"{title}\n\n"

        full_jd_text = f"{header_prefix}{jd_text}".strip()

        logger.info(
            f"Successfully scraped JD from {url}: {word_count} words extracted "
            f"(Source: {result.get('source', 'unknown')})"
        )

        return {
            "url": url,
            "title": title or None,
            "company": company or None,
            "jd_text": full_jd_text,
            "word_count": len(full_jd_text.split()),
            "source": result.get("source", "generic")
        }
