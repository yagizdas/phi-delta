def parse_agent(text: str):

    summary = []
    resources = []
    summary_b = bool
    resources_b = bool

    for line in text.splitlines():

        line = line.strip()
        
        if "summary:" in line.lower():
            summary_b = True
            resources_b = False
            continue

        if "resources:" in line.lower():
            summary_b = False
            resources_b = True
            continue

        if summary_b:
            summary.append(line)

        if resources_b:
            resources.append(line)

        summary_string = ""


    for line in summary:
        summary_string += line
        
    return summary_string, resources