import re
from typing import Tuple, List

def parse_agent(text: str) -> Tuple[str, List[str]]:
    """
    Extracts the 'Summary' and 'Resources' sections from agent output.

    Returns:
        - summary_string: Concatenated summary section (str)
        - resources: List of resource lines (List[str])
    """
    # Use regex to extract the sections
    summary_match = re.search(r"###\s*Summary:\s*(.*?)###\s*Resources:", text, re.DOTALL | re.IGNORECASE)
    resources_match = re.search(r"###\s*Resources:\s*(.*?)($|###|\Z)", text, re.DOTALL | re.IGNORECASE)

    summary_string = summary_match.group(1).strip() if summary_match else ""
    resources_block = resources_match.group(1).strip() if resources_match else ""

    # Split resources into non-empty lines
    resources = [line.strip() for line in resources_block.splitlines() if line.strip()]

    return summary_string, resources
