## File: phi_delta/agents/quickresponse.py

from prompts import QUICKRESPONSE_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_quickresponse(reasoning_llm, question: str, context: AgentMemory, retrieved_context: str = "", rag: bool = False) -> str:

    if not rag:
        quickresponse_prompt = QUICKRESPONSE_PROMPT_TEMPLATE.format(context=context.chat_summary)
    else:
        quickresponse_prompt = QUICKRESPONSE_PROMPT_TEMPLATE.format(context=context.chat_summary, retrieved_context=retrieved_context)

    for chunk in reasoning_llm.stream([{"role": "system", "content": quickresponse_prompt},{"role": "user", "content": f"{question}"}]):
        yield chunk.content

