## File: phi_delta/agents/quickresponse.py

from prompts import HUMANIZER_PROMPT_TEMPLATE
from config import TOOL_DESCRIPTIONS
from memory.memory import AgentMemory

def run_humanizer(reasoning_llm, step: str) -> str:

    humanizer_prompt = HUMANIZER_PROMPT_TEMPLATE.format(step=step, tools=TOOL_DESCRIPTIONS)

    result = reasoning_llm.invoke([

        {"role": "system", "content": humanizer_prompt},
        {"role": "user", "content": f"Now humanize this step: {step}"}

    ])

    return result.content