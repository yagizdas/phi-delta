## File: phi_delta/agents/router.py

from config import TOOL_DESCRIPTIONS
from prompts import RAG_ROUTER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_RAG_router(reasoning_llm, query: str, response: str = "", debug: bool = False) -> str:

    RAG_router_prompt = RAG_ROUTER_PROMPT_TEMPLATE.format(question=query, response=response)
    
    if debug:
        print(f"RAG Router Prompt: {RAG_router_prompt}\n")

    result = reasoning_llm.invoke([

            {"role": "system", "content": "You are a router agent deciding rather you should escalate or end the process."},
            {"role": "user", "content": f"{RAG_router_prompt}"}

        ])
    
    return result.content