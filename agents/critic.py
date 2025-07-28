## File: phi_delta/agents/critic.py

from config import TOOL_DESCRIPTIONS,RAG_TOOL_DESCRIPTIONS
from prompts import CRITIC_PROMPT_TEMPLATE

def run_critic(reasoning_llm, 
               planner_response: str, 
               rag: bool = False) -> str:
    """
    Evaluates the planner's response and provides feedback or suggestions.
    Args:
        reasoning_llm: The language model to use for evaluation.
        planner_response (str): The response from the planner agent to be evaluated.
        rag (bool): If True, enables RAG (Retrieval-Augmented Generation) mode.
    Returns:
        str: The evaluation or feedback from the critic agent.
    """
    if rag: 
        critic_prompt = CRITIC_PROMPT_TEMPLATE.format(tools=RAG_TOOL_DESCRIPTIONS)

    else:
        # Use the standard tool descriptions for non-RAG planning
        critic_prompt = CRITIC_PROMPT_TEMPLATE.format(tools=TOOL_DESCRIPTIONS) 

    result = reasoning_llm.invoke([

        {"role": "system", "content": critic_prompt},
        {"role": "user", "content": f"Planner Agent's Response: {planner_response}"}

    ])

    return result.content



