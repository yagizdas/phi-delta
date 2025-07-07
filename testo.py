from memory.memory import AgentMemory
from tools.arxiv_tool import search_arxiv_details

# Create a fake memory object
memory = AgentMemory()

# Run the arXiv search directly
result = search_arxiv_details("quantum computing", memory, max_results=2)

# Print result and check memory contents
print("Search Results:\n", result)
print("\nSaved Links in Memory:")
print(memory.arxiv_links)