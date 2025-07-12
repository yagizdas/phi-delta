from langchain_experimental.tools.python.tool import PythonREPLTool
from langchain.tools import Tool

from . import phi4multimodal

from memory.memory import AgentMemory
from .search_and_summarize import search_and_summarize
from .arxiv_tool import search_arxiv_tool_input
from .download_arxiv_pdfs import bound_download_tool
from .list_directory import list_files_tool_wrapper
from .wolfram_tool import run_wolfram_alpha_query
from .rag_tool import rag_search_wrapper


def initialize_tools(llm, memory : AgentMemory, 
                     vectorstore, 
                     debug: bool = False) -> list[Tool]:
    """
    Initialize the tools used in the application.
    
    Args:
        memory: An object that stores state, such as arxiv links.
    
    Returns:
        A list of initialized tools.

    """
    search_tool = Tool.from_function(
        name="search_tool",
        func=lambda search: search_and_summarize(llm, search),
        description=(
            "Searches the web for up-to-date information, including breaking news. "
            "Accepts a natural language query as input. "
            "Example input: 'Your query here'")
    )
    

    code_tool = PythonREPLTool()

    multimodal_tool = phi4multimodal.Phi4MMTool()

    arxiv_tool = Tool.from_function(
        name="arxiv_search",
        func=lambda input_data: search_arxiv_tool_input(input_data, memory),
        description=(
            "Searches ArXiv for academic papers. "
            "Accepts a dictionary with 'query': (str), 'max_results': (int).' "
            "Example input: {'query': 'your query here', 'max_results': 'your max results here'}"
        )
    )
    
    download_tool = Tool.from_function(

        name="download_arxiv_pdfs",
        func=lambda input_data: bound_download_tool(input_data, memory.arxiv_links),  # return just the message
        description=("Downloads the PDF versions of academic papers from the last arxiv_search. It saves them locally for extensive analysis of the academic resources."
                     "Accepts a list of the wanted papers to be downloaded. " 
                     "Example input: '[x, y ,z]' where the x,y,z letters correspond to the indices of the papers in the last arxiv_search result.")

    )


    list_files_tool = Tool.from_function(

        name="list_files",
        func=list_files_tool_wrapper,
        description="Lists files in the directory. Optionally filter by file extension like 'pdf'."

    )

    wolfram_tool = Tool.from_function(
        name="wolfram_search",
        func=lambda input_data: run_wolfram_alpha_query(query=input_data),
        description=(
            "Queries the Wolfram Alpha API for computational knowledge. "
            "Accepts a natural language query as input. "
            "Example input: 'What is the mass of the sun in kg?, or 'What is the integral of x^2?'"
        )
    )

    rag_tool = Tool.from_function(
        name="rag_search",
        func=lambda input_data: rag_search_wrapper(vectorstore=vectorstore,
                                                   input_string=input_data,
                                                   debug=debug),
        description=(
            "Performs a similarity search in the vector store and returns the results. "
            "Accepts a query string and a file name as input. "
            "Example input: 'query: your search query here, file: your_file_name.pdf'"
        )
    )

    tools = [search_tool, 
             code_tool, 
             multimodal_tool, 
             arxiv_tool, 
             download_tool, 
             list_files_tool, 
             wolfram_tool,
             rag_tool]

    return tools


if __name__ == "__main__":
    
    #for testing purposes only

    import json
    from memory.memory import AgentMemory

    memory = AgentMemory()  # initialize dummy memory
    llm = None
    tools = initialize_tools(llm, memory)

    arxiv_tool = [tool for tool in tools if tool.name == "arxiv_search"][0]

    search_tool = tools[0]  # Tavily search tool
    
    wolfram_tool = [tool for tool in tools if tool.name == "wolfram_search"][0]

    #print("Try the ArXiv tool! Type your query below or type 'exit' to quit.\n")

    while True:
        user_query = input("Enter your query: ")
        print(user_query)
        try:

            print("\nRunning tool...\n")
            result = wolfram_tool.run(user_query)
            print("\n=== Tool Output ===\n")
            print(result)
            print("\n===================\n")
        except Exception as e:
            print(f"\n❌ Error while running tool: {e}\n")


