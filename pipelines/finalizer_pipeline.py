from agents import run_finalizer
from session_manager import session_manager
from memory.memory import AgentMemory

def finalizer_behaviour(llm, memory: AgentMemory, session_id: str, session_path: str):
        finalized_answer = ""

        for token in run_finalizer(llm, memory):
            finalized_answer += token
            yield token

        memory.chat_history_total.append({"role":"assistant","content":finalized_answer})

        memory.thinkingsteps.clear()
        
        print("Saved session with ID:", session_id)
        print("Session path:", session_path)
        print("Saved Memory:", memory.chat_history_total)
        # Save the session with the finalized memory

        session_manager.save_session(session_id=session_id, session_path=session_path, memory=memory)
