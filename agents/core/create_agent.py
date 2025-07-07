from langgraph.prebuilt import create_react_agent

def instance_agent(llm,tools):

    agent = create_react_agent(

        model = llm,

        tools = tools,
        
    )

    return agent