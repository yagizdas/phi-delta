from huggingface_hub import snapshot_download
from config import EMBEDDER_MODEL_NAME
from langchain_community.embeddings import HuggingFaceEmbeddings

_embedder_cache = None

def download_embedder():
    """
    Downloads the sentence-transformers/all-MiniLM-L6-v2 model from Hugging Face.
    This model is used for generating embeddings in the SessionRAG framework.
    """
    snapshot_download(
        repo_id=EMBEDDER_MODEL_NAME,
        force_download=False
    )

def setup_embedder():
    """
    Sets up the RAG (Retrieval-Augmented Generation) environment by downloading necessary models.
    """
    global _embedder_cache
    
    if _embedder_cache is not None:
        print("Embedder already set up, skipping download.")
        return _embedder_cache
    
    print("Setting up RAG environment...")
    download_embedder()
    print("RAG environment setup complete.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME, model_kwargs={"device":"cpu"})
    _embedder_cache = embeddings

    return embeddings

def reset_embedder():
    """
    Resets the embedder cache.
    This is useful for reinitializing the embedder if needed.
    """
    global _embedder_cache
    _embedder_cache = None
    print("Embedder cache reset.")