from config import TOOL_DESCRIPTIONS, RAG_TOOL_DESCRIPTIONS
from prompts import EVALUATOR_PROMPT_TEMPLATE

def run_evaluator(reasoning_llm, action: str, step: str, steps, question: str, rag: bool = False) -> str:

    if rag:
        eval_prompt = EVALUATOR_PROMPT_TEMPLATE.format(
            tools=TOOL_DESCRIPTIONS,
            steps=steps,
            question=question,
        )

    else:
        # Use the standard tool descriptions for non-RAG evaluation
        eval_prompt = EVALUATOR_PROMPT_TEMPLATE.format(
            tools=RAG_TOOL_DESCRIPTIONS,
            steps=steps,
            question=question,
        )

    result = reasoning_llm.invoke([

            {"role": "system", "content": eval_prompt},
            {"role": "user", "content": f"How the Agent approach the Step: {step} is: {action}"}

        ])
    
    return result.content