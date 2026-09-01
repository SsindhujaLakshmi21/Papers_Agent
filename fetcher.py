"""
Paper Fetcher: Retrieves newly published Computer Science papers.
Primary: Google Scholar (web scraper)
Fallback 1: arXiv API (cs.* categories sorted by submittedDate)
Fallback 2: Semantic Scholar API
"""

import time
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
import feedparser

from config import logger
from database import is_paper_sent

# User-Agent mimicking a standard desktop Chrome browser
BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.google.com/",
}


def fetch_google_scholar(query: str = "computer science", max_results: int = 10) -> List[Dict[str, Any]]:
    """
    Attempts to fetch recent papers from Google Scholar.
    Falls back gracefully if Google Scholar blocks or rate-limits the request.
    """
    logger.info("Attempting primary source: Google Scholar search for '%s'...", query)
    papers = []
    
    current_year = datetime.now().year
    params = {
        "q": query,
        "hl": "en",
        "as_ylo": str(current_year),
        "as_sdt": "0,5"
    }
    url = f"https://scholar.google.com/scholar?{urllib.parse.urlencode(params)}"
    
    try:
        response = requests.get(url, headers=BROWSER_HEADERS, timeout=10)
        if response.status_code != 200:
            logger.warning("Google Scholar returned status code %d (likely rate-limited). Falling back.", response.status_code)
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Check for CAPTCHA or blocking
        if "recaptcha" in response.text.lower() or "unusual traffic" in response.text.lower():
            logger.warning("Google Scholar triggered CAPTCHA / bot detection. Falling back to arXiv API.")
            return []
        
        results = soup.find_all("div", class_="gs_r gs_or gs_scl")
        for res in results:
            title_tag = res.find("h3", class_="gs_rt")
            if not title_tag:
                continue
            
            link_tag = title_tag.find("a")
            title = title_tag.get_text().strip()
            # Clean off [HTML] or [PDF] tags from title
            title = title.replace("[HTML]", "").replace("[PDF]", "").replace("[B]", "").strip()
            
            paper_url = link_tag["href"] if link_tag and "href" in link_tag.attrs else url
            
            pub_info = res.find("div", class_="gs_a")
            authors_venue = pub_info.get_text().strip() if pub_info else "Computer Science Community"
            
            snippet_div = res.find("div", class_="gs_rs")
            abstract = snippet_div.get_text().strip() if snippet_div else "Abstract unavailable from snippet."
            
            papers.append({
                "paper_id": paper_url,
                "title": title,
                "authors": [authors_venue.split("-")[0].strip()],
                "venue": authors_venue.split("-")[1].strip() if "-" in authors_venue else "Recent CS Publication",
                "published_date": str(current_year),
                "url": paper_url,
                "pdf_url": paper_url,
                "abstract": abstract,
                "source": "Google Scholar"
            })
            if len(papers) >= max_results:
                break
                
        logger.info("Successfully fetched %d papers from Google Scholar.", len(papers))
        return papers
        
    except Exception as e:
        logger.warning("Google Scholar scraping error: %s. Falling back.", e)
        return []


def fetch_arxiv_cs(max_results: int = 35) -> List[Dict[str, Any]]:
    """
    Fetches newly submitted/announced Computer Science papers from arXiv API.
    Covers broad CS domains: AI, ML, NLP/CL, Computer Vision, Security, Software Eng, Distributed Systems.
    """
    logger.info("Fetching fresh papers from arXiv API (cs.* categories)...")
    papers = []
    
    # Comprehensive CS categories
    categories = [
        "cat:cs.AI", "cat:cs.LG", "cat:cs.CL", "cat:cs.CV", 
        "cat:cs.CR", "cat:cs.SE", "cat:cs.DC", "cat:cs.RO", 
        "cat:cs.NE", "cat:cs.SY"
    ]
    query_str = "+OR+".join(categories)
    api_url = f"http://export.arxiv.org/api/query?search_query={query_str}&sortBy=submittedDate&sortOrder=descending&max_results={max_results}"
    
    try:
        response = requests.get(api_url, timeout=15)
        if response.status_code != 200:
            logger.error("arXiv API returned HTTP %d", response.status_code)
            return []
        
        feed = feedparser.parse(response.content)
        
        for entry in feed.entries:
            title = entry.title.replace("\n", " ").strip()
            # Clean multiple whitespaces
            title = " ".join(title.split())
            
            paper_id = entry.id
            published_date = entry.published[:10] if hasattr(entry, "published") else datetime.now().strftime("%Y-%m-%d")
            
            authors = [author.name for author in entry.authors] if hasattr(entry, "authors") else ["Unknown Authors"]
            abstract = entry.summary.replace("\n", " ").strip() if hasattr(entry, "summary") else "No abstract provided."
            abstract = " ".join(abstract.split())
            
            # Find PDF link
            pdf_url = entry.link
            for link in entry.links:
                if link.get("title") == "pdf" or link.get("type") == "application/pdf":
                    pdf_url = link.get("href", entry.link)
                    break
            
            # Primary category tag
            category = entry.arxiv_primary_category["term"] if hasattr(entry, "arxiv_primary_category") else "cs"
            
            papers.append({
                "paper_id": paper_id,
                "title": title,
                "authors": authors,
                "venue": f"arXiv: {category.upper()}",
                "published_date": published_date,
                "url": entry.link,
                "pdf_url": pdf_url,
                "abstract": abstract,
                "source": "arXiv API"
            })
            
        logger.info("Successfully fetched %d papers from arXiv API.", len(papers))
        return papers
        
    except Exception as e:
        logger.error("Error fetching from arXiv API: %s", e)
        return []


