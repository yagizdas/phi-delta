from config import MAIN_PATH

def list_directory(filetype: str = None, session_path: str = None) -> list[str]:
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