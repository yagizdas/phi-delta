# config.py

TOOL_DESCRIPTIONS = """
You have access to the following tools:

1. search_tool: Use this to search the web for up-to-date information, including breaking news.
   - Input: a natural language query
   - Output: recent web results related to the query

2. arxiv_search: Use this to search for academic papers in a max_results amount. download_tool can be used AFTER to download the resulting PDFs to local storage for further analysis. Downloading the previously accessed ArXiv links are not possible, it has to be downloaded right away or not. 
   - Input: A JSON string representing a dictionary with a "query" and optional "max_results".
     Example: {"query": "your search query here", "max_results": 3}
   - Output: A formatted string with the titles, summaries, arXiv IDs, and links to the papers.
   - **IMPORTANT** Note: DO NOT go more than 3 max_results. Your system can not handle more than that.

3. rag_search: Use this to perform a similarity search on locally stored documents in the vector store. This tool is ideal for retrieving relevant information from specific files based on a query.
   - Input: A string containing the "query" and an optional "file" name. Example: query: your query here, file: your_file_path.pdf
   - Input: If no file is specified, the tool will search across all available documents in the vector store. Example: "query: your general query here"
   - **Important** Input: Query should be one, if you want to search multiple queries, you have to use the rag_tool multiple times.
   - Output: A list of relevant document extractions matching the query.
   - Note: Use this tool to retrieve specific information from documents you have previously added to the system. It is particularly useful for academic papers, reports, or any text-based files you have stored in the vector store.
   - Important Note: The file names that are added to the vector store are the same as the file names in the "./model_files/" directory, so you can use the list_directory_tool to check the files you have in your directory first.

4. code_tool: Executes Python code.
   - Input: a Python expression or block
   - Output: the result of code execution (e.g., calculations, data analysis)

5. multimodal_tool: Use this to analyze or interpret visual content in images or PDF files. Not intended for use for full RAG tasks, but rather for quick visual analysis. 
   You should use the rag_tool for more extensive RAG tasks. 
   You should use this tool when you want to analyze a specific image or PDF page, a graph or an image on a pdf, not for general RAG tasks. 
   This tools usage is very resource heavy, so use it wisely and pick rag_tool if it is possible.
   Note: This tool is not intended for full RAG tasks, but rather for quick visual analysis. It would work ideal for analyzing a specific image or PDF page, a graph or an image on a pdf, not general PDF analysis.
   - Input: an image or a PDF file (plus an optional page number if PDF), and a natural language prompt (e.g., "What does this chart show?" or "Summarize the content of page 2.")
   - Output: A detailed answer, interpretation, or description based on the visual input, including reasoning over text, structure, layout, and imagery.

6. download_tool:
Use this tool immediately after running arxiv_search to download one or more of the papers that were just retrieved.
This is the only way to save papers locally for deeper analysis.
Important:
When specifying which papers to download, you must provide a list of indices starting from 1, not 0.
    ✅ Correct: [1] for the first paper, [2, 3] for the second and third papers
    ❌ Incorrect: [0] (there is no zero-based indexing)
Input:
A list of indices corresponding to the papers shown in the most recent arxiv_search results.
Output:
A confirmation message listing the saved files and their directory.

7. list_directory_tool: Use this to check your directory. You can check out the previous files that are downloaded before you to gather information about their name to further analysis on the next steps.
   - Input: "" for listing ALL files, or "pdf", "jpeg" etc. to filter-search with special file types.
   - Output: The directories of the specified folders

8. wolfram_search: Queries the Wolfram Alpha API for factual or computational answers. It is faster than the search_tool, but it is not as up-to-date as the search_tool.
   - Input: a natural language question or expression
   - Output: Wolfram Alpha’s computed result
   - Example: "Derivative of sin(x)", "Population of Turkey in 2023", "Solve x^2 + 5x + 6 = 0"

You are only allowed to plan steps that use these tools. Do not mention subscribing to newsletters, downloading apps, or using external social media platforms.

You need to only solve the task. Do not add something suggestive.
"""

TOOL_DESCRIPTIONS_DICT = parse_tool_descriptions(TOOL_DESCRIPTIONS)

