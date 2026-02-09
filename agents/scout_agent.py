import pandas as pd
from llm_utils import llm_risk_analysis

class ScoutAgent:
    def calculate_risk_score(self, row):
        """FIXED: Ensures score is always float"""
        message = str(row.get("description", ""))
        result = llm_risk_analysis(message)
        
        # CRITICAL: Convert string scores to float
        try:
            score = float(result.get("risk_score", 0.5))
        except (ValueError, TypeError):
            score = 0.5  # Default safe value
            
        reasons = result.get("reasons", [])
        suggestion = result.get("suggestion", "")
        
        return score, reasons, suggestion

    def scan_jobs(self, csv_path=None, df=None, threshold=0.4):
        if df is None:
            df = pd.read_csv(csv_path)

        results = []
        for idx, row in df.iterrows():  # Use idx for job_id if missing
            score, reasons, suggestion = self.calculate_risk_score(row)
            
            
            if score >= threshold:
                results.append({
                    "job_id": row.get("job_id", idx),
                    "job_title": row.get("job_title", "Unknown"),
                    "platform": row.get("platform", "Unknown"),
                    "description": row.get("description", ""),
                    "risk_score": score,
                    "reasons": reasons,
                    "suggestion": suggestion
                })
        return pd.DataFrame(results)
