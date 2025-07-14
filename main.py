# main.py

from memory.memory import AgentMemory
from agents import instance_agent, instance_llm
from SessionRAG import init_rag
from tools import initialize_tools
from SessionRAG import add_to_rag, similarity_search
from parsers import parse_router
from agents import run_router, run_quickresponse, run_RAG_router
from pipelines import agentic_behaviour, planner_behaviour
from utils import create_session_id, create_session_directory
from agents import run_rewriter, run_summarizer

def init_agent(debug: bool = False) -> dict:
    memory          = AgentMemory()
    llm             = instance_llm()
    deterministic   = instance_llm(temperature=0.0)
    vectorstore, _  = init_rag()
    tools           = initialize_tools(llm=llm, memory=memory, vectorstore=vectorstore, debug=debug)
    agent           = instance_agent(llm=llm, tools=tools)
    session_id      = create_session_id()
    session_path    = create_session_directory(session_id=session_id)
    add_to_rag(vectorstore=vectorstore, session_path=session_path, debug=debug)
    return {
      "memory": memory,
      "llm": llm,
      "deterministic": deterministic,
      "vectorstore": vectorstore,
      "agent": agent,
      "session_path": session_path,
    }

def route_query(state: dict, question: str, debug: bool = False):
    memory        = state["memory"]
    llm           = state["llm"]
    deterministic = state["deterministic"]
    vectorstore   = state["vectorstore"]

    rew_q = run_rewriter(reasoning_llm=llm, question=question)
    ctx   = similarity_search(vectorstore=vectorstore, query=rew_q, debug=debug)
    route = parse_router(run_router(reasoning_llm=deterministic, query=question,
                       context=memory, retrieved_context=ctx, debug=debug),debug=debug)
    return route, ctx

def get_reply(state: dict, question: str, route: str, ctx: str, debug: bool = False) -> str:
    memory        = state["memory"]
    llm           = state["llm"]
    deterministic = state["deterministic"]
    vectorstore   = state["vectorstore"]
    agent         = state["agent"]
    session_path  = state["session_path"]

    if debug: print(f"\nQuestion: {question} | Routing: {route}\n")

    if route == "QuickResponse":
        answer = run_quickresponse(llm, question, context=memory)
    elif route == "Agentic":
        plan   = planner_behaviour(llm=llm, question=question, memory=memory)
        answer = agentic_behaviour(llm=llm, agent=agent, plan=plan,
                                   question=question, memory=memory, log=debug)
        add_to_rag(vectorstore=vectorstore, session_path=session_path, debug=debug)
    else:  
        resp      = run_quickresponse(llm, question, context=memory,
                                      retrieved_context=ctx, rag=True)
        rag_route = run_RAG_router(llm, query=question, response=resp,
                                   debug=debug).strip()
        if rag_route == "ESCALATE":
            plan   = planner_behaviour(llm=llm, question=question,
                                       memory=memory, rag=True, debug=debug)
            answer = agentic_behaviour(llm=llm, agent=agent, plan=plan,
                                       question=question, memory=memory,
                                       rag=True, log=debug)
        else:
            answer = resp

    # update summary
    memory.chat_summary = run_summarizer(reasoning_llm=llm, memory=memory)
    return answer

def run_agentic_task(state, question, debug=False):
    global processing_state
    processing_state["is_processing"] = True
    processing_state["current_question"] = question
    
    try:
        memory = state["memory"]
        llm = state["llm"]
        agent = state["agent"]
        plan = planner_behaviour(llm=llm, question=question, memory=memory)
        result = agentic_behaviour(llm=llm, agent=agent, plan=plan, question=question, memory=memory, log=debug)
        
        # Store the final result
        processing_state["result"] = result
        processing_state["is_processing"] = False
        
    except Exception as e:
        processing_state["result"] = f"Error: {str(e)}"
        processing_state["is_processing"] = False


processing_state = {
    "is_processing": False,
    "result": None,
    "current_question": None
    }

def main(debug: bool = False):

    global processing_state
    state = init_agent(debug=debug)
    print("Welcome to Phi Delta!\n")
    while True:
        q = input("You: ")
        if q.lower() in ("exit", "quit"):
            break

        processing_state["result"] = None
        
        route, ctx = route_query(state, q, debug=False)

        if route == "Agentic":
            run_agentic_task(state, q, False)
            print(f"Response: {processing_state['result']}")
        
        else:
            answer = get_reply(state, q, route, ctx, debug=False)
            print(f"Response: {answer}")

if __name__ == "__main__":
    main()
