## File: phi_delta/agents/planner.py

from ..config import TOOL_DESCRIPTIONS
from ..prompts import PLANNER_PROMPT_TEMPLATE

def run_planner(reasoning_llm, question: str, context: str = "") -> str:

    planner_prompt = PLANNER_PROMPT_TEMPLATE.format(context=context, tools=TOOL_DESCRIPTIONS)

    result = reasoning_llm.invoke([

        {"role": "system", "content": planner_prompt},
        {"role": "user", "content": f"Task: {question}"}

    ])

    return result.content