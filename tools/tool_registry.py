from langchain_community.tools import TavilySearchResults
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_community.utilities import ArxivAPIWrapper
from langchain.tools import Tool
from langchain.agents import load_tools
from langchain.tools import StructuredTool

from . import phi4multimodal

from .arxiv_tool import search_arxiv_tool_input
from .download_arxiv_pdfs import download_arxiv_pdfs
from .list_directory import list_files_tool_wrapper

def initialize_tools(memory : list = []) -> list[Tool]:
    """
    Initialize the tools used in the application.
    
    Args:
        memory: An object that stores state, such as arxiv links.
    
    Returns:
        A list of initialized tools.

    """
    search_tool = TavilySearchResults(max_results = 5, include_answer = True)
    code_tool = PythonREPLTool()
    multimodal_tool = phi4multimodal.Phi4MMTool()

    #arxiv = ArxivAPIWrapper(top_k_results=3)

    arxiv_tool = StructuredTool.from_function(
        name="arxiv_search",

        func=search_arxiv_tool_input,

        description=(
            "Searches ArXiv for academic papers. "
            "Accepts a dictionary with 'query' (str), and 'max_results' (int). "
            "Example input: {'query': 'quantum entanglement', 'max_results': 5}"
        )

    )

    download_tool = Tool.from_function(

        name="download_arxiv_pdfs",
        func=lambda _: download_arxiv_pdfs(memory),  # return just the message
        description="Downloads the PDF versions of academic papers from the last arxiv_search. It saves them locally for extensive analysis of the academic resources."

    )


    list_files_tool = Tool.from_function(

        name="list_files",
        func=list_files_tool_wrapper,
        description="Lists files in the directory. Optionally filter by file extension like 'pdf'."

    )

    tools = [search_tool, code_tool, multimodal_tool, arxiv_tool, download_tool, list_files_tool]

    return tools
