import chromadb
from vector_db import embedding_fn


def make_query(collection_name: str, default_query_prompt: str, summary_prompt: str):
    chroma_client = chromadb.Client()
    try:
        collection = chroma_client.get_collection(name=collection_name)
    except:
        return {"Error": "Collection does not exist"}
    query = default_query_prompt + summary_prompt
    query_embeddings = embedding_fn([query])

    results = collection.query(
        query_embeddings=query_embeddings,
        n_results=3,
    )

    return results, query