RAG_TOOL_DESCRIPTIONS = """
You have access to the following tools:

1. multimodal_tool: Use this to analyze or interpret visual content in images or PDF files. Not intended for use for full RAG tasks, but rather for quick visual analysis. 
   You should use the rag_tool for more extensive RAG tasks. 
   You should use this tool when you want to analyze a specific image or PDF page, a graph or an image on a pdf, not for general RAG tasks. 
   This tools usage is very resource heavy and time consuming, so use it wisely and pick rag_tool if it is possible.
   Note: This tool is not intended for full RAG tasks, but rather for quick visual analysis. It would work ideal for analyzing a specific image or PDF page, a graph or an image on a pdf, not general PDF analysis.
   - Input: an image or a PDF file (plus an optional page number if PDF), and a natural language prompt (e.g., "What does this chart show?" or "Summarize the content of page 2.")
   - Output: A detailed answer, interpretation, or description based on the visual input, including reasoning over text, structure, layout, and imagery.

2. list_directory_tool: Use this to check your directory. You can check out the previous files that are downloaded before you to gather information about their name to further analysis on the next steps.
   - Input: "" for listing ALL files, or "pdf", "jpeg" etc. to filter-search with special file types.
   - Output: The directories of the specified folders

3. rag_search: Use this to perform a similarity search on locally stored documents in the vector store. This tool is ideal for retrieving relevant information from specific files based on a query.
   - Input: A string containing the "query" and an optional "file" name. Example: query: your query here, file: your_file_path.pdf
   - Input: If no file is specified, the tool will search across all available documents in the vector store. Example: "query: your general query here"
   - **Important** Input: Query should be one, if you want to search multiple queries, you have to use the rag_tool multiple times.
   - Output: A list of relevant document extractions matching the query.
   - Note: Use this tool to retrieve specific information from documents you have previously added to the system. It is particularly useful for academic papers, reports, or any text-based files you have stored in the vector store.
   - Important Note: The file names that are added to the vector store are the same as the file names in the "./model_files/" directory, so you can use the list_directory_tool to check the files you have in your directory first.


You are only allowed to plan steps that use these tools. Do not mention subscribing to newsletters, downloading apps, or using external social media platforms.

You need to only solve the task. Do not add something suggestive. 

"""

RAG_TOOL_DESCRIPTIONS_DICT = parse_tool_descriptions(RAG_TOOL_DESCRIPTIONS)

RAG_TOOL_DESCRIPTIONS = """
You have access to the following tools:

1. multimodal_tool: Use this to analyze or interpret visual content in images or PDF files. Not intended for use for full RAG tasks, but rather for quick visual analysis. 
   You should use the rag_tool for more extensive RAG tasks. 
   You should use this tool when you want to analyze a specific image or PDF page, a graph or an image on a pdf, not for general RAG tasks. 
   This tools usage is very resource heavy and time consuming, so use it wisely and pick rag_tool if it is possible.
   Note: This tool is not intended for full RAG tasks, but rather for quick visual analysis. It would work ideal for analyzing a specific image or PDF page, a graph or an image on a pdf, not general PDF analysis.
   - Input: an image or a PDF file (plus an optional page number if PDF), and a natural language prompt (e.g., "What does this chart show?" or "Summarize the content of page 2.")
   - Output: A detailed answer, interpretation, or description based on the visual input, including reasoning over text, structure, layout, and imagery.

2. list_directory_tool: Use this to check your directory. You can check out the previous files that are downloaded before you to gather information about their name to further analysis on the next steps.
   - Input: "" for listing ALL files, or "pdf", "jpeg" etc. to filter-search with special file types.
   - Output: The directories of the specified folders

3. rag_search: Use this to perform a similarity search on locally stored documents in the vector store. This tool is ideal for retrieving relevant information from specific files based on a query.
   - Input: A string containing the "query" and an optional "file" name. Example: query: your query here, file: your_file_path.pdf
   - Input: If no file is specified, the tool will search across all available documents in the vector store. Example: "query: your general query here"
   - **Important** Input: Query should be one, if you want to search multiple queries, you have to use the rag_tool multiple times.
   - Output: A list of relevant document extractions matching the query.
   - Note: Use this tool to retrieve specific information from documents you have previously added to the system. It is particularly useful for academic papers, reports, or any text-based files you have stored in the vector store.
   - Important Note: The file names that are added to the vector store are the same as the file names in the "./model_files/" directory, so you can use the list_directory_tool to check the files you have in your directory first.


You are only allowed to plan steps that use these tools. Do not mention subscribing to newsletters, downloading apps, or using external social media platforms.

You need to only solve the task. Do not add something suggestive. 

"""



MAIN_PATH = "./model_files/"

LLM_PORT = "http://localhost:8000/v1"

MODEL_NAME= "phi-4-IQ4_XS"

EMBEDDER_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

ADDED_FILES = "added_files.txt"

SESSION_BASED_PATHING = "sessions/session_{session_id}/"
