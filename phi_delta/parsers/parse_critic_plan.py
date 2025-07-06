def parse_critic_plan(text: str):

    steps = []
    step = []
    first = False
    started = False
    for line in text.splitlines():
        line = line.strip()
        if line.lower().startswith("step"):
            started = True
            if not first:
                first = True
                step = []
                step.append(line)
                continue
            steps.append(step)
            step = []

        if started: 
            step.append(line)
    
    if step:
        steps.append(step)

    folded_steps = []
    for step in steps:
        step_string = ""
        for line in step:
            step_string += line
        folded_steps.append(step_string)

    return folded_steps