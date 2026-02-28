def retrieve_documents(vector_store, query, k=4):
    return vector_store.similarity_search(
        query,
        k=k,
    )
