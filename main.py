from .memory.memory import AgentMemory
from .parsers import parse_router
from .agents import run_router, run_quickresponse, run_summarizer
from .pipelines import agentic_behaviour, planner_behaviour
from .agents import instance_agent, instance_llm
from .tools import initialize_tools

memory = AgentMemory()

tools = initialize_tools(memory.arxiv_links)
llm = instance_llm()
agent = instance_agent(llm=llm, tools=tools)
context = memory.chat_summary

def main():
    
    while True:
        try:
            question = input("Enter your question (or type 'exit' to quit): ")

            if question.lower() == 'exit':
                break

            memory.chat_history.append({"role": "user", "content": question})

            decision = parse_router(run_router(question)) 

            if decision == "QuickResponse":
                print(run_quickresponse(llm, question, context=context))

            elif decision == "Agentic":
                agentic_behaviour(llm, agent, 
                                  planner_behaviour(llm, question, memory.chat_history), 
                                  question, 
                                  memory.chat_history, 
                                  context,
                                  log=True)
                
            conv_hist = run_summarizer(llm, memory.chat_history)
            memory.chat_summary = conv_hist

        except Exception as e:
            print(f"An error occurred: {e}")
            continue



        
    