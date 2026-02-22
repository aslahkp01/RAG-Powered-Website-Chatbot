import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from langchain_core.documents import Document
from config import Config

def clean_text(html):
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()
    return " ".join(soup.get_text(separator=" ").split())

def extract_links(base_url, html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for a in soup.find_all("a", href=True):
        full_url = urljoin(base_url, a["href"])
        parsed = urlparse(full_url)
        if parsed.netloc == urlparse(base_url).netloc:
            links.append(full_url)
    return links

def crawl(url, depth=0, visited=None):
    if visited is None:
        visited = set()

    if depth > Config.MAX_DEPTH or len(visited) >= Config.MAX_PAGES:
        return []

    try:
        response = requests.get(
            url,
            headers={"User-Agent": Config.USER_AGENT},
            timeout=8,
        )
        response.raise_for_status()
    except:
        return []

    visited.add(url)
    text = clean_text(response.text)

    documents = [
        Document(
            page_content=text,
            metadata={"source": url, "depth": depth}
        )
    ]

    if depth < Config.MAX_DEPTH:
        for link in extract_links(url, response.text):
            if link not in visited:
                documents.extend(crawl(link, depth + 1, visited))

    return documents