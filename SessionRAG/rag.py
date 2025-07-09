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

ADDED_FILES = "added_files.txt"

def init_rag():

    embeddings = setup_embedder()

    # Get embedding dimension from dummy query
    dim = len(embeddings.embed_query("dummy"))

    # Initialize empty FAISS index
    index = faiss.IndexFlatL2(dim)

    # Empty docstore and ID map
    docstore = InMemoryDocstore({})
    index_to_docstore_id = {}

    # Create empty FAISS vector store
    vector_store = FAISS(
        embedding_function=embeddings,
        index=index,
        docstore=docstore,
        index_to_docstore_id=index_to_docstore_id,
    )
    
    return vector_store, embeddings


def add_to_rag(vector_store: FAISS, embeddings: HuggingFaceEmbeddings = None, pdfs_path: str = MAIN_PATH, debug: bool = False) -> None:
    """
    Adds new documents to the existing FAISS vector store.
    """
    files = os.listdir(pdfs_path)

    if not files:
        raise FileNotFoundError("No PDF files found in the specified directory.")
    
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        for file in files:

            if is_file_added(file):
                
                if debug:
                    print("✅ File already added to RAG system, Skipping...")

                continue

            if file.endswith('.pdf'):

                loader = PyMuPDFLoader(os.path.join(pdfs_path, file))
                docs = loader.load()
                splits = text_splitter.split_documents(docs)

                vector_store.add_documents(splits)
                mark_as_added(file)

                if debug:
                    print(f"✅ Added {file} to RAG system.")

    except Exception as e:
        print(f"❌ Error while adding files to RAG system: {e}")
        raise e
    
def similarity_search(query: str, vector_store: FAISS, k: int = 4) -> list[Document]:
    """
    Performs a similarity search on the vector store.
    """
    if not query:
        return "ERROR: Query cannot be empty."
    
    results = vector_store.similarity_search(query, k=k)
    results_summary = ""
    for doc in results:
        results_summary  += f"- {doc.page_content[:600]}...\n"

    return results_summary
    
if __name__ == "__main__":
    # For testing purposes only
    vector_store, embeddings = init_rag()
    print("RAG system initialized with empty vector store.")

    # Add to RAG
    add_to_rag(vector_store, embeddings)
    print("RAG system updated with new documents.")

    # Test similarity search
    query = "Climate policy under the Obama administration"
    results = similarity_search(query, vector_store)
    print(f"Found {len(results)} relevant documents for the query '{query}':")
    for doc in results:
        print(f"- {doc.page_content[:600]}...")
#     print("Similarity search completed.")
