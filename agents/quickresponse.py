## File: phi_delta/agents/quickresponse.py

from prompts import QUICKRESPONSE_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_quickresponse(reasoning_llm, question: str, context: AgentMemory, retrieved_context: str = "", rag: bool = False):
    """
    Generates a quick response based on the provided question and context.
    Args:
        reasoning_llm: The language model to use for generating the response.
        question (str): The question to be answered.
        context: An object that stores state, such as chat history and thinking steps.
        retrieved_context (str): Additional context retrieved for the query.
        rag (bool): If True, enables RAG mode for additional context.
    Yields:
        str: The generated tokens from the quick response agent.
    """
    if not rag:
        quickresponse_prompt = QUICKRESPONSE_PROMPT_TEMPLATE.format(context=context.chat_summary)
    else:
        quickresponse_prompt = QUICKRESPONSE_PROMPT_TEMPLATE.format(context=context.chat_summary, retrieved_context=retrieved_context)

    for chunk in reasoning_llm.stream([{"role": "system", "content": quickresponse_prompt},{"role": "user", "content": f"{question}"}]):
        yield chunk.content

