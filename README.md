# Phi Delta: A Local Agentic Research Assistant

**Phi Delta** is an autonomous, tool-augmented research assistant that runs locally using lightweight Phi-4 language models. Designed for scientific workflows, it combines agentic reasoning with dynamic tool use to explore, analyze, and summarize complex topics across academic and general domains — all without relying on cloud APIs.

## 🚀 Features

- **💬 Local LLM Reasoning**  
  Deploys `Phi-4-IQ4_XS` locally via `vLLM` or `llama.cpp` for low-latency inference.

- **🤖 Planner–Critic–Executor Loop**  
  Breaks down complex tasks into actionable steps with agentic planning, evaluation, and execution logic.

- **🔧 Tool Integration**  
  Includes custom tools for:
  - `arxiv_search`: Search and retrieve academic papers via the ArXiv API
  - `download_arxiv_pdfs`: Automatically download PDFs for local processing
  - `code_tool`: Execute Python snippets on the fly
  - `multimodal_tool`: Analyze image content
  - `list_files`: Explore saved files by type (e.g., `.pdf`)

- **📚 Document Analysis**  
  Parses downloaded PDFs, embeds them via HuggingFace (`MiniLM-L6-v2`), and performs vector similarity search using `FAISS`.

- **🧠 Memory and Context Awareness**  
  Maintains conversation history, summarizes past interactions, and routes new queries using a QuickResponse vs. Agentic pipeline.

---

<details>
<summary>📁 Project Structure</summary>


Will be updated!
</details>

---

## 🔧 Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/phi-delta.git
cd phi-delta
