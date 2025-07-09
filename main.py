from memory.memory import AgentMemory
from parsers import parse_router
from agents import run_router, run_quickresponse, run_summarizer
from pipelines import agentic_behaviour, planner_behaviour
from agents import instance_agent, instance_llm
from tools import initialize_tools
from pd_secrets import OPENAI_API_KEY, TAVILY_API_KEY
from SessionRAG import init_rag, add_to_rag, similarity_search

memory = AgentMemory()

tools = initialize_tools(memory)
llm = instance_llm()
agent = instance_agent(llm=llm, tools=tools)

def main():
    
    vectorstore, embeddings = init_rag()
    retrieved_context = ""

    while True:
        try:
            question = input("Enter your question (or type 'exit' to quit): ")

            if question.lower() == 'exit':
                break
            
            memory.chat_history.append({"role": "user", "content": question})

            # Perform similarity search in the vector store
            retrieved_context = similarity_search(question, vectorstore)

            decision = parse_router(run_router(llm, question, 
                                               context=memory, 
                                               retrieved_context=retrieved_context)) 

            print(f"Decision made by the router: {decision}")

            if decision == "QuickResponse":
                print(run_quickresponse(llm, question, context=memory))

            elif decision == "Agentic":
                agentic_behaviour(llm, agent, 
                                  planner_behaviour(llm, question, memory), 
                                  question, 
                                  memory,
                                  log=False)
                
                # Add the new conversation to the RAG system
                add_to_rag(vectorstore, embeddings)
            
            elif decision == "RAGQuickResponse":
                response = run_quickresponse(llm, question, 
                                             context=memory, 
                                             retrieved_context=retrieved_context, 
                                             rag=True)
                
                print(response)

            # Update conversation history and generate summary
            memory.chat_summary = run_summarizer(llm, memory)

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()


        
    