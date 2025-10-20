"""
ArXiv API Integration

This module provides functionality to search and fetch papers from arXiv API.
Based on the provided arXiv search implementation with enhancements for RAG pipeline.
"""

import time
import urllib.parse
import requests
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import logging

# Set up logging
logger = logging.getLogger(__name__)

ARXIV_API_BASE = "https://export.arxiv.org/api/query"


class ArxivAPIError(Exception):
    """Custom exception for ArXiv API errors."""
    pass


def build_search_query(
    terms: Optional[List[str]] = None,
    title_terms: Optional[List[str]] = None,
    author: Optional[str] = None,
    category: Optional[str] = None
) -> str:
    """
    Build arXiv 'search_query' string.

    Examples of components:
      - all:term -> search all fields
      - ti:term  -> title
      - au:author_name -> author
      - cat:cs.LG -> category
    Terms are ANDed within each list, components are ANDed together.

    Note: Spaces must be replaced with '+' in the query component; we use urllib.parse.quote_plus.
    """
    components = []

    def join_terms(prefix: str, items: List[str]):
        for t in items:
            t = t.strip()
            if not t:
                continue
            # arXiv recommends ASCII; quote_plus encodes spaces as '+'
            components.append(f"{prefix}:{t}")

    if terms:
        join_terms("all", terms)
    if title_terms:
        join_terms("ti", title_terms)
    if author:
        components.append(f"au:{author.strip()}")
    if category:
        components.append(f"cat:{category.strip()}")

    # AND components; for phrases, users can pass quoted terms like '"large language model"'
    return " AND ".join(components) if components else "all:*"


def parse_atom(xml_text: str) -> List[Dict[str, Any]]:
    """
    Parse arXiv Atom feed XML into a list of entries.
    """
    ns = {
        "atom": "http://www.w3.org/2005/Atom",
        "arxiv": "http://arxiv.org/schemas/atom"
    }
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError as e:
        raise ArxivAPIError(f"Failed to parse XML: {e}")

    entries = []
    for entry in root.findall("atom:entry", ns):
        # Basic fields
        arxiv_id = entry.findtext("atom:id", default="", namespaces=ns)
        title = (entry.findtext("atom:title", default="", namespaces=ns) or "").strip()
        summary = (entry.findtext("atom:summary", default="", namespaces=ns) or "").strip()
        published = entry.findtext("atom:published", default="", namespaces=ns)
        updated = entry.findtext("atom:updated", default="", namespaces=ns)

        # Authors
        authors = []
        for a in entry.findall("atom:author", ns):
            name = a.findtext("atom:name", default="", namespaces=ns)
            if name:
                authors.append(name)

        # Categories
        categories = []
        for c in entry.findall("atom:category", ns):
            term = c.attrib.get("term")
            if term:
                categories.append(term)

        # Links (pdf, doi, html)
        links = []
        for l in entry.findall("atom:link", ns):
            href = l.attrib.get("href")
            rel = l.attrib.get("rel")
            title_attr = l.attrib.get("title")
            if href:
                links.append({"href": href, "rel": rel, "title": title_attr})

        # Primary category and doi (in arxiv namespace)
        primary_category = None
        pc = entry.find("arxiv:primary_category", ns)
        if pc is not None:
            primary_category = pc.attrib.get("term")

        doi = None
        doi_el = entry.find("arxiv:doi", ns)
        if doi_el is not None and doi_el.text:
            doi = doi_el.text.strip()

        # Comment, journal ref
        comment = None
        comment_el = entry.find("arxiv:comment", ns)
        if comment_el is not None and comment_el.text:
            comment = comment_el.text.strip()

        journal_ref = None
        jr_el = entry.find("arxiv:journal_ref", ns)
        if jr_el is not None and jr_el.text:
            journal_ref = jr_el.text.strip()

        entries.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "authors": authors,
            "categories": categories,
            "primary_category": primary_category,
            "published": published,
            "updated": updated,
            "links": links,
            "doi": doi,
            "comment": comment,
            "journal_ref": journal_ref,
        })

    return entries


def search_arxiv(
    search_query: str,
    start: int = 0,
    max_results: int = 50,
    sort_by: str = "relevance",  # or "lastUpdatedDate", "submittedDate"
    sort_order: str = "descending",
    timeout_sec: int = 20,
) -> List[Dict[str, Any]]:
    """
    Perform a single arXiv search API request and return parsed entries.

    Rate limits: arXiv asks clients to limit to ~1 request per 3 seconds; we sleep in paginate function.
    """
    if max_results < 1 or max_results > 2000:
        raise ValueError("max_results must be between 1 and 2000")

    params = {
        "search_query": search_query,
        "start": str(start),
        "max_results": str(max_results),
        "sortBy": sort_by,
        "sortOrder": sort_order,
    }

    # Build URL with proper encoding
    url = f"{ARXIV_API_BASE}?{urllib.parse.urlencode(params, quote_via=urllib.parse.quote_plus)}"

    resp = requests.get(url, headers={"User-Agent": "arxiv-rag-pipeline/1.0"}, timeout=timeout_sec)
    if resp.status_code != 200:
        raise ArxivAPIError(f"HTTP {resp.status_code}: {resp.text[:200]}")
    return parse_atom(resp.text)


