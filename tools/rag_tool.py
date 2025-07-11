from langchain.schema import Document
from SessionRAG import similarity_search

def rag_search(query: str, file: str, vectorstore, embeddings) -> list[Document]:
    """
    Perform a similarity search in the vector store and return the results.

    Args:
        query (str): The query string to search for.
        vectorstore: The vector store to search in.
        embeddings: The embeddings used for the search.

    Returns:
        list[Document]: A list of documents that match the query.
    """
    if not query.strip():
        return []

    results = similarity_search(query, vectorstore, target=file)
    
    if not results:
        return []

    return results