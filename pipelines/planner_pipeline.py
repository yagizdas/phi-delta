from agents import run_planner, run_critic
from parsers import parse_critic_plan
from langchain_openai import ChatOpenAI
from memory.memory import AgentMemory
from typing import List

def planner_behaviour(llm: ChatOpenAI, 
                      question :str, 
                      memory: AgentMemory) -> List[str]:

    memory.chat_history.append({"role":"user","content":question})

    planner_answer = run_planner(llm, question, memory)

    critic_answer = run_critic(llm, planner_answer)

    print("\n\nCritized plan:",critic_answer,"\n\n")

    p_c_a = parse_critic_plan(critic_answer)

    memory.chat_history.append({"role":"system","content":critic_answer})

    return p_c_a