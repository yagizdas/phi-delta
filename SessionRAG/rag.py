from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.in_memory import InMemoryDocstore
import os
import faiss

from config import MAIN_PATH
from .setup_emb import setup_embedder
from .rag_utils import mark_as_added, is_file_added

from langchain_community.vectorstores import Chroma

from utils import create_session_id, create_session_directory


ADDED_FILES = "added_files.txt"

def init_rag(embedding = None, session_id = None) -> tuple:
    """
    Initializes the RAG system with a vector store and embeddings.
    If no embedding is provided, it initializes a new HuggingFace embedding model.
    If no session_id is provided, it creates a new session ID and directory, NOT recommended.
    Args:
        embedding: Optional, a pre-initialized embedding model.
        session_id: Optional, a pre-defined session ID.
    Returns:
        tuple: A tuple containing the vector store and embeddings.
    """
    if embedding is None:
        print("Initializing the embedder...")
        embeddings = setup_embedder()
    else:
        embeddings = embedding

    # Chroma vectorstore alternative is used, replacing FAISS
    """
    # Get embedding dimension from dummy query
    dim = len(embeddings.embed_query("dummy"))

    # Initialize empty FAISS index
    #index = faiss.IndexFlatL2(dim)

    # Empty docstore and ID map
    docstore = InMemoryDocstore({})
    index_to_docstore_id = {}

   
    # Create empty FAISS vector store
    faiss_vectorstore = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )
    """
    session_path = create_session_directory(session_id=session_id)

    persist_directory = f"./{session_path}/utils/chroma_db"

    # Chroma vectorstore alternative initialization
    chroma_vectorstore = Chroma(
        collection_name=f"chat_{session_id}",
        embedding_function=embeddings,
        persist_directory=persist_directory  # Directory to store the collection
    )
    
    vectorstore = chroma_vectorstore

    print(f"RAG system initialized with session ID: {session_id}")
    print(f"Documents:{vectorstore.get()['documents']}")
    print(f"metadatas:{vectorstore.get()['metadatas']}")


    return vectorstore, embeddings


def add_to_rag(vectorstore, 
               session_path: str,
               debug: bool = False) -> None:
    """
    Adds new documents to the existing FAISS vector store.
    Args:
        vectorstore: The vector store to add documents to.
        session_path: The path to the session directory containing PDF files.
        debug: If True, enables debug mode for additional logging.
    Returns:
        None
    """
    files = os.listdir(session_path)

    if not files:
        print("No PDF files found in the specified directory, Skipping...")
        return
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        for file in files:

            if is_file_added(file_name=file, 
                             session_path=session_path,):
                
                if debug:
                    print("✅ File already added to RAG system, Skipping...")

                continue

            if file.endswith('.pdf'):

                loader = PyMuPDFLoader(os.path.join(session_path, file))
                docs = loader.load()

                for doc in docs:
                    doc.metadata["source"] = file

                splits = text_splitter.split_documents(docs)

                vectorstore.add_documents(splits)
                mark_as_added(file, session_path)

                if debug:
                    print(f"✅ Added {file} to RAG system.")

    except Exception as e:
        print(f"❌ Error while adding files to RAG system: {e}")
        raise e
    
def similarity_search(vectorstore, 
                      query: str, 
                      target:str = None, 
                      k: int = 4,
                      debug: bool = False) -> str:
    """
    Performs a similarity search on the specified vector store.
    Args:
        vectorstore: The vector store to search in.
        query (str): The query string to search for.
        target (str): Optional, a specific document to filter results by.
        k (int): The number of results to return. Default is 4.
        debug (bool): If True, enables debug mode for additional logging.
    Returns:
        str: A shortened response based on the search results. 
    """
    if not query: 
        return "❌ ERROR: Query cannot be empty."
    
    try:
        if target: 
            if debug: print(f"Target: {target}\n")

            results = vectorstore.similarity_search(query=query,
                                                        k=k,
                                                        filter={"source":target})
            short = 300
            
        else:
            if debug: print("No target specified, searching across all documents.")

            results = vectorstore.similarity_search(query=query, 
                                                    k=k)
            short = 600
            
        results_summary = "\n".join(
            [f"- {doc.page_content[:short].strip()}" for doc in results]
            )

        #if debug: print(f"Type: {type(results[0])}\n Results: {results}\n")

        ## Format results for better readability for the model. Summarizes the content


        return results_summary

    except Exception as e:
        return f"❌ Error during similarity search: {e}"

def reset_rag(vectorstore) -> None:
    """
    Resets the RAG system by clearing the vector store.
    Args:
        vectorstore: The vector store to reset.
    Returns:
        None
    """
    try:
        # Delete the collection if it exists
        vectorstore.delete_collection()
        print("RAG system reset successfully.")
    except Exception as e:
        if "does not exist" in str(e):
            print("Collection does not exist. Initializing a new collection.")
        else:
            print(f"❌ Error while resetting RAG system: {e}")
            raise e

if __name__ == "__main__":
    # For testing purposes only, will be removed soon.

    vector_store, embeddings = init_rag()
    print("RAG system initialized with empty vector store.")

    session_id = create_session_id()

    print(f"Session ID: {session_id}\n")

    session_path = create_session_directory(session_id=session_id)
    
    print(f"Session Path: {session_path}\n")

    # Add to RAG
    add_to_rag(vector_store, session_path=session_path, debug=True)
    print("RAG system updated with new documents.")

    # Test similarity search
    query = "abstract"

    results = similarity_search(vectorstore=vector_store, 
                                query=query, 
                                target="Albert_Einstein:_Rebellious_Wunderkind.pdf", 
                                debug=True)

    print(f"Found {len(results)} relevant documents for the query '{query}':")
    print(results)
#     print("Similarity search completed.")
