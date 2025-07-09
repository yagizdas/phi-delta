import re 

def parse_router(response:str, debug:bool = False) -> str:

    try:
        match = re.search(r"Choosen Pipeline:\s*(QuickResponse|RAG|Agentic)", response)
        if not match:
            if debug:
                print(f"⚠️ Could not parse pipeline: {response}")
            return None
        return match.group(1)
    
    except Exception as e:
        if debug:
            print(f"❌ Parsing the router failed: {e}")
        return None