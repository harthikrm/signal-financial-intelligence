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


def get_filing_text(accession_url: str) -> str:
    """
    Fetch the full text of a filing document.
    Returns raw text content.
    """
    time.sleep(EDGAR_RATE_LIMIT_SLEEP)
    response = requests.get(accession_url,
                            headers=EDGAR_HEADERS, timeout=60)
    response.raise_for_status()
    return response.text


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
