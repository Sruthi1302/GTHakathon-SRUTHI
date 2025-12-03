from typing import List, Dict


class SimpleRAG:
    """Very simple keyword-based retrieval over a list of docs."""

    def __init__(self):
        self.docs: List[Dict] = []

    def build_index(self, docs: List[Dict]):
        self.docs = docs or []

    def _score(self, text: str, query: str) -> int:
        text_lower = text.lower()
        words = set(query.lower().split())
        score = 0
        for w in words:
            if w and w in text_lower:
                score += 1
        return score

    def query(self, query: str, top_k: int = 3) -> List[Dict]:
        if not query or not self.docs:
            return []
        scored = []
        for doc in self.docs:
            s = self._score(doc.get("text", ""), query)
            if s > 0:
                scored.append((s, doc))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [d for _, d in scored[:top_k]]
