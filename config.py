TOOL_DESCRIPTIONS = """
You have access to the following tools:

1. search_tool: Use this to search the web for up-to-date information, including breaking news.
   - Input: a natural language query
   - Output: recent web results related to the query

2. arxiv_search: Use this to search for academic papers in a max_results amount. download_tool can be used AFTER to download the resulting PDFs to local storage for further analysis. Downloading the previously accessed ArXiv links are not possible, it has to be downloaded right away or not. 
   - Input: A JSON string representing a dictionary with a "query" and optional "max_results".
     Example: {"query": "your search query here", "max_results": 3}
   - Output: A formatted string with the titles, summaries, arXiv IDs, and links to the papers.
   - Note: DO NOT go more than 5 max_results...

3. code_tool: Executes Python code.
   - Input: a Python expression or block
   - Output: the result of code execution (e.g., calculations, data analysis)

4. multimodal_tool: Use this to analyze or interpret visual content in images or PDF files. 
   - Input: an image or a PDF file (plus an optional page number if PDF), and a natural language prompt (e.g., "What does this chart show?" or "Summarize the content of page 2.")
   - Output: A detailed answer, interpretation, or description based on the visual input, including reasoning over text, structure, layout, and imagery.

5. download_tool: Use this to download the previously accessed academic papers with arxiv_search tool. You can ONLY use this tool after you use arxiv_search, and it will only download tha papers you searched exactly before this tool.
   - Input: The indices of the papers you want to download, in a list format. Example: [1, 2, 3] where the numbers correspond to the indices of the papers in the last arxiv_search result.
   - Note: The first index is 1, not 0. If you want to download the first paper, you have to input [1].
   - Output: Downloading the Papers searched before to gather a deep analysis on them. The files will be saved in the "./model_files/" directory, and the output will be a message about the success of the download and the paths of the downloaded files.

6. list_directory_tool: Use this to check your directory. You can check out the previous files that are downloaded before you to gather information about their name to further analysis on the next steps.
   - Input: "" for listing ALL files, or "pdf", "jpeg" etc. to filter-search with special file types.
   - Output: The directories of the specified folders

You are only allowed to plan steps that use these tools. Do not mention subscribing to newsletters, downloading apps, or using external social media platforms.

You need to only solve the task. Do not add something suggestive.
"""

MAIN_PATH = "./model_files/"

LLM_PORT = "http://localhost:8000/v1"

MODEL_NAME= "phi-4-IQ4_XS"

EMBEDDER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

ADDED_FILES_PATH = "added_files.txt"
