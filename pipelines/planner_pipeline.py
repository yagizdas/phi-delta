from ..agents import run_planner, run_critic
from ..parsers import parse_critic_plan
from langchain_openai import ChatOpenAI
from ..memory.memory import AgentMemory
from typing import List

def planner_behaviour(llm: ChatOpenAI, 
                      question :str, 
                      memory: AgentMemory.chat_history) -> List[str]:

    memory.chat_history.append({"role":"user","content":question})

    planner_answer = run_planner(llm, question, memory)

    print(planner_answer)

    critic_answer = run_critic(llm, planner_answer)

    print(critic_answer)

    p_c_a = parse_critic_plan(critic_answer)

    memory.append({"role":"system","content":critic_answer})

    return p_c_a