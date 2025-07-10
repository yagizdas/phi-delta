## File: phi_delta/agents/rewriter.py

from prompts import REWRITER_PROMPT_TEMPLATE

def run_rewriter(reasoning_llm, question: str) -> str:

    rewriter_prompt = REWRITER_PROMPT_TEMPLATE.format(query=question)

    result = reasoning_llm.invoke([

        {"role": "system", "content": "You are a helpful query rewriter."},
        {"role": "user", "content": rewriter_prompt}

    ])

    return result.content