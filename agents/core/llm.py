from langchain_openai import ChatOpenAI
from config import LLM_PORT, MODEL_NAME


def instance_llm(temperature: float = 0.6):
    """
    Creates an instance of the language model with the specified temperature.
    Args:
        temperature (float): The temperature for the language model, controlling randomness.
    Returns:
        ChatOpenAI: An instance of the ChatOpenAI model configured with the specified temperature and other settings.
    """
    return ChatOpenAI(

        model=MODEL_NAME,

        temperature=temperature,

        base_url=LLM_PORT,

        streaming=True

    )
