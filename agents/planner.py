## File: phi_delta/agents/planner.py

from config import TOOL_DESCRIPTIONS, RAG_TOOL_DESCRIPTIONS
from prompts import PLANNER_PROMPT_TEMPLATE, RAG_PLANNER_PROMPT_TEMPLATE  
from memory.memory import AgentMemory


def run_planner(reasoning_llm, 
                question: str, 
                context: AgentMemory, 
                rag: bool = False) -> str:
    """
    Generates a plan for the given question based on the context and available tools.
    Args:
        reasoning_llm: The language model to use for planning.
        question (str): The question to be planned.
        context: An object that stores state, such as chat history and thinking steps.
        rag (bool): If True, enables RAG (Retrieval-Augmented Generation) mode.
    Returns:
        str: The generated plan from the planner agent.
    """
    planner_prompt = PLANNER_PROMPT_TEMPLATE.format(context=context.chat_summary, tools=TOOL_DESCRIPTIONS)

    result = reasoning_llm.invoke([

        {"role": "system", "content": planner_prompt},
        {"role": "user", "content": f"Task: {question}"}

    ])

    return result.content
