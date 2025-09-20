# InquiroAI
Inquiro is an open-source AI tool for interactive Q&amp;A over PDFs, Word, and PowerPoint files. It combines semantic search with LLMs to provide precise, context-aware answers via an intuitive chat interface. Designed for academic use, it offers local control, extensibility, and a polished user experience for effective knowledge exploration.


## Overview

**Inquiro** is an open-source AI-powered assistant designed for interactive question answering over PDF, Word, and PowerPoint documents. It combines semantic search using dense vector embeddings with large language models to deliver precise, context-aware answers within an intuitive chat interface. Tailored for academic and research use, it offers full local control, extensibility, and a polished user experience for effective knowledge exploration.

---

## Key Features

- **Multiformat Document Support:** Upload and analyze PDFs, DOCX, and PPTX files seamlessly.
- **Semantic Search + Generative QA:** Utilizes Sentence Transformers and FAISS for accurate semantic search alongside Google Flan-T5 for natural language answers.
- **Token-Length Aware Context Handling:** Manages LLM input limits to ensure stable and reliable responses.
- **Custom Document Chunking:** Breaks down documents into balanced chunks for efficient embedding and retrieval.
- **Interactive Chat UI:** Streamlit-based interface with conversation history and styled chat messages.
- **Open-source and Modular:** Easily customizable components for embedding, search, and generation.
- **Local Deployment:** Run the assistant entirely on your machine for privacy and cost-effectiveness.


- Upload PDFs, Word documents, or PowerPoint files via the sidebar.
- Ask questions in the input box and receive AI-generated answers grounded in your documents.
- Review your conversation history within the chat interface.

---

## Project Structure

| File           | Description                                         |
|----------------|-----------------------------------------------------|
| `app.py`       | Streamlit frontend and main application logic       |
| `pdf_utils.py` | Multi-format document parsing and text extraction   |
| `embeddings.py`| Embedding generation using Sentence Transformers    |
| `vectorstore.py`| FAISS-based vector storage and semantic search     |
| `qa_engine.py` | Core engine combining semantic search and LLM QA   |
| `requirements.txt` | Python dependencies                               |

---

## Future Improvements

- Support additional document types (e.g., HTML, EPUB).
- Add summarization and multi-turn dialogue memory.
- Provide user authentication and secure data handling.
- Enable cloud deployment with Docker.
- Enhance UI with exportable chat history and richer chat bubbles.

---

## License

MIT License © 2025 Your Name

---

## Contact & Contributions

Feel free to open issues or submit pull requests.  
Email: your.email@example.com  
GitHub: [yourusername](https://github.com/yourusername)
