from langchain_community.tools import TavilySearchResults
from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain_community.utilities import ArxivAPIWrapper
from langchain.tools import Tool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.tools import StructuredTool

from . import phi4multimodal

from memory.memory import AgentMemory

from .arxiv_tool import search_arxiv_tool_input
from .download_arxiv_pdfs import bound_download_tool
from .list_directory import list_files_tool_wrapper

import json

def initialize_tools(memory : AgentMemory) -> list[Tool]:
    """
    Initialize the tools used in the application.
    
    Args:
        memory: An object that stores state, such as arxiv links.
    
    Returns:
        A list of initialized tools.

    """
    search_tool = TavilySearchResults(max_results = 5, 
                                      include_answer = True)

    code_tool = PythonREPLTool()

    multimodal_tool = phi4multimodal.Phi4MMTool()

    arxiv_tool = Tool.from_function(
        name="arxiv_search",
        func=lambda input_data: search_arxiv_tool_input(input_data, memory),
        description=(
            "Searches ArXiv for academic papers. "
            "Accepts a dictionary with 'query' (str), and 'max_results' (int). "
            "Example input: {'query': 'your query here', 'max_results': 'your max results here'}"
        )
    )
    
    download_tool = Tool.from_function(

        name="download_arxiv_pdfs",
        func=lambda input_data: bound_download_tool(input_data, memory.arxiv_links),  # return just the message
        description=("Downloads the PDF versions of academic papers from the last arxiv_search. It saves them locally for extensive analysis of the academic resources."
                     "Accepts a list of the wanted papers to be downloaded. " 
                     "Example input: '[1, 2, 3]' where the numbers correspond to the indices of the papers in the last arxiv_search result.")

    )


    list_files_tool = Tool.from_function(

        name="list_files",
        func=list_files_tool_wrapper,
        description="Lists files in the directory. Optionally filter by file extension like 'pdf'."

    )

    tools = [search_tool, code_tool, multimodal_tool, arxiv_tool, download_tool, list_files_tool]

    return tools


if __name__ == "__main__":
    
    #for testing purposes only
    
    import json
    from memory.memory import AgentMemory

    memory = AgentMemory()  # initialize dummy memory

    tools = initialize_tools(memory)

    arxiv_tool = [tool for tool in tools if tool.name == "arxiv_search"][0]

    print("Try the ArXiv tool! Type your query below or type 'exit' to quit.\n")

    while True:
        user_query = input("Enter your query: ")
        print(user_query)
        try:

            print("\nRunning arxiv_search tool...\n")
            result = arxiv_tool.run(user_query)
            print("\n=== Tool Output ===\n")
            print(result)
            print("\n===================\n")

        except Exception as e:
            print(f"\n❌ Error while running tool: {e}\n")

