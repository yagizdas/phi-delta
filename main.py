# main.py

from turtle import st
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
from session_manager import session_manager

def init_agent(passed_state=None, session_id=None, session_path=None, debug: bool = False) -> dict:
    """
    Initializes the agent with necessary components. Either start or a new chat session.
    Args:
        passed_state: Optional existing state to continue from
        session_id: Optional session ID to load from disk
        debug (bool): Flag to enable debug mode.
    Returns:
        dict: A dictionary containing initialized components.
    """
    # Try to load from existing session if session_id is provided
    print(f"Initializing agent with session_id: {session_id}, session_path: {session_path}, debug: {debug}")
    print(f"Passed state: {passed_state}")

    if session_id:
        session_path = create_session_directory(session_id=session_id)
        session_data = session_manager.load_session(session_id=session_id, session_path=session_path)
        if session_data:
            memory = session_data["memory"]
            print(f"Loaded session {session_id} from {session_data['timestamp']}")
        else:
            print(f"Session {session_id} not found, creating new session")
            memory = AgentMemory(max_history_length=30)
            session_id = session_manager.generate_session_id()
    else:
        memory = AgentMemory(max_history_length=30)
        session_id = session_manager.generate_session_id()
        session_path = create_session_directory(session_id=session_id)

    if passed_state is None:
        vectorstore, embeddings = init_rag(session_id=session_id)
        llm = instance_llm()
        deterministic = instance_llm(temperature=0.0)
        tools = initialize_tools(llm=llm, memory=memory, session_path=session_path, vectorstore=vectorstore, debug=debug)
        agent = instance_agent(llm=llm, tools=tools)
        
    else:
        print(passed_state)
        vectorstore, embeddings = init_rag(embedding=passed_state.get("embeddings"), session_id=session_id)
        llm = passed_state.get("llm")
        deterministic = passed_state.get("deterministic")
        tools = initialize_tools(llm=llm, memory=memory, session_path=session_path, vectorstore=vectorstore, debug=debug)
        agent = instance_agent(llm=llm, tools=tools)

    add_to_rag(vectorstore=vectorstore, session_path=session_path, debug=debug)

    print(f"Session initialized with ID: {session_id}")  # Debug log
    return {
      "memory": memory,
      "llm": llm,
      "deterministic": deterministic,
      "vectorstore": vectorstore,
      "agent": agent,
      "session_path": session_path,
      "embeddings": embeddings,
      "session_id": session_id,
      "session_path": session_path
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

def qr_get_reply(state: dict, question: str, route: str, ctx: str, debug: bool = False) -> str:
    memory        = state["memory"]
    llm           = state["llm"]
    session_id    = state["session_id"]
    session_path  = state["session_path"]

    if debug: print(f"\nQuestion: {question} | Routing: {route}\n")

    memory.add("user", question)

    answer = ""
    
    for token in run_quickresponse(llm, question, context=memory):
        print(token, end="", flush=True)  # Stream the response, debug
        answer += token  # Collect the response
        yield token  # Stream the response

    # update summary
    memory.add("assistant", answer)
    memory.chat_summary = run_summarizer(reasoning_llm=llm, memory=memory)
    
    # Save session after each interaction
    if session_id:
        session_manager.save_session(session_id=session_id, session_path=session_path, memory=memory)
        if debug: print(f"Session {session_id} saved")
    
    return answer

def rag_decide(state: dict, question: str, ctx: str, debug: bool = False):
    memory        = state["memory"]
    llm           = state["llm"]

    memory.add("user", question)

    resp      = run_quickresponse(llm, question, context=memory,
                                      retrieved_context=ctx, rag=True)
    rag_route = run_RAG_router(llm, query=question, response=resp,
                                   debug=debug).strip()
    decision = parse_router(rag_route, debug=debug)

    print(f"RAG Route: {decision}")  # Debug log
    
    if decision == "ESCALATE":
        print("Escalating to agentic task...")  # Debug log
        return True  # Indicates that the agentic task should be run
    
    return False

def rag_get_reply(state: dict, question: str, route: str, ctx: str, debug: bool = False):
    memory        = state["memory"]
    llm           = state["llm"]
    session_id    = state["session_id"]
    session_path  = state["session_path"]

    answer = ""

    for token in run_quickresponse(llm, question, context=memory, retrieved_context=ctx, rag=True):
        print(token, end="", flush=True)  # Stream the response, debug
        answer += token  # Collect the response
        yield token  # Stream the response

    # update summary
    memory.add("assistant", answer)
    memory.chat_summary = run_summarizer(reasoning_llm=llm, memory=memory)

    # Save session after each interaction
    if session_id:
        session_manager.save_session(session_id=session_id, session_path=session_path, memory=memory)
        if debug: print(f"Session {session_id} saved")

    return answer

def run_agentic_task(state, question, rag = False, debug=False):
    global processing_state
    processing_state["is_processing"] = True
    processing_state["current_question"] = question
    
    try:
        memory = state["memory"]
        llm = state["llm"]
        agent = state["agent"]
        session_id = state.get("session_id")
        session_path = state["session_path"]
        
        plan = planner_behaviour(llm=llm, question=question, memory=memory, rag=rag, debug=debug)
        result = agentic_behaviour(llm=llm, agent=agent, plan=plan, question=question, memory=memory, rag=rag, log=debug)

        # Store the final result
        processing_state["result"] = result
        processing_state["is_processing"] = False
        
        # Save session after agentic task completion
        if session_id:
            session_manager.save_session(session_id=session_id, session_path=session_path, memory=memory)
            if debug: print(f"Session {session_id} saved after agentic task")
        
    except Exception as e:
        processing_state["result"] = f"Error: {str(e)}"
        processing_state["is_processing"] = False


processing_state = {
    "is_processing": False,
    "result": None,
    "current_question": None
    }

def save_current_session(state: dict) -> str:
    """Save current session and return session ID"""
    session_id = state["session_id"]
    session_path = state["session_path"]
    memory = state["memory"]
    
    if session_id:
        success = session_manager.save_session(session_id=session_id, session_path=session_path, memory=memory)
        return session_id if success else None
    return None

def load_session_by_id(session_id: str, session_path: str, debug: bool = False) -> dict:
    """Load a session by ID and return initialized state"""
    return init_agent(session_id=session_id, session_path=session_path, debug=debug)

def list_available_sessions():
    """List all available sessions"""
    return session_manager.list_sessions()

def delete_session_by_id(session_id: str, session_path: str) -> bool:
    """Delete a session by ID"""
    return session_manager.delete_session(session_id=session_id, session_path=session_path)

def main(debug: bool = False):

    global processing_state
    state = init_agent(debug=debug)
    print("Welcome to phiDelta!\n")
    print("Commands: 'exit/quit' to exit, 'sessions' to list saved sessions, 'load <session_id>' to load a session")
    
    while True:
        q = input("You: ")
        if q.lower() in ("exit", "quit"):
            # Save session before exit
            session_id = save_current_session(state)
            if session_id:
                print(f"Session {session_id} saved")
            break
        
        # Handle session commands
        if q.lower() == "sessions":
            sessions = list_available_sessions()
            if sessions:
                print("\nAvailable sessions:")
                for session in sessions[:10]:  # Show last 10 sessions
                    print(f"  {session['session_id'][:8]}... - {session['title']} ({session['timestamp'][:19]})")
            else:
                print("No saved sessions found")
            continue
            
        if q.lower().startswith("load "):
            session_id = q[5:].strip()
            try:
                state = load_session_by_id(session_id, debug=debug)
                print(f"Loaded session {session_id}")
                continue
            except Exception as e:
                print(f"Error loading session: {e}")
                continue

        processing_state["result"] = None
        
        route, ctx = route_query(state, q, debug=False)

        if route == "Agentic":
            run_agentic_task(state, q, False)
            print(f"Response: {processing_state['result']}")
        
        else:
            answer = qr_get_reply(state, q, route, ctx, debug=False)
            print(f"Response: {answer}")

if __name__ == "__main__":
    main()
