from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from main import init_agent, get_reply, route_query, save_current_session, load_session_by_id, list_available_sessions, delete_session_by_id
from fastapi import BackgroundTasks
import asyncio
import threading
from session_manager import session_manager

from pipelines import planner_behaviour, agentic_behaviour

from SessionRAG import add_to_rag

from utils import create_session_directory

app = FastAPI()
state = init_agent(debug=True)

# Add state management for async processing
processing_state = {
    "is_processing": False,
    "result": None,
    "current_question": None
}

def run_agentic_task(state, question, rag = False, debug=False):
    global processing_state
    processing_state["is_processing"] = True
    processing_state["current_question"] = question
    
    try:
        print(f"Starting agentic task for question: {question}")  # Debug log
        memory = state["memory"]
        llm = state["llm"]
        agent = state["agent"]
        vectorstore = state["vectorstore"]
        session_path = state["session_path"]
        session_id = state.get("session_id")
        
        plan = planner_behaviour(llm=llm, question=question, memory=memory, rag=rag, debug=debug)
        result = agentic_behaviour(llm=llm, agent=agent, plan=plan, question=question, memory=memory, rag=rag, log=debug)
        
        print(f"Agentic task completed. Result: {result[:100]}...")  # Debug log
        
        # Store the final result
        processing_state["result"] = result
        processing_state["is_processing"] = False
        
        # Update chat summary (like in main.py)
        from agents import run_summarizer
        memory.chat_summary = run_summarizer(reasoning_llm=llm, memory=memory)

        # adding if any files were downloaded
        add_to_rag(vectorstore=vectorstore, session_path=session_path, debug=debug)
        
        # Save session after agentic task completion
        if session_id:
            session_manager.save_session(session_id=session_id, session_path=session_path, memory=memory)
            if debug: print(f"Session {session_id} saved after agentic task")

        print(f"Task fully completed. Processing state: {processing_state}")  # Debug log
        
    except Exception as e:
        print(f"Error in agentic task: {str(e)}")  # Debug log
        processing_state["result"] = f"Error: {str(e)}"
        processing_state["is_processing"] = False



class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

class SessionInfo(BaseModel):
    session_id: str
    session_path: str
    timestamp: str
    title: str

@app.get("/sessions")
async def get_sessions():
    """Get list of all saved sessions"""
    sessions = list_available_sessions()
    return {"sessions": sessions}

@app.post("/save-session")
async def save_session():
    """Save current session"""
    session_id = save_current_session(state)
    if session_id:
        return {"status": "success", "session_id": session_id}
    return {"status": "error", "message": "Failed to save session"}

