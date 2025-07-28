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
    """
    Executes the planner agent to generate a plan based on the provided question and memory.
    Args:
        llm: The language model to use for planning.
        question (str): The question to plan for.
        memory: An object that stores state, such as chat history and thinking steps.
        rag (bool): If True, enables RAG (Retrieval-Augmented Generation) mode.
        debug (bool): If True, enables debug mode for additional logging.
    Returns:
        List[str]: A list of strings representing the parsed plan from the critic agent.
    """
    if debug:
        print("\n\nPlanner started with RAG mode: ", rag, "\n\n")

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