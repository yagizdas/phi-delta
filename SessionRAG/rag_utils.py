from config import MAIN_PATH, ADDED_FILES, SESSION_BASED_PATHING
import os

def mark_as_added(file_name: str, 
                  session_path: str = None,
                  debug: bool = False) -> None:
    """
    Marks a file as added to the RAG system by appending its name to the added_files.txt.
    """
    if session_path is None:
        raise ValueError("Session path must be provided.")
    
    if debug: 
        print(f"Marking file '{file_name}' as added in session path: {session_path}")

    with open(os.path.join(session_path, ADDED_FILES), 'a') as f:
        f.write(file_name + '\n')


def get_added_files(session_path: str = None) -> set:
    """
    Retrieves the set of files that have already been added to the RAG system.
    """
    if session_path is None:
        raise ValueError("Session path must be provided.")
    
    added_files_path = os.path.join(session_path, ADDED_FILES)

    if not os.path.exists(added_files_path):
        return set()

    with open(added_files_path, 'r') as f:
        added_files = f.read().splitlines()
    
    return set(added_files)

def is_file_added(file_name: str, 
                  session_path: str = None) -> bool:
    """
    Checks if a file has already been added to the RAG system.
    """

    if session_path is None:
        raise ValueError("Session path must be provided.")
    
    added_files = get_added_files(session_path=session_path)
    return file_name in added_files

