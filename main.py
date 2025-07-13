from memory.memory import AgentMemory
from parsers import parse_router
from agents import run_router, run_quickresponse, run_summarizer, run_rewriter, run_RAG_router
from pipelines import agentic_behaviour, planner_behaviour
from agents import instance_agent, instance_llm
from tools import initialize_tools
from pd_secrets import OPENAI_API_KEY, TAVILY_API_KEY
from SessionRAG import init_rag, add_to_rag, similarity_search
from utils import create_session_id, create_session_directory


def main(debug: bool = True):

    memory = AgentMemory()

    llm = instance_llm()
    deterministic_llm = instance_llm(temperature=0.0)

    vectorstore, embeddings = init_rag()

    tools = initialize_tools(llm=llm, 
                             memory=memory, 
                             vectorstore=vectorstore,
                             debug=debug)

    agent = instance_agent(llm=llm, 
                           tools=tools)


    session_id = create_session_id()

    print(f"Session ID: {session_id}\n")

    session_path = create_session_directory(session_id=session_id)
    
    print(f"Session Path: {session_path}\n")

    add_to_rag(vectorstore=vectorstore, 
               session_path=session_path, 
               debug=debug)

    print("Setup Complete.\nWelcome to Phi Delta!\n\n")
    while True:
        try:
            question = input("Enter your question (or type 'exit' to quit): ")
            if question.lower() == 'exit':
                break
            
            memory.chat_history.append({"role": "user", "content": question})

            ## Rewriting the question for max effectiveness of retrieval
            rewrited_question = run_rewriter(reasoning_llm=llm,
                                             question=question)

            #print(f"Rewritten question: {rewrited_question}")

            ## Perform general similarity search in the vector store
            retrieved_context = similarity_search(vectorstore=vectorstore, 
                                                  query=rewrited_question,
                                                  debug=debug)
            
            router_answer = run_router(reasoning_llm=deterministic_llm, 
                                       query=question, 
                                       context=memory, 
                                       retrieved_context=retrieved_context, 
                                       debug=debug)

            decision = parse_router(response=router_answer,
                                    debug=debug) 
            
            if debug:
                print(f"Decision made by the router: {decision}")

            if decision == "QuickResponse":
                print(run_quickresponse(llm, question, context=memory))

            elif decision == "Agentic":

                answer = agentic_behaviour(llm=llm, 
                                           agent=agent, 
                                           plan=planner_behaviour(llm=llm, 
                                                                  question=question, 
                                                                  memory=memory), 
                                           question=question, 
                                           memory=memory,
                                           log=debug)
                
                # Add the new conversation to the RAG system
                add_to_rag(vectorstore=vectorstore, 
                           session_path=session_path, 
                           debug=debug)
            
            elif decision == "RAG":

                response = run_quickresponse(reasoning_llm=llm, 
                                             question=question, 
                                             context=memory, 
                                             retrieved_context=retrieved_context, 
                                             rag=True)
                
                routed_rag = run_RAG_router(reasoning_llm=llm, 
                                            query=question, 
                                            response=response, 
                                            debug=debug)
                
                rag_decision = parse_router(response=routed_rag, debug=debug)

                if debug:
                    print(f"\nRAG Decision: {rag_decision}\n")
                
                if rag_decision == "ESCALATE":
                    ## If the RAG router decides to escalate, we run the agentic behaviour focused in RAG tools
                    answer = agentic_behaviour(llm=llm, 
                                               agent=agent, 
                                               plan=planner_behaviour(llm=llm, 
                                                                      question=question, 
                                                                      memory=memory, 
                                                                      rag=True, 
                                                                      debug=debug), 
                                               question=question, 
                                               memory=memory,
                                               rag=True, 
                                               log=debug)

                else:
                    ## Get the answer from the response
                    answer = response
            
                                        
            # Update conversation history and generate summary
            memory.chat_summary = run_summarizer(reasoning_llm=llm, 
                                                 memory=memory)

            print(f"\n\nAnswer: {answer}\n\n")

        except Exception as e:
            print(f"An error occurred: {e}")
            continue

if __name__ == "__main__":
    main(debug=True)


        
    