from config import TOOL_DESCRIPTIONS
from prompts import EXECUTOR_PROMPT_TEMPLATE
from utils import extract_tool_names
from memory.memory import AgentMemory

def run_agent(agent, step: str, context: str = "") -> tuple[str, list[str]]:

    executor_prompt = EXECUTOR_PROMPT_TEMPLATE.format(
        context=context, 
        tools=TOOL_DESCRIPTIONS
        )
    
    #print(f"\n\nExecutor Prompt: {executor_prompt}\n\n")

    result = agent.invoke({"messages":[

        {"role": "system", "content": executor_prompt},
        {"role": "user", "content": f"Your task: {step}"}

    ]})

    raw_answer = result["messages"][-1].content
    tools_used = extract_tool_names(result)

    return raw_answer,tools_used