def fetch_semantic_scholar(query: str = "Computer Science", max_results: int = 20) -> List[Dict[str, Any]]:
    """
    Fallback 2: Semantic Scholar API search.
    """
    logger.info("Fetching papers from Semantic Scholar API fallback...")
    papers = []
    current_year = datetime.now().year
    
    api_url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "year": f"{current_year-1}-{current_year}",
        "fields": "paperId,title,abstract,authors,year,publicationDate,url,openAccessPdf,venue",
        "limit": str(max_results)
    }
    
    try:
        response = requests.get(api_url, params=params, headers=BROWSER_HEADERS, timeout=12)
        if response.status_code != 200:
            logger.warning("Semantic Scholar returned HTTP %d", response.status_code)
            return []
        
        data = response.json()
        for item in data.get("data", []):
            title = item.get("title", "").strip()
            if not title:
                continue
            
            authors = [a.get("name") for a in item.get("authors", []) if a.get("name")]
            abstract = item.get("abstract") or "Abstract unavailable."
            paper_url = item.get("url") or f"https://www.semanticscholar.org/paper/{item.get('paperId')}"
            pdf_url = item.get("openAccessPdf", {}).get("url") if item.get("openAccessPdf") else paper_url
            
            papers.append({
                "paper_id": item.get("paperId", paper_url),
                "title": title,
                "authors": authors or ["Authors listed on publication"],
                "venue": item.get("venue") or "Semantic Scholar CS",
                "published_date": item.get("publicationDate") or str(item.get("year", current_year)),
                "url": paper_url,
                "pdf_url": pdf_url,
                "abstract": abstract,
                "source": "Semantic Scholar"
            })
            
        logger.info("Fetched %d papers from Semantic Scholar.", len(papers))
        return papers
    except Exception as e:
        logger.warning("Semantic Scholar API error: %s", e)
        return []


def get_new_cs_papers(count: int = 5) -> List[Dict[str, Any]]:
    """
    Master orchestrator: Fetches candidate papers, checks against database
    to deduplicate, and returns exactly `count` unseen papers.
    """
    candidates = []
    
    # 1. Primary: Google Scholar
    scholar_papers = fetch_google_scholar(max_results=15)
    candidates.extend(scholar_papers)
    
    # 2. If needed or to ensure diverse, rich full-abstract papers, pull arXiv
    if len(candidates) < count * 3:
        arxiv_papers = fetch_arxiv_cs(max_results=35)
        candidates.extend(arxiv_papers)
        
    # 3. If still short, pull Semantic Scholar
    if len(candidates) < count:
        sem_papers = fetch_semantic_scholar(max_results=20)
        candidates.extend(sem_papers)
    
    # Deduplicate against database and within current batch
    unique_new_papers = []
    seen_in_batch = set()
    
    for paper in candidates:
        pid = paper.get("paper_id", "")
        title = paper.get("title", "")
        
        if not title:
            continue
            
        title_key = title.lower().strip()
        if title_key in seen_in_batch:
            continue
            
        if is_paper_sent(pid, title):
            logger.debug("Skipping already sent paper: %s", title)
            continue
            
        seen_in_batch.add(title_key)
        unique_new_papers.append(paper)
        
        if len(unique_new_papers) >= count:
            break
            
    logger.info("Found %d brand-new, unseen CS papers for today's digest.", len(unique_new_papers))
    return unique_new_papers
