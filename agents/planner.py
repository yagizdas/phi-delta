## File: phi_delta/agents/planner.py

from config import TOOL_DESCRIPTIONS, RAG_TOOL_DESCRIPTIONS
from prompts import PLANNER_PROMPT_TEMPLATE, RAG_PLANNER_PROMPT_TEMPLATE  
from memory.memory import AgentMemory


def run_planner(reasoning_llm, 
                question: str, 
                context: AgentMemory, 
                rag: bool = False) -> str:

    planner_prompt = PLANNER_PROMPT_TEMPLATE.format(context=context.chat_summary, tools=TOOL_DESCRIPTIONS)

    result = reasoning_llm.invoke([

        {"role": "system", "content": planner_prompt},
        {"role": "user", "content": f"Task: {question}"}

    ])

    return result.content
