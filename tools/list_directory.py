from config import MAIN_PATH

def list_directory(filetype: str = None, session_path: str = None) -> list[str]:
    """
    Agentic tool for listing files in a directory.
    Lists files in the specified directory, optionally filtering by file extension.
    If no filetype is specified, lists all files.
    Args:
        filetype (str): Optional file extension to filter files (e.g., 'pdf').
        session_path (str): Path to the directory to list files from.
    Returns:
        list[str]: Sorted list of file names in the directory.
    """
    import os

    try:
        files = os.listdir(session_path)

        if filetype:
            return sorted([f for f in files if f.endswith(filetype)])
        
        print(f"\nListing files in directory: {session_path}\n")

        return sorted(files)
    
    except Exception as e:
        return [f"Error listing directory: {e}"]

def list_files_tool_wrapper(input: str = "", session_path: str = None) -> list[str]:

    filetype = input.strip() or None

    print(f"\n Listing files with filetype: {filetype}")

    return list_directory(filetype=filetype, session_path=session_path)