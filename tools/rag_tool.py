from langchain.schema import Document
from SessionRAG import similarity_search
from config import MAIN_PATH
import os

def rag_search(vectorstore, query: str, file: str = None, debug:bool = False) -> list[Document]:
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
        if debug: raise ValueError("Query Not Found")
        return []

    results = similarity_search(vectorstore=vectorstore, 
                                query=query, 
                                target=file, 
                                debug=debug)
    
    if not results:
        return []

    if debug: 
        print(results)

    return results

def rag_search_wrapper(vectorstore, input_string: str, debug: bool = False) -> list[Document]:
    """
    Wrapper function for rag_search to be used as a tool function.
    
    Args:
        input_string (str): The input string containing the query and file name. This will get parsed to extract the query and file name.
        vectorstore: The vector store to search in.
        debug (bool): Whether to print debug information.

    Returns:
        list[Document]: A list of documents that match the query.
    """
    try:
        # Normalize the input string, remove unnecessary characters, parts etc.
        input_string = input_string.replace("'", "").replace('"', "").replace("{","").replace("}","").replace(MAIN_PATH,"").strip()
        parts = input_string.split(",")
        if debug: print(f"Normalized parts: {parts}")

        query = None
        file = None

        for part in parts:
            try:
                # Ensure clean splitting by stripping spaces around the colon
                key, value = map(str.strip, part.split(":", 1))  # Use `split(":", 1)` to avoid errors with multiple colons
                key = key.lower()
                if debug: print(f"Key: {key}, Value: {value}")
                if "query" in key:
                    query = value
                elif "file" in key:
                    file = value
            except ValueError:
                if debug:
                    print(f"Error parsing part: {part}")
                continue

        if not query:
            raise ValueError("Query is required in the input string.")

        # Perform the RAG search
        return rag_search(vectorstore, query=query, file=file, debug=debug)

    except Exception as e:
        if debug:
            print(f"Error parsing input string: {e}")
        return []