from config import TOOL_DESCRIPTIONS
from prompts import EVALUATOR_PROMPT_TEMPLATE

def run_evaluator(reasoning_llm, action: str, step: str, steps, question: str, rag: bool = False) -> str:
    """
    Evaluates the agent's action and provides feedback or suggestions.
    Args:
        reasoning_llm: The language model to use for evaluation.
        action (str): The action taken by the agent.
        step (str): The step to be evaluated.
        steps: The list of steps taken by the agent.
        question (str): The original question posed by the user.
        rag (bool): If True, enables RAG (Retrieval-Augmented Generation) mode.
    Returns:
        str: The evaluation or feedback from the evaluator agent.
    """

    # Use the standard tool descriptions for non-RAG evaluation
    eval_prompt = EVALUATOR_PROMPT_TEMPLATE.format(
            tools=TOOL_DESCRIPTIONS,
            steps=steps,
            question=question,
        )

    result = reasoning_llm.invoke([

            {"role": "system", "content": eval_prompt},
            {"role": "user", "content": f"User's initial question was: {question}. How the Agent approach the Step: {step} is: {action}"}

        ])
    
    return result.content