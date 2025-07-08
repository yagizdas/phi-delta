from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.document_loaders import PyMuPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

import os

from config import MAIN_PATH
from .setup_emb import setup_embedder
from .rag_utils import mark_as_added, is_file_added

ADDED_FILES = "added_files.txt"

def init_rag():

    embeddings = setup_embedder()

    #docs are empty for initialization
    docs = []

    embeddings = setup_embedder()

    vector_store = FAISS.from_documents(docs, embeddings)

    return vector_store, embeddings


def add_to_rag(vector_store: FAISS, embeddings: HuggingFaceEmbeddings = None, pdfs_path: str = MAIN_PATH):
    """
    Adds new documents to the existing FAISS vector store.
    """
    files = os.listdir(pdfs_path)

    if not files:
        raise FileNotFoundError("No PDF files found in the specified directory.")
    try:
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

        for file in files:

            if is_file_added(file, pdfs_path):
                print("✅ File already added to RAG system, Skipping...")
                continue

            if file.endswith('.pdf'):

                loader = PyMuPDFLoader(os.path.join(pdfs_path, file))
                docs = loader.load()
                splits = text_splitter.split_documents(docs)
                vector_store.add_documents(splits)
                mark_as_added(file)
                print(f"✅ Added {file} to RAG system.")

    except Exception as e:
        print(f"❌ Error while adding files to RAG system: {e}")
        raise e
    
if __name__ == "__main__":
    # For testing purposes only
    vector_store, embeddings = init_rag()
    print("RAG system initialized with empty vector store.")
    
    
    # Add to RAG
    add_to_rag(vector_store, embeddings)
    print("RAG system updated with new documents.")