def paginate_search(
    search_query: str,
    total_results: int,
    page_size: int = 100,
    pause_sec: float = 3.0,
    **kwargs,
) -> List[Dict[str, Any]]:
    """
    Fetch multiple pages until total_results is reached or entries exhausted.

    kwargs are forwarded to search_arxiv (sort_by, sort_order, timeout_sec).
    """
    all_entries: List[Dict[str, Any]] = []
    fetched = 0
    while fetched < total_results:
        to_fetch = min(page_size, total_results - fetched)
        entries = search_arxiv(
            search_query=search_query, start=fetched, max_results=to_fetch, **kwargs
        )
        if not entries:
            break
        all_entries.extend(entries)
        fetched += len(entries)
        # Respect arXiv rate limit suggestions
        time.sleep(pause_sec)
    return all_entries


def format_paper_for_rag(entry: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format an arXiv entry for RAG storage.
    
    Returns a dictionary with all metadata needed for vector storage.
    """
    # Extract PDF URL
    pdf_url = None
    for link in entry.get("links", []):
        if link.get("title") == "pdf" or (link.get("rel") == "related" and "pdf" in link.get("href", "")):
            pdf_url = link["href"]
            break
    
    # Create combined text for embedding (title + abstract)
    combined_text = f"{entry['title']}\n\n{entry['summary']}"
    
    return {
        "id": entry["id"],
        "title": entry["title"],
        "abstract": entry["summary"],
        "authors": ", ".join(entry["authors"]),  # Convert list to string
        "categories": ", ".join(entry["categories"]),  # Convert list to string
        "primary_category": entry.get("primary_category"),
        "published": entry.get("published"),
        "updated": entry.get("updated"),
        "pdf_url": pdf_url,
        "doi": entry.get("doi"),
        "comment": entry.get("comment"),
        "journal_ref": entry.get("journal_ref"),
        "text": combined_text,  # For embedding
        "source": "arxiv"
    }


def fetch_papers_for_topic(
    topic: str,
    max_papers: int = 12,
    category: Optional[str] = None,
    sort_by: str = "submittedDate",
    sort_order: str = "descending"
) -> List[Dict[str, Any]]:
    """
    Fetch papers for a given topic and format them for RAG storage.
    
    Args:
        topic: Research topic to search for
        max_papers: Maximum number of papers to fetch
        category: Optional arXiv category filter (e.g., "cs.AI", "cs.LG")
        sort_by: Sort criteria ("relevance", "submittedDate", "lastUpdatedDate")
        sort_order: Sort order ("ascending", "descending")
    
    Returns:
        List of formatted paper dictionaries ready for vector storage
    """
    logger.info(f"Fetching papers for topic: {topic}")
    
    # Build search query
    search_query = build_search_query(
        terms=[topic],
        category=category
    )
    
    logger.info(f"Search query: {search_query}")
    
    # Fetch papers with pagination
    entries = paginate_search(
        search_query=search_query,
        total_results=max_papers,
        page_size=min(50, max_papers),  # ArXiv API limit
        pause_sec=3.0,  # Respect rate limits
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Format papers for RAG
    formatted_papers = []
    for entry in entries[:max_papers]:  # Ensure we don't exceed max_papers
        formatted_paper = format_paper_for_rag(entry)
        formatted_papers.append(formatted_paper)
    
    logger.info(f"Successfully fetched and formatted {len(formatted_papers)} papers")
    return formatted_papers


def format_brief(entry: Dict[str, Any]) -> str:
    """
    Return a single-line brief string for an entry.
    """
    title = entry["title"].replace("\n", " ").strip()
    authors = ", ".join(entry["authors"])
    primary = entry.get("primary_category") or ""
    published = entry.get("published") or ""
    # Find PDF link if present
    pdf = next((l["href"] for l in entry["links"] if l.get("title") == "pdf" or (l.get("rel") == "related" and "pdf" in l.get("href", ""))), None)
    return f"{title} — {authors} — {primary} — {published} — PDF: {pdf or 'N/A'}"


def main():
    """Example usage of the ArXiv fetcher."""
    # Example: search for "large language models" in title and ML category, newest first
    search_query = build_search_query(
        title_terms=['"large language model"', "LLM"],
        category="cs.LG"
    )
    print("Query:", search_query)

    entries = paginate_search(
        search_query=search_query,
        total_results=150,
        page_size=50,
        sort_by="submittedDate",
        sort_order="descending",
    )

    print(f"Fetched {len(entries)} results")
    for e in entries[:10]:
        print(format_brief(e))


if __name__ == "__main__":
    main()
