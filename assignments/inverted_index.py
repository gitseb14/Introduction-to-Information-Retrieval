import re
import requests
from collections import defaultdict

WIKI_API = "https://en.wikipedia.org/w/api.php"

DOC_TITLES = [
    "Pizza",
    "The Hitchhiker's Guide to the Galaxy",
    "George Gershwin"
]


session = requests.Session()

HEADERS = {
    "User-Agent": "Python/requests"
}

def wiki(title):
    params = {
        "action": "query",
        "prop": "extracts",
        "explaintext": False,
        "titles": title,
        "format": "json",
        "redirects": 0,
        "formatversion": 2
    }
    resp = session.get(WIKI_API, params=params, headers=HEADERS).json()
    pages = resp.get("query", {}).get("pages", [])
    if not pages:
        return ""
    return pages[0].get("extract", "")


def build_inverted_index(docs):
    inverted = defaultdict(list)
    for doc_id, text in docs.items():
        tokens = [t for t in (re.split(r"\W+", text.lower())) if t]
        positions_by_term = defaultdict(list)
        for pos, tok in enumerate(tokens):
            positions_by_term[tok].append(pos)
        for term, positions in positions_by_term.items():
            posting = {"doc_id": doc_id, "positions": positions}
            inverted[term].append(posting)
    return dict(inverted)

def main():
    docs = {}
    for i, title in enumerate(DOC_TITLES, start=1):
        print(f"Fetching: {title}")
        text = wiki(title)
        docs[i] = {"title": title, "text": text}
    doc_texts = {doc_id: info["text"] for doc_id, info in docs.items()}
    index = build_inverted_index(doc_texts)
    sample_terms = input('input terms to search ').split(', ')
    for term in sample_terms:
        postings = index.get(term, [])
        print(f"{len(postings)} postings found for {term}")
        for p in postings:
            title = docs[p["doc_id"]]["title"]
            print(f"  doc_id={p['doc_id']} title='{title}' positions={p['positions'][:5]}")
if __name__ == "__main__":
    main()
