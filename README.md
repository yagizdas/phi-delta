# 🐍 phi-delta

A modern, agentic, local-first research assistant platform with LLM reasoning, document analysis, and an integrated Next.js frontend.

<img width="2559" height="1439" alt="phideltastartpage" src="https://github.com/user-attachments/assets/8c97630d-7e49-437a-991b-c6e72075e560" />

---

## 🚀 Overview

**phi-delta** is an advanced, locally running AI agentic assistant. It leverages cutting-edge LLMs (by default, Phi-4-IQ4_K_S) for reasoning, planning, and tool use. The system integrates custom tools for code execution, PDF/ArXiv document search and retrieval, multimodal (image) analysis, and vector-embedded document search. The platform features a robust backend in Python, and a sleek, responsive frontend built with Next.js.

**Key Features:**
- **💬 Local LLM Reasoning:**  
  Run `Phi-4-IQ4_XS` or `Phi-4-IQ4_K_S` locally via `vLLM` or `llama.cpp` for low-latency inference.
- **🤖 Planner–Critic–Executor Loop:**  
  Handles complex tasks with agentic planning, evaluation, and execution logic.
- **🔧 Tool Integration:**  
  - `arxiv_search`: Search & retrieve academic papers from ArXiv API  
  - `download_arxiv_pdfs`: Auto-download and process PDFs  
  - `code_tool`: Execute Python code snippets  
  - `multimodal_tool`: Analyze image contents, pdf pages, etc. 
  - `list_files`: Explore saved files by type (e.g. `.pdf`)
  - `rag_search`: Retrieve relevant information from dynamic RAG
  - `wolfram_search`: WolframAlpha API integration for easy factual information retrieval.
  - `Python REPL`: Code Execution tool for Phi Delta.
  
- **📚 Document Analysis:**  
  Parse downloaded PDFs, embed via HuggingFace (MiniLM-L6-v2), and search with Chroma.
- **🧠 Memory & Context Awareness:**  
  Maintains conversation history, summarizes past interactions, and routes queries through QuickResponse vs. Agentic pipelines.
- **🖥️ Next.js Frontend:**  
  Fully-featured modern UI for chat and file exploration.
  
## Quickstart
- Will be implemented soon.
- You can email me for any inquiries for this project at kyd.kemalyagiz@gmail.com
---

## 📦 Project Structure

```
phi-delta/
├── main.py                 # Entry point for backend, interactive CLI
├── config.py               # Configuration (paths, model names, etc.)
├── requirements.txt        # Python dependencies
├── phi-delta-frontend/     # Next.js frontend app
│   ├── src/app/page.js     # Main page (edit for UI changes)
│   ├── ...                 # Other frontend files
├── model_files/            # Directory for local model files
├── sessions/               # Session data storage
├── added_files.txt         # Tracks added/processed files
├── tests/                  # Backend tests (TODO)
└── ...
```

---

## 🛠️ Usage

- Interact with the agent through the CLI (`main.py`) or via the web UI.
- Supported actions include: asking questions, searching/downloading academic papers, running Python code, uploading/analyzing files, and more.

---

## 🧩 Configuration

Main config is in `config.py`:

- `MAIN_PATH` — path for model files
- `LLM_PORT` — local LLM API port
- `MODEL_NAME` — which LLM to use
- `EMBEDDER_MODEL_NAME` — embedding model
- `ADDED_FILES` — file tracking added docs

---

## 👨‍💻 Custom Tooling

The system supports extensible "tools" for:
- Academic search/PDF retrieval
- Python code execution (sandboxed)
- Multimodal (image) processing
- Local file management and retrieval

New tools can be added for further extensibility! Feel free to contribute.

---


## 📜 License

Licensed under the [Apache 2.0 License](LICENSE).

---

## 🙏 Credits

- [@yagizdas](https://github.com/yagizdas) (Author)
- Built with [Next.js](https://nextjs.org), [HuggingFace](https://huggingface.co), and the pioneering open-source LLM community.

