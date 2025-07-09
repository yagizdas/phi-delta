## File: phi_delta/agents/quickresponse.py

from prompts import REWRITER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_rewriter(reasoning_llm, question: str) -> str:

    rewriter_prompt = REWRITER_PROMPT_TEMPLATE

    result = reasoning_llm.invoke([

        {"role": "system", "content": rewriter_prompt},
        {"role": "user", "content": f"{question}"}

    ])

    return result.content