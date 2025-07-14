import re

def extract_tools_from_plan(steps) -> list[str]:
    tool_pattern = r"`?(\w+_(?:tool|search))`?"
    tools = set()
    if isinstance(steps, str):
        steps = [steps]
    for step in steps:
        tools.update(re.findall(tool_pattern, step))
    return list(tools)