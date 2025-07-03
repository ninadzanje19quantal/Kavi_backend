from vector_db import embedding_fn, collection

query = "Best general questions for a Designer Junior level"
query_embeddings = embedding_fn([query])

results = collection.query(
    query_embeddings=query_embeddings,
    n_results=3,
)

