## File: phi_delta/agents/router.py

from config import TOOL_DESCRIPTIONS
from prompts import ROUTER_PROMPT_TEMPLATE
from memory.memory import AgentMemory

def run_router(reasoning_llm, query: str, context: AgentMemory, retrieved_context: str = "", debug: bool = False) -> str:
    """
    Routes the query to the appropriate tool based on the context and retrieved information.
    Args:
        reasoning_llm: The language model to use for routing.
        query (str): The query to be routed.
        context: An object that stores state, such as chat history and thinking steps.
        retrieved_context (str): Additional context retrieved for the query.
        debug (bool): If True, enables debug mode for additional logging.
    Returns:
        str: The response from the routing agent.
    """
    router_prompt = ROUTER_PROMPT_TEMPLATE.format(context=context.chat_summary, retrieved_context=retrieved_context, tools= TOOL_DESCRIPTIONS)
    
    if debug:
        print("Router Prompt:")
        print(router_prompt)

    result = reasoning_llm.invoke([

            {"role": "system", "content": router_prompt},
            {"role": "user", "content": f"The Query to be routed is: {query}"}

        ])
    
    return result.content