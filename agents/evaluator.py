from config import TOOL_DESCRIPTIONS
from prompts import EVALUATOR_PROMPT_TEMPLATE

def run_evaluator(reasoning_llm, action: str, step: str, steps) -> str:

    eval_prompt = EVALUATOR_PROMPT_TEMPLATE.format(
        tools=TOOL_DESCRIPTIONS,
        steps=steps
    )

    result = reasoning_llm.invoke([

            {"role": "system", "content": eval_prompt},
            {"role": "user", "content": f"How the Agent approach the Step: {step} is: {action}"}

        ])
    
    return result.content