from langgraph.prebuilt import create_react_agent

def instance_agent(llm,tools):
    """
    Creates an instance of the agent with the specified language model and tools.
    Args:
        llm: The language model to use for the agent.
        tools: The tools available to the agent.
    Returns:
        Agent: An instance of the agent configured with the specified model and tools.
    """
    agent = create_react_agent(

        model = llm,

        tools = tools,
        
    )

    return agent