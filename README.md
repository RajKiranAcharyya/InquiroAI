# InquiroAI

InquiroAI is a document question-answering app that retrieves relevant text and answers with source references.

## Features

- Upload PDF, DOCX, and PPTX files in the React web interface.
- Extract selectable PDF text, Word paragraphs and tables, and PowerPoint slide text.
- Create local sentence-transformer embeddings and search them with Chroma using cosine distance.
- Generate grounded answers from retrieved document context using the Groq API (`openai/gpt-oss-120b`).
- Show source file and page, slide, paragraph, or table row for retrieved text, plus inspectable retrieved chunks.
- Ask the model to use an exact refusal response when the documents do not contain the answer.

## How it works

1. The React frontend uploads documents to the FastAPI backend (`POST /api/upload`).
2. The backend extracts text while retaining each unit's file and location.
3. Text is split into overlapping chunks without crossing page, slide, or paragraph boundaries.
4. Sentence Transformers creates local embeddings, which Chroma indexes for semantic search.
5. When a question is submitted (`POST /api/ask`), the backend retrieves the closest chunks and sends them with the question to Groq.
6. The answer, source citations, and inspectable retrieved chunks are displayed in the chat UI.

## Run locally

Use Python 3.10 or newer and Node.js 18 or newer. From the project folder in PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
```

Add your Groq API key and model ID to `.env`:

```text
GROQ_API_KEY=your-key
GROQ_MODEL_ID=openai/gpt-oss-120b
```

Install frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

Start the FastAPI backend (terminal 1):

```powershell
uvicorn api:app --reload --port 8000
```

Start the React frontend (terminal 2):

```powershell
cd frontend
npm run dev
```

Open `http://localhost:5173` in your browser and upload documents from the sidebar. The first run downloads the embedding model; asking a question requires internet access and a valid Groq API key.

## Privacy and limitations

- Embeddings and retrieval run locally in memory for the current app session.
- Retrieved document excerpts and the question are sent to Groq to generate an answer. Do not upload sensitive documents unless you are comfortable with that.
- Answer generation uses the Groq Chat Completions API with a 45-second request timeout.
- Scanned PDFs without selectable text are not OCR-processed.
- The model can still produce incorrect answers or fail to refuse when evidence is missing. Check its citations against the original documents.
- PDF sources use page numbers, PPTX sources use slide numbers, and DOCX sources use paragraph or table-row numbers.

## Project files

| File | Purpose |
| --- | --- |
| `api.py` | FastAPI backend exposing `/api/upload`, `/api/ask`, `/api/session`, and `/api/health` |
| `frontend/` | React + Vite frontend (`index.html`, `src/App.jsx`, `src/api.js`, `src/styles.css`) |
| `pdf_utils.py` | Text extraction with source locations for each supported format |
| `embeddings.py` | Loads and uses the local Sentence Transformer model |
| `vectorstore.py` | Stores and retrieves embedded chunks with Chroma |
| `qa_engine.py` | Chunks documents, builds grounded prompts, and returns answers and sources |
| `llm.py` | Calls Groq and reports API configuration or generation errors |
| `config.py` | Shared model and chunking settings |
