import arxiv
from langchain.tools import Tool
from memory.memory import AgentMemory

# 2. Create a custom function that returns structured data

def search_arxiv_details(query: str, memory, max_results: int = 3, ) -> str:

    
    """
    Searches arXiv for a given query and returns a formatted string with
    the paper's title, summary, arXiv ID, and a direct link.
        

    """
    try:

        memory.arxiv_links.clear()
    
        # Perform the search using the arxiv library
        Client = arxiv.Client()

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        formatted_results = []
        for result in Client.results(search):
            # The entry_id is the full URL, we can use it directly as the link
            paper_link = result.entry_id
            # The actual ID is the last part of the URL
            paper_id = paper_link.split('/')[-1]

            result_string = (
                f"Title: {result.title}\n"
                f"Authors: {', '.join(author.name for author in result.authors)}\n"
                f"Published: {result.published.strftime('%Y-%m-%d')}\n"
                f"Summary: {result.summary}\n"
                f"ArXiv ID: {paper_id}\n"
                f"Link: {paper_link}\n"
            )

            formatted_results.append(result_string)
            
            
            memory.arxiv_links.append([paper_link, result.title])

        if not formatted_results:
            return "No results found on ArXiv for that query."

        return "\n---\n".join(formatted_results)

    except Exception as e:
        print("error")
        return f"An error occurred during ArXiv search: {e}"

def search_arxiv_tool_input(input_data: dict, memory: AgentMemory) -> str:

    query = input_data.get("query", "")
    max_results = input_data.get("max_results", 3)

    return search_arxiv_details(query=query, memory=memory, max_results=max_results)