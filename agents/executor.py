from config import TOOL_DESCRIPTIONS_DICT, RAG_TOOL_DESCRIPTIONS_DICT, TOOL_DESCRIPTIONS, RAG_TOOL_DESCRIPTIONS, parse_tool_descriptions
from prompts import EXECUTOR_PROMPT_TEMPLATE
from utils import extract_tool_names
from memory.memory import AgentMemory

def run_agent(agent, 
              step: str, 
              context: str = "", 
              rag: bool = False) -> tuple[str, list[str]]:
    """
    Executes a step using the provided agent and context.
    Args:
        agent: The agent to execute the step.
        step (str): The step to be executed.
        context (str): Context for the agent, defaults to an empty string.
        rag (bool): Whether to use RAG tools, defaults to False.
    Returns:
        tuple: A tuple containing the raw answer and a list of tools used.
    """

    print(step)

    tools_used = parse_tool_descriptions(step)

    print(f"\n\nTools used: {tools_used}\n\n")
    
    tools = "" 

    for tool in tools_used:

        if not rag and tool in TOOL_DESCRIPTIONS_DICT:
            tools += tool + ":" + TOOL_DESCRIPTIONS_DICT[tool] + "\n"

        elif rag and tool in RAG_TOOL_DESCRIPTIONS_DICT:
            tools += tool + ":" + RAG_TOOL_DESCRIPTIONS_DICT[tool] + "\n"

    if rag: 
        # If RAG is enabled, we might want to use different tool descriptions
        executor_prompt = EXECUTOR_PROMPT_TEMPLATE.format(
        context=context, 
        tools=tools
        )

    else:
        executor_prompt = EXECUTOR_PROMPT_TEMPLATE.format(
            context=context, 
            tools=tools
            )
    
    print(f"\n\nExecutor Prompt: {executor_prompt}\n\n")

    result = agent.invoke({"messages":[

        {"role": "system", "content": executor_prompt},
        {"role": "user", "content": f"Your task: {step}"}

    ]})

    raw_answer = result["messages"][-1].content
    tools_used = extract_tool_names(result)

    return raw_answer, tools_used