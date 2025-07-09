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
    
    step_by_step_context = "Summary of the previous steps:"

    while i < len(plan):
        
        if log:
            print("-"*60 + f" {i}th Step " + "-"*60)

        print(run_humanizer(llm, plan[i]))

        if log:
            print(f"\n\n {i}th Context (Summary): ", memory.chat_summary, "\n\n")

        answer, tools = run_agent(agent, plan[i], step_by_step_context)

        if log:
            print("\n\nagent ran\n\n")

        summ, res = parse_agent(answer)

        # print(f"\nFound Resources: {res}\n")

        # Since agent does not need all the summarized context, we only feed with the summary of the previous steps
        step_by_step_context += f"{answer}\n\n"

        if log:
            print(f"\n\n {i}th Summary: ", summ, "\n\n")
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

        print("Done. Proceeding...\n\n")

        if log:
            print("-"*130 + "\n\n")
        i += 1

    print("Response: ", answer)


    return