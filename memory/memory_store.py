import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

class FraudMemory:
    def __init__(self, dim=384):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = faiss.IndexFlatL2(dim)
        self.metadata = []

    def add(self, text, meta):
        vec = self.model.encode([text]).astype("float32")
        self.index.add(vec)
        self.metadata.append(meta)

    def search(self, text, k=3):
        if self.index.ntotal == 0:
            return []

        vec = self.model.encode([text]).astype("float32")
        _, idxs = self.index.search(vec, k)

        return [self.metadata[i] for i in idxs[0] if i < len(self.metadata)]


# 🔥 SINGLETON MEMORY INSTANCE
fraud_memory = FraudMemory()
