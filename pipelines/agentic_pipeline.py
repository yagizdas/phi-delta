from ..agents import run_agent, run_evaluator
from ..parsers import parse_agent, parse_eval
from langchain_openai import ChatOpenAI
from ..memory.memory import AgentMemory
from typing import List

def agentic_behaviour(llm: ChatOpenAI, 
                      agent, 
                      plan: List[str], 
                      question: str,  
                      memory: AgentMemory.chat_history, 
                      context: str = "",
                      log :bool = False) -> list:

    i = 0

    while i < len(plan):

        answer, tools = run_agent(agent, plan[i], context)
        summ, res = parse_agent(answer) 

        memory.append({"role":"system","content": answer})

        evaluation = run_evaluator(llm, answer, plan[i], plan)

        if log:
            print(f"\n\n {i}th Evaluation: ", evaluation, "\n\n")
        
        parsed_eval = parse_eval(evaluation)

        if parsed_eval == -1:
            
            print(answer)
            break
        
        elif isinstance(parsed_eval, str):
            
            #declaring the new plan
            plan = parsed_eval

            memory.chat_history.append({"role":"system","content":evaluation})

            print(answer)

            i = 0

            continue

        if log:
            print(f"\n\n {i}th Context: ", context, "\n\n")
            print(answer)

        i += 1


    return