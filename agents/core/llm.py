from langchain_openai import ChatOpenAI
from config import LLM_PORT, MODEL_NAME


def instance_llm(temperature: float = 0.6):
    """Create an instance of the LLM with the specified model and temperature."""

    return ChatOpenAI(

        model=MODEL_NAME,

        temperature=temperature,

        base_url=LLM_PORT

    )
