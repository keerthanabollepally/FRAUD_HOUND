import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

class PatternHunterAgent:
    def __init__(self, similarity_threshold=0.75):
        self.similarity_threshold = similarity_threshold
        try:
            self.model = SentenceTransformer("all-MiniLM-L6-v2")
        except:
            print("Embedding model failed. Using rule-based clustering.")
            self.model = None

    def detect_fraud_rings(self, undercover_results):
        scam_cases = [r for r in undercover_results if r["scam_detected"]]
        if not scam_cases:
            return []

        # TRY EMBEDDINGS FIRST
        try:
            if self.model:
                return self._embedding_clusters(scam_cases)
            else:
                raise Exception("No embedding model")
        except:
            print("Embeddings failed. Using rule-based clustering.")
            return self._rule_clusters(scam_cases)

    def _embedding_clusters(self, scam_cases):
        texts = [" ".join([m["message"] for m in case["conversation"]]) for case in scam_cases]
        embeddings = self.model.encode(texts)
        
        clusters = []
        used = set()
        for i in range(len(embeddings)):
            if i in used: continue
            cluster = [i]
            used.add(i)
            for j in range(i + 1, len(embeddings)):
                if j in used: continue
                sim = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
                if sim >= self.similarity_threshold:
                    cluster.append(j)
                    used.add(j)
            clusters.append(cluster)
        
        return self._format_rings(scam_cases, clusters)

    def _rule_clusters(self, scam_cases):
        """Rule-based: group by phone/email/keywords"""
        clusters = {}
        for case in scam_cases:
            text = " ".join([m["message"].lower() for m in case["conversation"]])
            # Extract identifiers
            key = "unknown"
            if any(x in text for x in ["telegram", "whatsapp"]):
                key = "messaging_scam"
            elif "upi" in text or "pay" in text:
                key = "payment_scam"
            if key not in clusters:
                clusters[key] = []
            clusters[key].append(case)
        
        # Format as rings
        rings = []
        for idx, (key, cases) in enumerate(clusters.items()):
            rings.append({
                "ring_id": f"rule_cluster_{idx}_{key}",
                "job_ids": [case["job_id"] for case in cases],
                "ring_size": len(cases)
            })
        return rings

    def _format_rings(self, scam_cases, clusters):
        fraud_rings = []
        for idx, cluster in enumerate(clusters):
            job_ids = [scam_cases[i]["job_id"] for i in cluster]
            fraud_rings.append({
                "ring_id": f"cluster_{idx}",
                "job_ids": job_ids,
                "ring_size": len(job_ids)
            })
        return fraud_rings