@app.post("/load-session/{session_id}")
async def load_session(session_id: str):
    """Load a session by ID"""
    global state, processing_state
    
    try:
        print("Loading session:", session_id)  # Debug log

        session_path = create_session_directory(session_id=session_id)

        state = load_session_by_id(session_id=session_id, session_path=session_path, debug=True)

        print("Session state after loading:", state)  # Debug log

        # Reset processing state
        processing_state["is_processing"] = False
        processing_state["result"] = None
        processing_state["current_question"] = None
        
        return {"status": "success", "message": f"Session {session_id} loaded successfully"}
    except Exception as e:
        print("Error loading session:", e)  # Debug log
        return {"status": "error", "message": str(e)}

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a session by ID"""
    session_path = create_session_directory(session_id=session_id)

    success = delete_session_by_id(session_id=session_id, session_path=session_path)
    if success:
        return {"status": "success", "message": f"Session {session_id} deleted"}
    return {"status": "error", "message": "Failed to delete session"}

@app.get("/get-chat-history")
async def get_chat_history():
    memory = state["memory"]
    return memory.thinkingsteps

@app.get("/get-processing-status")
async def get_processing_status():
    status = {
        "is_processing": processing_state["is_processing"],
        "has_result": processing_state["result"] is not None,
        "current_question": processing_state["current_question"]
    }
    print(f"Processing status: {status}")  # Debug log
    return status

@app.get("/get-final-result")
async def get_final_result():
    if processing_state["result"] is not None:
        result = processing_state["result"]
        print(f"Returning final result: {result[:100]}...")  # Debug log
        # Clear the result after retrieving it
        processing_state["result"] = None
        processing_state["current_question"] = None
        return {"result": result}
    print("No result available yet")  # Debug log
    return {"result": None}

@app.get("/get-chat")
async def get_chat():
    memory = state["memory"]
    chat_history = memory.chat_history_total
    return {"chat": chat_history}

@app.get("/current-session")
async def get_current_session():
    """Get current session information"""
    session_id = state.get("session_id")
    session_path = state.get("session_path")
    return {
        "session_id": session_id,
        "session_path": session_path,
        "has_session": session_id is not None
    }

@app.post("/reset-chat-history")
async def reset_chat_history():
    memory = state["memory"]
    memory.thinkingsteps.clear()
    # Also reset processing state
    processing_state["is_processing"] = False
    processing_state["result"] = None
    processing_state["current_question"] = None
    return {"status": "cleared"}

@app.get("/get-model-files/{session_id}")
async def get_model_files(session_id: str):
    """
    Retrieves a list of model files for the given session ID.
    """
    import os
    from config import MAIN_PATH
    session_path = create_session_directory(session_id=session_id)
    model_files = [f for f in os.listdir(session_path) if not f.endswith('.json') and not f.endswith('.txt') and not os.path.isdir(os.path.join(session_path, f))]
    return model_files

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file to the server.
    """
    from pathlib import Path

    vectorstore = state["vectorstore"]
    session_path = state["session_path"]

    # Save to session directory instead of MAIN_PATH
    save_path = Path(session_path) / file.filename
    base = save_path.stem
    ext = save_path.suffix
    counter = 2

    # Check for existing file and increment suffix
    while save_path.exists():
        save_path = Path(session_path) / f"{base}_{counter}{ext}"
        counter += 1

    try:
        # Read file content
        file_content = await file.read()
        
        # Write file to disk
        with open(save_path, "wb") as f:
            f.write(file_content)

        print(f"File uploaded successfully: {save_path}")

        # Add to RAG system
        add_to_rag(vectorstore=vectorstore, session_path=session_path, debug=False)

        print("File added to RAG system")
        
        return {"status": "success", "file_path": str(save_path), "filename": save_path.name}
    except Exception as e:
        print(f"Error uploading file: {e}")
        return {"status": "error", "message": str(e)}

@app.post("/new-chat", response_model=ChatResponse)
async def new_chat():
    """
    Endpoint to start a new chat session.
    """
    global state, processing_state

    try:
        # Save current session before starting new one
        current_session_id = save_current_session(state)
        if current_session_id:
            print(f"Saved current session: {current_session_id}")
        
        passed_state = {
            "llm": state["llm"],
            "agent": state["agent"],
            "vectorstore": state["vectorstore"],
            "deterministic": state["deterministic"],
            "embeddings": state["embeddings"],
        }

        if not passed_state:
            raise ValueError("Passed state is empty or invalid.")

        # Reinitialize state with new session
        state = init_agent(passed_state, debug=True)
        print(f"New session initialized: {state.get('session_id')}")

        # Reset processing state
        processing_state["is_processing"] = False
        processing_state["result"] = None
        processing_state["current_question"] = None
        print("Processing state reset successfully.")

        return ChatResponse(reply="New chat session started successfully.")
    
    except Exception as e:
        print(f"Error initializing new chat: {e}")
        return ChatResponse(reply=f"Error: {str(e)}")



@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, background_tasks: BackgroundTasks):
    # Clear previous result
    processing_state["result"] = None
    
    route, ctx = route_query(state, req.message, debug=False)
    print(f"Route determined: {route}")

    if route == "Agentic":
        processing_state["is_processing"] = True
        background_tasks.add_task(run_agentic_task, state, req.message, False, True)  # Enable debug

        print(state["memory"].chat_history)
        
        return ChatResponse(reply="🔄 Processing your request... This may take a moment.")
    
    else:
        answer = get_reply(state, req.message, route, ctx, debug=False)

        # Answer returns True if it indicates an agentic task should be run after RAG routing. This is handled in the main.py logic.
        if answer == True:
            print("RAG Agentic task triggered")
            background_tasks.add_task(run_agentic_task, state, req.message, True, True)  # Enable debug, RAG

            print(state["memory"].chat_history)

            return ChatResponse(reply="🔄 Processing your request... This may take a moment.")
        
        # Session is automatically saved in get_reply function
        return ChatResponse(reply=answer)
