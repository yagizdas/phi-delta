import requests
from pathlib import Path
from typing import List, Tuple
from config import MAIN_PATH

def download_arxiv_pdfs(links: List[str], save_directory: str = MAIN_PATH) -> Tuple[str, List[str]]:
    
    downloaded_file_paths = []

    def convert_to_pdf_url(url: str) -> str:
        if "arxiv.org/abs/" in url:
            return url.replace("/abs/", "/pdf/") + ".pdf"
        elif "arxiv.org/pdf/" in url and not url.endswith(".pdf"):
            return url + ".pdf"
        return url

    Path(save_directory).mkdir(parents=True, exist_ok=True)

    for arxiv_url,doc_name in links:
        
        pdf_url = convert_to_pdf_url(arxiv_url)

        # Better Document Names
        doc_name = doc_name.replace(" ", "_").replace("/","-") + ".pdf"

        filepath = Path(save_directory) / doc_name 

        try:
            response = requests.get(pdf_url)
            response.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Downloaded to: {filepath}")
            downloaded_file_paths.append(str(filepath))
        except Exception as e:
            print(f"❌ Failed to download {pdf_url}: {e}")

    summary_msg = f"Successfully downloaded {len(downloaded_file_paths)} PDFs."
    return summary_msg, downloaded_file_paths

