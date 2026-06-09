import re

STOPWORDS = {
    "the", "and", "for", "with", "our", "your", "you", "will", "are", "have", "this", "that", 
    "with", "from", "these", "those", "their", "them", "they", "been", "have", "has", "had", 
    "about", "above", "after", "again", "against", "all", "any", "are", "aren't", "because", 
    "but", "can", "cannot", "could", "couldn't", "did", "didn't", "does", "doesn't", "doing", 
    "don't", "down", "during", "each", "few", "for", "from", "further", "hadn't", "hasn't", 
    "haven't", "having", "here", "how", "into", "its", "itself", "more", "most", "mustn't", 
    "myself", "once", "only", "other", "ought", "ours", "ourselves", "out", "over", "own", 
    "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "some", "such", 
    "than", "then", "there", "there's", "themselves", "these", "they", "they'd", "they'll", 
    "they're", "they've", "this", "those", "through", "under", "until", "very", "was", "wasn't", 
    "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what", "what's", "when", "when's", 
    "where", "where's", "which", "while", "who", "who's", "whom", "why", "why's", "would", "wouldn't"
}

def extract_keywords(text: str) -> set:
    if not text:
        return set()
    # Capture terms like C++, C#, .NET, Node.js, ReactJS, etc.
    words = re.findall(r'\b[a-zA-Z][a-zA-Z+#\.0-9]{1,}\b', text.lower())
    return {w for w in words if w not in STOPWORDS and len(w) > 2 or w in {"c#", "c++", "go", "r"}}

def compute_match(resume_kw: set, jd_kw: set) -> dict:
    matched = list(resume_kw & jd_kw)
    missing = list(jd_kw - resume_kw)
    score = min(100, int((len(matched) / max(len(jd_kw), 1)) * 100))
    label = "Excellent" if score >= 80 else "Good" if score >= 60 else "Needs Work"
    return {
        "score": score,
        "label": label,
        "matched": sorted(matched)[:25],
        "missing": sorted(missing)[:25]
    }
