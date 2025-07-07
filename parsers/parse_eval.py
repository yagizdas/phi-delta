from .parse_critic_plan import parse_critic_plan

def parse_eval(response: str):

    for i,line in enumerate(response.splitlines()):

        if i == 0:

            if "no change" in line.lower():
                return 1
            
            if "break" in line.lower() or "stop" in line.lower():
                return -1
            
            if "changed steps" in line.lower():
                return parse_critic_plan(response)