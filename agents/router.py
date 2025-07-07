## File: phi_delta/agents/router.py

from config import TOOL_DESCRIPTIONS
from prompts import ROUTER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_router(reasoning_llm, query: str, context: AgentMemory) -> str:

    router_prompt = ROUTER_PROMPT_TEMPLATE.format(context=context.chat_summary, tools= TOOL_DESCRIPTIONS)
    
    result = reasoning_llm.invoke([

            {"role": "system", "content": router_prompt},
            {"role": "user", "content": f"The Query to be routed is: {query}"}

        ])
    
    return result.content