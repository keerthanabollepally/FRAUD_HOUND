from agent_graph import build_fraud_graph

graph = build_fraud_graph()

result = graph.invoke({
    "flagged_jobs": [],
    "undercover_results": [],
    "fraud_rings": [],
    "decisions": []
})

print("\nFINAL GRAPH OUTPUT:\n")
print(result)
