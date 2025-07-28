#from langchain_community.tools import TavilySearchResults
from agents import run_search_summarizer
from langchain_tavily import TavilySearch

def search_and_summarize(llm, question: str = "", debug: bool = False) -> str:
    """
    Searches the web for information based on the provided question and summarizes the results.
    Args:
        llm: The language model to use for summarization.
        question (str): The question to search for.
        debug (bool): If True, prints debug information.
    Returns:
        str: A summarized response based on the search results.
    """
    if debug:
        print(f"Search and Summarize invoked with question: {question}")

    search_tool = TavilySearch(max_results=3, include_answer=True)
        
    results = search_tool.invoke(question)

    summarized_response = run_search_summarizer(llm, results)

    if debug:
        print(f"Summarized Response sent to the LLM: {summarized_response}")

    return summarized_response
