from agents import run_agent, run_evaluator, run_humanizer
from parsers import parse_agent, parse_eval
from langchain_openai import ChatOpenAI
from memory.memory import AgentMemory
from typing import List

def agentic_behaviour(llm: ChatOpenAI, 
                      agent, 
                      plan: List[str], 
                      question: str,  
                      memory: AgentMemory, 
                      log :bool = False) -> list:

    i = 0

    while i < len(plan):

        print(run_humanizer(llm, plan[i]))

        answer, tools = run_agent(agent, plan[i], memory)
        summ, res = parse_agent(answer) 

        #print(f"\n\n {i}th Step: ", plan[i], "\n\n")

        print("\nAnswer: "+answer +"\n\n")

        memory.chat_history.append({"role":"system","content": answer})

        evaluation = run_evaluator(llm, answer, plan[i], plan, question=question)

        if log:
            print(f"\n\n {i}th Evaluation: ", evaluation, "\n\n")
        
        parsed_eval = parse_eval(evaluation)

        if parsed_eval == -1:
            break
        
        elif isinstance(parsed_eval, str):
            
            #declaring the new plan
            plan = parsed_eval
            
            print("\n\nChanged plans\n\n")

            memory.chat_history.append({"role":"system","content":evaluation})

            i = 0

            continue

        if log:
            print(f"\n\n {i}th Context: ", memory.chat_summary, "\n\n")

        i += 1


    return