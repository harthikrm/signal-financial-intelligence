import time
import requests
from config import EDGAR_HEADERS, EDGAR_RATE_LIMIT_SLEEP

# Rule-3 amendment 2026-05-13 — manual bug fix.
# data.sec.gov serves XBRL/JSON APIs (companyfacts, submissions).
# www.sec.gov serves legacy CGI endpoints (browse-edgar Atom feed).
# Original manual had a single BASE_URL = "https://data.sec.gov" used for both,
# which 404s on the browse-edgar path.
BASE_URL   = "https://data.sec.gov"
BROWSE_URL = "https://www.sec.gov"
SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"


def get_company_facts(cik: str) -> dict:
    """
    Fetch all XBRL facts for a company from SEC EDGAR.
    Returns the full companyfacts JSON.
    """
    padded_cik = str(cik).zfill(10)
    url = f"{BASE_URL}/api/xbrl/companyfacts/CIK{padded_cik}.json"
    time.sleep(EDGAR_RATE_LIMIT_SLEEP)
    response = requests.get(url, headers=EDGAR_HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def get_filing_list(cik: str, form_type: str,
                    date_from: str, date_to: str) -> list:
    """
    Get list of filings for a company by form type and date range.
    Returns list of dicts with accession_number, filing_date, document_url.
    """
    padded_cik = str(cik).zfill(10)
    url = f"{BROWSE_URL}/cgi-bin/browse-edgar"
    params = {
        "action": "getcompany",
        "CIK": padded_cik,
        "type": form_type,
        "dateb": "",
        "owner": "include",
        "count": 40,
        "search_text": "",
        "output": "atom",
    }
    time.sleep(EDGAR_RATE_LIMIT_SLEEP)
    response = requests.get(url, params=params,
                            headers=EDGAR_HEADERS, timeout=30)
    response.raise_for_status()
    return _parse_filing_list(response.text, date_from, date_to)


def _resolve_index_doc_href(href: str) -> str | None:
    """Map an index-page href to a direct Archives .htm URL."""
    from urllib.parse import parse_qs, urlparse

    if not href or 'index' in href.lower():
        return None

    if href.startswith('/ix?') or 'ix?doc=' in href:
        parsed = urlparse(
            'https://www.sec.gov' + href if href.startswith('/') else href
        )
        doc = parse_qs(parsed.query).get('doc', [None])[0]
        if doc and (doc.endswith('.htm') or doc.endswith('.html')):
            return 'https://www.sec.gov' + doc if doc.startswith('/') else doc
        return None

    if href.endswith('.htm') or href.endswith('.html'):
        if href.startswith('/'):
            return 'https://www.sec.gov' + href
        if href.startswith('http'):
            return href
        return f'https://www.sec.gov/{href.lstrip("/")}'
    return None


_PRIMARY_FORM_TYPES = ('10-K', '10-Q', '8-K', '10-K/A', '10-Q/A', '8-K/A')


def get_filing_text(accession_url: str) -> str:
    """
    Fetch the full text of a filing document.
    1. Fetches the index page
    2. Finds the primary document (10-K, 10-Q, 8-K htm file)
    3. Fetches that document and strips HTML
    Returns clean plain text content.
    """
    import re

    from bs4 import BeautifulSoup

    time.sleep(EDGAR_RATE_LIMIT_SLEEP)

    # Step 1: Fetch index page
    response = requests.get(accession_url,
                            headers=EDGAR_HEADERS, timeout=60)
    response.raise_for_status()

    # Step 2: Parse index to find primary document
    soup = BeautifulSoup(response.text, 'html.parser')

    candidates: list[tuple[str, str, int]] = []
    for row in soup.find_all('tr'):
        cells = row.find_all('td')
        if len(cells) < 3:
            continue
        link = cells[2].find('a') if len(cells) > 2 else None
        if not link or not link.get('href'):
            continue
        doc_url = _resolve_index_doc_href(link['href'])
        if not doc_url:
            continue
        desc = cells[1].get_text(strip=True) if len(cells) > 1 else ''
        doc_type = cells[3].get_text(strip=True) if len(cells) > 3 else ''
        size_raw = cells[4].get_text(strip=True) if len(cells) > 4 else '0'
        size = int(re.sub(r'\D', '', size_raw) or 0)
        candidates.append((doc_type or desc, doc_url, size))

    doc_url = None
    for form_type in _PRIMARY_FORM_TYPES:
        for row_type, url, _size in candidates:
            if row_type == form_type:
                doc_url = url
                break
        if doc_url:
            break

    if not doc_url and candidates:
        doc_url = max(candidates, key=lambda c: c[2])[1]

    if not doc_url:
        for a in soup.find_all('a', href=True):
            doc_url = _resolve_index_doc_href(a['href'])
            if doc_url and '/Archives/' in doc_url:
                break
        else:
            doc_url = None

    if not doc_url:
        return ''

    # Step 3: Fetch actual document
    time.sleep(EDGAR_RATE_LIMIT_SLEEP)
    doc_response = requests.get(doc_url,
                                headers=EDGAR_HEADERS, timeout=60)
    doc_response.raise_for_status()

    # Step 4: Strip HTML to get clean text
    doc_soup = BeautifulSoup(doc_response.text, 'html.parser')

    for element in doc_soup(['script', 'style', 'head']):
        element.decompose()

    text = doc_soup.get_text(separator=' ', strip=True)
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def _parse_filing_list(atom_xml: str,
                       date_from: str, date_to: str) -> list:
    """Parse EDGAR Atom XML response into list of filing dicts."""
    import xml.etree.ElementTree as ET
    ns = {"atom": "http://www.w3.org/2005/Atom"}
    root = ET.fromstring(atom_xml)
    filings = []
    for entry in root.findall("atom:entry", ns):
        date_el = entry.find("atom:updated", ns)
        if date_el is None:
            continue
        filing_date = date_el.text[:10]
        if not (date_from <= filing_date <= date_to):
            continue
        link_el = entry.find("atom:link", ns)
        if link_el is None:
            continue
        filings.append({
            "filing_date": filing_date,
            "document_url": link_el.get("href", ""),
        })
    return filings
