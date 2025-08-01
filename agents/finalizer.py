## File: phi_delta/agents/finalizer.py

from prompts import FINALIZER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_finalizer(reasoning_llm, memory: AgentMemory):
    """
    Finalizes the conversation by summarizing and explaining the steps taken.
    Args:
        reasoning_llm: The language model to use for finalization.
        memory: An object that stores state, such as chat history and thinking steps.
    Yields:
        str: The streamed tokens generated by the finalizer agent.
    """
    finalizer_prompt = FINALIZER_PROMPT_TEMPLATE.format(step_history = memory.step_history)

    for chunk in reasoning_llm.stream([

        {"role": "system", "content": "You are a helpful assistant that will finalize and summarize and explain the question to humans in a more digestible way."},
        {"role": "user", "content": f"{finalizer_prompt}"}

    ]):
        yield chunk.content

