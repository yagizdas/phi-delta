def extract_tool_names(conversation:dict) -> list[str]:
    tool_names = set()
    for msg in conversation.get('messages', []):
        calls = []
        if hasattr(msg, 'tool_calls'):
            calls = msg.tool_calls or []
        elif isinstance(msg,dict):
            calls = msg.get('tool_calls') or []
            if not calls and isinstance(msg.get('additional_kwargs'), dict):
                calls = msg['additional_kwargs'].get('tool_calls', [])
        else:
            ak = getattr(msg, 'additional_kwargs', None)
            if isinstance(ak, dict):
                calls = ak.get('tool_calls', [])
        for call in calls:
            if isinstance(call, dict):
                if 'name' in call:
                    tool_names.add(call['name'])
                elif 'function' in call and isinstance(call['function'], dict):
                    fn = call['function']
                    if 'name' in fn:
                        tool_names.add(fn['name'])
    return sorted(tool_names)