from ..config import TOOL_DESCRIPTIONS
from ..prompts import SUMMARIZER_PROMPT_EXAMPLE
from typing import List, Dict

def run_summarizer(reasoning_llm, history: List[Dict[str, str]]) -> str:

    summary_prompt = SUMMARIZER_PROMPT_EXAMPLE

    return reasoning_llm.invoke([

        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": str(history)}
        
    ]).content