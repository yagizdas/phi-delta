from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
from main import init_agent, get_reply, route_query
from fastapi import BackgroundTasks
import asyncio
import threading

from pipelines import planner_behaviour, agentic_behaviour

from SessionRAG import add_to_rag

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

        print(f"Task fully completed. Processing state: {processing_state}")  # Debug log
        
    except Exception as e:
        print(f"Error in agentic task: {str(e)}")  # Debug log
        processing_state["result"] = f"Error: {str(e)}"
        processing_state["is_processing"] = False



class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    reply: str

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

@app.post("/reset-chat-history")
async def reset_chat_history():
    memory = state["memory"]
    memory.thinkingsteps.clear()
    # Also reset processing state
    processing_state["is_processing"] = False
    processing_state["result"] = None
    processing_state["current_question"] = None
    return {"status": "cleared"}

@app.get("/get-model-files")
async def get_model_files():
    """
    Retrieves a list of model files for the given session ID.
    """
    import os
    from config import MAIN_PATH
    model_files = [f for f in os.listdir(MAIN_PATH) if f.endswith('.pdf')]
    return model_files

@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    """
    Endpoint to upload a file to the server.
    """
    from pathlib import Path
    from config import MAIN_PATH

    vectorstore = state["vectorstore"]
    session_path = state["session_path"]

    # Ensure MAIN_PATH is a Path object
    save_path = Path(MAIN_PATH) / file.filename
    base = save_path.stem
    ext = save_path.suffix
    counter = 2

    # Check for existing file and increment suffix
    while save_path.exists():
        save_path = Path(MAIN_PATH) / f"{base}_{counter}{ext}"
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
    try:
        vectorstore = state["vectorstore"]

        state = init_agent(vectorstore=vectorstore, debug=True)

        # Add state management for async processing
        processing_state = {
            "is_processing": False,
            "result": None,
            "current_question": None
        }

        print("New chat session initialized successfully.")

        return "New chat session started successfully."
    
    except Exception as e:
        print(f"Error initializing new chat: {e}")
        return f"Error: {str(e)}"



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
        
        return ChatResponse(reply=answer)
