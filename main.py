from memory.memory import AgentMemory
from parsers import parse_router
from agents import run_router, run_quickresponse, run_summarizer, run_rewriter, run_RAG_router
from pipelines import agentic_behaviour, planner_behaviour
from agents import instance_agent, instance_llm
from tools import initialize_tools
from pd_secrets import OPENAI_API_KEY, TAVILY_API_KEY
from SessionRAG import init_rag, add_to_rag, similarity_search
from utils import create_session_id, create_session_directory


def main(debug: bool = False):

    memory = AgentMemory()

    llm = instance_llm()
    deterministic_llm = instance_llm(temperature=0.0)

    tools = initialize_tools(llm, memory)

    agent = instance_agent(llm=llm, tools=tools)

    vectorstore, embeddings = init_rag()
    retrieved_context = ""

    session_id = create_session_id()

    print(f"Session ID: {session_id}\n")

    session_path = create_session_directory(session_id=session_id)
    
    print(f"Session Path: {session_path}\n")

    print("Setup Complete.\nWelcome to Phi Delta!\n\n")
    while True:
        try:
            question = input("Enter your question (or type 'exit' to quit): ")
            if question.lower() == 'exit':
                break
            
            memory.chat_history.append({"role": "user", "content": question})

            ## Rewriting the question for max effectiveness of retrieval
            rewrited_question = run_rewriter(llm,question)

            #print(f"Rewritten question: {rewrited_question}")

            ## Perform similarity search in the vector store
            retrieved_context = similarity_search(rewrited_question, vectorstore)
            
            router_answer = run_router(deterministic_llm, question, context=memory, retrieved_context=retrieved_context, debug=debug)

            decision = parse_router(router_answer) 
            
            if debug:
                print(f"Decision made by the router: {decision}")

            if decision == "QuickResponse":
                print(run_quickresponse(llm, question, context=memory))

            elif decision == "Agentic":

                agentic_behaviour(llm, agent, 
                                  planner_behaviour(llm, question, memory), 
                                  question, 
                                  memory,
                                  debug)
                
                # Add the new conversation to the RAG system
                add_to_rag(vectorstore=vectorstore, 
                           session_path=session_path, 
                           debug=debug)
            
            elif decision == "RAG":

                response = run_quickresponse(llm, question, 
                                             context=memory, 
                                             retrieved_context=retrieved_context, 
                                             rag=True)
                
                routed_rag = run_RAG_router(llm, query=question, 
                                            response=response, 
                                            debug=debug)
                
                print(routed_rag)

                rag_decision = parse_router(response=routed_rag,
                                           debug=debug)
                
                print(rag_decision)

                if rag_decision == "ESCALATE":
                    #rag_agent_behaviour()
                    pass

                else:
                    ## Print the response immediately
                    print(response)
                                        
            # Update conversation history and generate summary
            memory.chat_summary = run_summarizer(llm, memory)

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main()


        
    