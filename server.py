from fastapi import FastAPI
from pydantic import BaseModel
from main import init_agent, get_reply, route_query
from fastapi import BackgroundTasks
import asyncio
import threading

from pipelines import planner_behaviour, agentic_behaviour

app = FastAPI()
state = init_agent(debug=False)

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
        plan = planner_behaviour(llm=llm, question=question, memory=memory, rag=rag, debug=debug)
        result = agentic_behaviour(llm=llm, agent=agent, plan=plan, question=question, memory=memory, rag=rag, log=debug)
        
        print(f"Agentic task completed. Result: {result[:100]}...")  # Debug log
        
        # Store the final result
        processing_state["result"] = result
        processing_state["is_processing"] = False
        
        # Update chat summary (like in main.py)
        from agents import run_summarizer
        memory.chat_summary = run_summarizer(reasoning_llm=llm, memory=memory)
        
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

@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, background_tasks: BackgroundTasks):
    # Clear previous result
    processing_state["result"] = None
    
    route, ctx = route_query(state, req.message, debug=False)
    print(f"Route determined: {route}")

    if route == "Agentic":
        processing_state["is_processing"] = True
        background_tasks.add_task(run_agentic_task, state, req.message, False, True)  # Enable debug
        return ChatResponse(reply="🔄 Processing your request... This may take a moment.")
    
    else:

        answer = get_reply(state, req.message, route, ctx, debug=False)

        # Answer returns True if it indicates an agentic task should be run after RAG routing. This is handled in the main.py logic.
        if answer == True:

            print("RAG Agentic task triggered")
            background_tasks.add_task(run_agentic_task, state, req.message, True, True)  # Enable debug, RAG
            return ChatResponse(reply="🔄 Processing your request... This may take a moment.")
        
        return ChatResponse(reply=answer)
