import requests
from pathlib import Path
from typing import List, Tuple
from config import MAIN_PATH
import ast
import re 
from SessionRAG import add_to_rag

def bound_download_tool(input_indices_str, links, vectorstore, session_path: str = MAIN_PATH) -> Tuple[str, List[str]]:
    """
    Wrapper function for the download tool for agent use.
    Accepts a string of indices, converts it to a list, and calls the download function.
    """
    print(f"\n\n\n\n\n\nDownload tool invoked, Input indices string: {input_indices_str}\n\n\n\n\n")
    input_indices = ast.literal_eval(input_indices_str)  # Converts "[1, 2]" -> [1, 2]
    return download_arxiv_pdfs(input_indices, links, vectorstore, save_directory=session_path)

def download_arxiv_pdfs(choices: List[int], links: List[str], vectorstore, save_directory: str = MAIN_PATH) -> Tuple[str, List[str]]:
    """Downloads PDFs from ArXiv based on user choices and saves them to a specified directory.
    Args:
        choices (List[int]): List of indices of papers to download.
        links (List[str]): List of tuples containing paper links and titles.
        vectorstore: Vector store for RAG.
        save_directory (str): Directory where PDFs will be saved.
    Returns:
        Tuple[str, List[str]]: Summary message and list of downloaded file paths.
    """
    print(f"Choices: {choices}")
    print(f"Links: {links}")
    print(f"Save directory: {save_directory}")

    downloaded_file_paths = []

    def convert_to_pdf_url(url: str) -> str:
        if "arxiv.org/abs/" in url:
            return url.replace("/abs/", "/pdf/") + ".pdf"
        elif "arxiv.org/pdf/" in url and not url.endswith(".pdf"):
            return url + ".pdf"
        return url

    Path(save_directory).mkdir(parents=True, exist_ok=True)

    for choice in choices:
        if choice <= 0 or choice > len(links):
            print(f"❌ Invalid choice: {choice}. Try again.")
            continue
        
        print(links[choice-1])
        
        pdf_url = convert_to_pdf_url(links[choice-1][0])

        doc_name = links[choice-1][-1]
        # Better Document Names
        doc_name = re.sub(r'[^\w]', '_', doc_name) + ".pdf"
        
        filepath = Path(save_directory) / doc_name

        print(f"Downloading {pdf_url} to {filepath}...") 

        try:
            response = requests.get(pdf_url)
            print(f"Response status: {response}")
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Downloaded to: {filepath}")
            downloaded_file_paths.append(str(filepath))
            # Add to RAG
            print(f"✅ Adding {filepath} to RAG at {save_directory}")
            add_to_rag(vectorstore=vectorstore, session_path=save_directory)


        except Exception as e:
            print(f"❌ Failed to download {pdf_url}: {e}")

    summary_msg = f"Successfully downloaded {len(downloaded_file_paths)} PDFs."
    return summary_msg, downloaded_file_paths

