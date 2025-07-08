from huggingface_hub import snapshot_download
from config import EMBEDDER_MODEL_NAME
from langchain_community.embeddings import HuggingFaceEmbeddings


def download_embedder():
    """
    Downloads the sentence-transformers/all-MiniLM-L6-v2 model from Hugging Face.
    This model is used for generating embeddings in the SessionRAG framework.
    """
    snapshot_download(
        repo_id=EMBEDDER_MODEL_NAME,
        force_download=True
    )

def setup_embedder():

    """
    Sets up the RAG (Retrieval-Augmented Generation) environment by downloading necessary models.
    """

    print("Setting up RAG environment...")
    download_embedder()
    print("RAG environment setup complete.")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDER_MODEL_NAME, model_kwargs={"device":"cpu"})

    return embeddings

