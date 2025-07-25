## File: phi_delta/agents/finalizer.py

from prompts import FINALIZER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_finalizer(reasoning_llm, memory: AgentMemory):
    """Finalizes the agent's response by summarizing and explaining the question in a more digestible way."""

    finalizer_prompt = FINALIZER_PROMPT_TEMPLATE.format(step_history = memory.step_history)

    for chunk in reasoning_llm.stream([

        {"role": "system", "content": "You are a helpful assistant that will finalize and summarize and explain the question to humans in a more digestible way."},
        {"role": "user", "content": f"{finalizer_prompt}"}

    ]):
        yield chunk.content

