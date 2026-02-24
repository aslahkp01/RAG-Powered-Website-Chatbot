def retrieve_documents(vector_store, query, k=5):
    return vector_store.max_marginal_relevance_search(
        query,
        k=k,
        fetch_k=20
    )
