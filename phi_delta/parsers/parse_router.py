def parse_router(response:str) -> str:

    try:
        if "QuickResponse" in response:
            return "QuickResponse"
        
        if "Agentic" in response:
            return "Agentic"
            
        return "None"


    except Exception as e:
        print(f"Parsing the router failed: {e}")