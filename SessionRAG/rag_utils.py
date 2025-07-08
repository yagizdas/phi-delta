from config import MAIN_PATH, ADDED_FILES
import os

def mark_as_added(file_name: str, pdfs_path: str = MAIN_PATH):
    """
    Marks a file as added to the RAG system by appending its name to the added_files.txt.
    """
    with open(os.path.join(pdfs_path, ADDED_FILES), 'a') as f:
        f.write(file_name + '\n')

def get_added_files(pdfs_path: str = MAIN_PATH) -> set:
    """
    Retrieves the set of files that have already been added to the RAG system.
    """
    added_files_path = os.path.join(pdfs_path, ADDED_FILES)
    if not os.path.exists(added_files_path):
        return set()

    with open(added_files_path, 'r') as f:
        added_files = f.read().splitlines()
    
    return set(added_files)

def if_file_added(file_name: str, pdfs_path: str = MAIN_PATH) -> bool:
    """
    Checks if a file has already been added to the RAG system.
    """
    added_files = get_added_files(pdfs_path)
    return file_name in added_files