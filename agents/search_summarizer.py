## File: phi_delta/agents/quickresponse.py

from prompts import SEARCH_SUMMARIZER_PROMPT_TEMPLATE

def run_search_summarizer(reasoning_llm, tool_output: str) -> str:

    search_summarizer_prompt = SEARCH_SUMMARIZER_PROMPT_TEMPLATE.format(tool_output=tool_output)

    result = reasoning_llm.invoke([

        {"role": "system", "content": "You are a helpful search tool summarizer."},
        {"role": "user", "content": search_summarizer_prompt}

    ])

    return result.content

