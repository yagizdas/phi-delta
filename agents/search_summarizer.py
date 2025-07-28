## File: phi_delta/agents/search_summarizer.py

from prompts import SEARCH_SUMMARIZER_PROMPT_TEMPLATE

def run_search_summarizer(reasoning_llm, tool_output: str) -> str:
    """
    Summarizes the output of a search tool using a language model.
    Args:
        reasoning_llm: The language model to use for summarization.
        tool_output (str): The output from the search tool to be summarized.
    Returns:
        str: The summarized response based on the search results.
    """
    search_summarizer_prompt = SEARCH_SUMMARIZER_PROMPT_TEMPLATE.format(tool_output=tool_output)

    result = reasoning_llm.invoke([

        {"role": "system", "content": "You are a helpful search tool summarizer."},
        {"role": "user", "content": search_summarizer_prompt}

    ])

    return result.content

