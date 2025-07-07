## File: phi_delta/agents/quickresponse.py

from ..prompts import QUICKRESPONSE_PROMPT_TEMPLATE

def run_quickresponse(reasoning_llm, question: str, context: str = "") -> str:

    quickresponse_prompt = QUICKRESPONSE_PROMPT_TEMPLATE.format(context=context)

    result = reasoning_llm.invoke([

        {"role": "system", "content": quickresponse_prompt},
        {"role": "user", "content": f"Task: {question}"}

    ])

    return result.content