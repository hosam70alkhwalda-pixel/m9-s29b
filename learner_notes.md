# Learner Notes — Stretch Thu (GraphRAG hybrid retrieval)

Use this file to capture your design decisions and what you observed.
It is read by the TA during grading.

## Design decisions

### Vector candidates
- How did you call the Neo4j vector index? Any parameters you tuned?
- Did you experiment with a candidate-k different from the returned-k?

### Traversal
- Did you fetch context lazily (per candidate) or in a single batched
  query? Why?

### Fusion
- You implemented the documented fusion rule. Briefly: where do you
  think this rule under-performs? Sketch one alternative fusion rule
  (e.g., weighted by ingredient overlap, or by hierarchical cuisine
  match) and a quick hypothesis about which queries it would help most.

## Eval observations

- Which of the 8 eval queries did your pipeline retrieve well?
- Which ones surfaced fewer gold ids, and what does the failure look
  like? (Wrong cuisine? Lexically similar but topically distant?)
- What does this suggest about the limits of MiniLM-L6-v2 as the
  embedding choice on a recipe-domain corpus?

## Production framing

GraphRAG hybrid retrieval — vector index + graph traversal fused at
answer time — is a first-class production pattern; it is the same
*schema-bounded NL→evidence* primitive you saw on Weaviate in Module 8
and will see again on the deployment surface in Module 10. The engine
differs (Weaviate's HNSW versus Neo4j's native vector index); the
primitive does not. Note one place where the Neo4j-side fusion gave
you a result that a vector-only Weaviate pipeline could not have
produced.
