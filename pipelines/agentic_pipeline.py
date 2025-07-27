from agents import run_agent, run_evaluator, run_humanizer, run_finalizer, run_summarizer
from parsers import parse_agent, parse_eval
from langchain_openai import ChatOpenAI
from memory.memory import AgentMemory
from typing import List

def agentic_behaviour(llm: ChatOpenAI, 
                      agent, 
                      plan: List[str], 
                      question: str,  
                      memory: AgentMemory,
                      rag: bool = False, 
                      log: bool = False) -> list:

    i,j = 0,1
    
    step_by_step_context = "Summary of the previous steps:"

    ## Clearing the step history
    memory.step_history.clear()


    if not rag: memory.step_history.append({"question":question})

    while i < len(plan):

        if log:
            print("-"*60 + f" {i}th Step " + "-"*60)

        print(i, j, plan[i])

        humanized_step_desc = run_humanizer(llm, plan[i])


        print(humanized_step_desc)

        memory.thinkingsteps.append({"step": j, "description": humanized_step_desc})

        if log:
            print(f"\n\n {i}th Context (Summary): ", memory.chat_summary, "\n\n")

        answer, tools = run_agent(agent=agent,
                                  step=plan[i], 
                                  context=step_by_step_context,
                                  rag=rag)

        memory.step_history.append({f"Step {j}":humanized_step_desc, f"Report {j}":answer})

        if log:
            print("\n\nagent ran\n\n")

        summ, res = parse_agent(answer)

        print("Resources: ",res)

        summary = run_summarizer(reasoning_llm=llm, memory=memory, step=plan[i], answer=answer)

        print(f"\n\n {i}th run_summarizer Summary: ", summary, "\n\n")
        # print(f"\nFound Resources: {res}\n")

        # Since agent does not need all the summarized context, we only feed with the summary of the previous steps
        step_by_step_context += summary
        
        if len(step_by_step_context) > 1000:
            step_by_step_context = step_by_step_context[-1000:]

        if log:
            print(f"\n\n {i}th Summary: ", summ, "\n\n")
            print("\nAnswer: "+answer +"\n\n")

        memory.chat_history.append({"role":"system","content": answer})

        evaluation = run_evaluator(reasoning_llm=llm, 
                                   action=summ, 
                                   step=plan[i], 
                                   steps=plan, 
                                   question=question,
                                   rag=rag)

        if log:
            print(f"\n\n {i}th Evaluation: ", evaluation, "\n\n")
        
        parsed_eval = parse_eval(evaluation)

        print(parsed_eval)
        print(type(parsed_eval))

        if parsed_eval == -1:
            break
                
        elif isinstance(parsed_eval, list):
            
            i = 0
            j += 1  

            #declaring the new plan
            plan = parsed_eval

            
            print("\n\nChanged plans\n\n")

            print(f"\n\nNew plan length: {len(plan)}\n\n")

            memory.chat_history.append({"role":"system","content":evaluation})

            continue

        #print("Done. Proceeding...\n\n")

        if log:
            print("-"*130 + "\n\n")

        i += 1
        j += 1


    return "Done"