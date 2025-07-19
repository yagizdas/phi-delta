from config import MAIN_PATH

def list_directory(filetype: str = None, directory: str = MAIN_PATH) -> list[str]:
    import os

    try:
        files = os.listdir(directory)

        if filetype:
            return sorted([f for f in files if f.endswith(filetype)])
        
        print(f"\nListing files in directory: {directory}\n")

        return sorted(files)
    
    except Exception as e:
        return [f"Error listing directory: {e}"]

def list_files_tool_wrapper(input: str = ""):

    filetype = input.strip() or None

    print(f"\n Listing files with filetype: {filetype}")

    return list_directory(filetype=filetype)