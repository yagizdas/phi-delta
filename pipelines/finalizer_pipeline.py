  
from agents import run_finalizer
def finalizer_behaviour(llm, memory):
        finalized_answer = ""

        for token in run_finalizer(llm, memory):
            finalized_answer += token
            yield token

        memory.chat_history_total.append({"role":"assistant","content":finalized_answer})

        memory.thinkingsteps.clear()