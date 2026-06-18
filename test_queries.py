from neo4j import GraphDatabase
from retrieval.embed import get_embedder
from retrieval.hybrid import hybrid_retrieve
import json

driver = GraphDatabase.driver(
    "bolt://localhost:7687",
    auth=("neo4j", "testtest")
)

embedder = get_embedder()

queries = [
    "stir-fried spicy chicken with peppercorn and peanuts",
    "silky tofu in fiery sichuan numbing sauce",
    "fresh tomato mozzarella and basil from southern italy",
    "vinegared rice rolled with seaweed and fresh fish",
    "warm tortillas with marinated grilled meat and lime",
    "noodle soup with rich pork broth and toppings",
    "creamy oven-baked layered pasta with meat sauce",
    "fluffy stack of pancakes with maple syrup for breakfast",
]

all_results = {}

for q in queries:
    print("Processing:", q)

    results = hybrid_retrieve(driver, embedder, q, k=10)

    all_results[q] = []

    for r in results[:10]:
        all_results[q].append({
            "recipe_id": r.get("recipe_id"),
            "score": r.get("score") or r.get("final_score"),
            "embedding_score": r.get("embedding_score"),
            "bm25_score": r.get("bm25_score"),
            "title": r.get("title"),
            "ingredients": r.get("ingredients"),
        })


output_file = "retrieval_results.json"

with open(output_file, "w", encoding="utf-8") as f:
    json.dump(all_results, f, indent=2, ensure_ascii=False)

print("\nSaved results to:", output_file)