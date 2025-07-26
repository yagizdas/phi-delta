from config import TOOL_DESCRIPTIONS
from prompts import SUMMARIZER_PROMPT_EXAMPLE, STEP_SUMMARIZER_PROMPT_EXAMPLE
from typing import List, Dict
from memory.memory import AgentMemory

def run_summarizer(reasoning_llm, memory: AgentMemory, step_mode: bool = False, step: str = None, answer: str = None) -> str:
    
    if step:
        summary_prompt = STEP_SUMMARIZER_PROMPT_EXAMPLE
        return reasoning_llm.invoke([

        {"role": "system", "content": "You are a summarizer. Your task is to summarize the step and the answer."},
        {"role": "user", "content": STEP_SUMMARIZER_PROMPT_EXAMPLE.format(step=step, answer=answer)}
        
        ]).content
    
    summary_prompt = SUMMARIZER_PROMPT_EXAMPLE

    return reasoning_llm.invoke([

        {"role": "system", "content": summary_prompt},
        {"role": "user", "content": str(memory.chat_history)}
        
    ]).content