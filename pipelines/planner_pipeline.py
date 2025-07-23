from agents import run_planner, run_critic
from parsers import parse_critic_plan
from langchain_openai import ChatOpenAI
from memory.memory import AgentMemory
from typing import List

def planner_behaviour(llm: ChatOpenAI, 
                      question :str, 
                      memory: AgentMemory,
                      rag: bool = False,
                      debug: bool = False) -> List[str]:

    if debug:
        print("\n\nPlanner started with RAG mode: ", rag, "\n\n")

    memory.chat_history.append({"role":"user","content":question})
    memory.chat_history_total.append({"role":"user","content":question})

    if debug: print("\nplanner started\n")

    planner_answer = run_planner(reasoning_llm=llm, 
                                 question=question, 
                                 context=memory,
                                 rag=rag)

    critic_answer = run_critic(reasoning_llm=llm, 
                               planner_response=planner_answer,
                               rag=rag)

    if debug: print("\nPlan to be executed:",critic_answer,"\n\n")

    memory.chat_history.append({"role":"system","content":critic_answer})

    return parse_critic_plan(critic_answer)