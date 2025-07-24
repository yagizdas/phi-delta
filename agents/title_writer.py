from prompts import TITLE_WRITER_PROMPT_TEMPLATE
from memory.memory import AgentMemory
from utils import get_user_prompts

def generate_title(reasoning_llm, memory: AgentMemory) -> str:

    user_messages = get_user_prompts(memory.chat_history_total)

    print(f"User messages for title generation: {user_messages}")  # Debug log

    title_generator_prompt = TITLE_WRITER_PROMPT_TEMPLATE.format(chat_history=user_messages)

    result = reasoning_llm.invoke([

        {"role": "system", "content": "You are a helpful assistant that will write 2-4 word concise and informative title for the chat."},
        {"role": "user", "content": f"{title_generator_prompt}"}

    ])

    return result.content