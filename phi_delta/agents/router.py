## File: phi_delta/agents/router.py

from ..config import TOOL_DESCRIPTIONS
from ..prompts import ROUTER_PROMPT_TEMPLATE

def run_router(reasoning_llm, query: str, context: str) -> str:

    router_prompt = ROUTER_PROMPT_TEMPLATE.format(context=context, tools= TOOL_DESCRIPTIONS)

    print("Router Prompt:", router_prompt)
    
    result = reasoning_llm.invoke([

            {"role": "system", "content": router_prompt},
            {"role": "user", "content": f"The Query to be routed is: {query}"}

        ])
    
    return result.content