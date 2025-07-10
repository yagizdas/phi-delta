## File: phi_delta/agents/finalizer.py

from prompts import FINALIZER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_finalizer(reasoning_llm, memory: AgentMemory) -> str:

    finalizer_prompt = FINALIZER_PROMPT_TEMPLATE.format(step_history = memory.step_history)

    result = reasoning_llm.invoke([

        {"role": "system", "content": "You are a helpful assistant that will finalize and summarize and explain the question to humans in a more digestible way."},
        {"role": "user", "content": f"{finalizer_prompt}"}

    ])

    return result.content