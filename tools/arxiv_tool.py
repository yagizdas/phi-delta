import arxiv
from langchain.tools import Tool
from memory.memory import AgentMemory
import json
import os
from datetime import datetime

import re
# 2. Create a custom function that returns structured data
from pydantic import BaseModel

class ArxivSearchInput(BaseModel):
    query: str
    max_results: int

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

            if len(result.summary) > 300:
                # Truncate the summary to 300 characters if it's too long
                result.summary = result.summary[:300] + "..."

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


def search_arxiv_tool_input(input_data: str, memory: AgentMemory, debug: bool = False) -> str:
    """
    Parses the input data for a search query and max results, then performs an ArXiv
    search using the provided memory.
    Returns the search results as a formatted string.
    """
    query = ""
    max_results = 3  # default fallback

    if isinstance(input_data, dict):
        query = input_data.get("query", "")
        max_results = input_data.get("max_results", 3)

    elif isinstance(input_data, str):
        input_data = input_data.strip()
        if not input_data:
            return "Empty input received. Please provide a search query."
    
        if debug:
            print("Input is a string, trying to parse it...")

        # First attempt: try JSON-style input
        try:
            normalized = input_data.replace("'", '"')
            parsed = json.loads(normalized)

            query = parsed.get("query", "")
            max_results = parsed.get("max_results", 3)

            if debug:
                print(f"Parsed JSON: query={query}, max_results={max_results}")

        except json.JSONDecodeError:
            print("Failed JSON parsing. Falling back to regex parsing...")

            query_match = re.search(r"query\s*[:=]\s*([^,]+)", input_data, re.IGNORECASE)
            max_results_match = re.search(r"max_results\s*[:=]\s*(\d+)", input_data, re.IGNORECASE)

            if query_match:
                query = query_match.group(1).strip()

            elif ":" not in input_data and "=" not in input_data:

                # Assume whole string is a query
                query = input_data.strip()

            if max_results_match:
                max_results = int(max_results_match.group(1))

    else:
        return "Invalid input type. Please provide a string or dictionary."

    if not query:
        return "Missing 'query'. Please provide a valid search term."

    #print(f"Running search with query='{query}', max_results={max_results}")
    result = search_arxiv_details(query=query, memory=memory, max_results=max_results)
    print(f"Search result: {result}")
    return result