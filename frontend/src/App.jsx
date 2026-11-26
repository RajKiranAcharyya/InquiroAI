import { useEffect, useRef, useState } from "react";
import { askQuestion, clearSession, uploadDocuments } from "./api.js";

const REFUSAL_SENTENCE = "I could not find this in the documents.";

const STARTER_PROMPTS = [
  "Give me a concise summary of the main topics covered.",
  "What are the key takeaways or conclusions?",
  "List any important definitions, frameworks, or metrics mentioned.",
];

function formatFileSize(bytes) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function getFileTypeMeta(filename) {
  const ext = filename.split(".").pop()?.toLowerCase() || "";
  if (ext === "pdf") return { label: "PDF", className: "badge-pdf" };
  if (ext === "docx") return { label: "DOCX", className: "badge-docx" };
  if (ext === "pptx") return { label: "PPTX", className: "badge-pptx" };
  return { label: "DOC", className: "badge-default" };
}

function formatSimilarity(distance) {
  if (typeof distance !== "number" || Number.isNaN(distance)) return null;
  const similarity = Math.max(0, Math.min(1, 1 - distance));
  return `${Math.round(similarity * 100)}% match`;
}

function SparkIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3l1.9 5.8L20 11l-6.1 2.2L12 19l-1.9-5.8L4 11l6.1-2.2L12 3z" />
    </svg>
  );
}

function UploadCloudIcon() {
  return (
    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" />
      <polyline points="17 8 12 3 7 8" />
      <line x1="12" y1="3" x2="12" y2="15" />
    </svg>
  );
}

function SendIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="22" y1="2" x2="11" y2="13" />
      <polygon points="22 2 15 22 11 13 2 9 22 2" />
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function CheckIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

export default function App() {
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  const [selectedFiles, setSelectedFiles] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [indexStats, setIndexStats] = useState(null);
  const [isReady, setIsReady] = useState(false);
  const [isIndexing, setIsIndexing] = useState(false);
  const [indexNotice, setIndexNotice] = useState(null);
  const [isDragging, setIsDragging] = useState(false);

  const [question, setQuestion] = useState("");
  const [isAsking, setIsAsking] = useState(false);
  const [askWarning, setAskWarning] = useState("");
  const [askError, setAskError] = useState("");
  const [conversation, setConversation] = useState([]);
  const [expandedEvidence, setExpandedEvidence] = useState({});
  const [copiedTurnId, setCopiedTurnId] = useState(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [conversation, isAsking]);

  async function processFiles(fileList) {
    const incoming = Array.from(fileList || []);
    if (incoming.length === 0) return;

    setSelectedFiles(incoming);
    setIsReady(false);
    setIndexStats(null);
    setIsIndexing(true);
    setIndexNotice(null);
    setAskWarning("");
    setAskError("");
    setConversation([]);
    setExpandedEvidence({});

    try {
      const data = await uploadDocuments(incoming, sessionId);
      setSessionId(data.session_id);
      setIndexStats({
        fileCount: data.file_count,
        unitCount: data.unit_count,
        chunkCount: data.chunk_count,
      });
      setIsReady(true);
      setIndexNotice({
        type: "success",
        text: data.message || "Documents are ready. Ask a question below.",
      });
    } catch (error) {
      setIsReady(false);
      setIndexNotice({
        type: "error",
        text: error.message || "No readable text was found in the uploaded documents.",
      });
    } finally {
      setIsIndexing(false);
    }
  }

  function handleFileChange(event) {
    processFiles(event.target.files);
    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();
    setIsDragging(false);
    processFiles(event.dataTransfer.files);
  }

  async function handleClearDocuments() {
    const activeId = sessionId;
    setSelectedFiles([]);
    setSessionId(null);
    setIndexStats(null);
    setIsReady(false);
    setIndexNotice(null);
    setConversation([]);
    setExpandedEvidence({});
    setQuestion("");
    setAskWarning("");
    setAskError("");
    try {
      await clearSession(activeId);
    } catch {
      // Ignore cleanup failures during local UI reset.
    }
  }

  async function submitQuestion(text) {
    setAskWarning("");
    setAskError("");

    const trimmed = text.trim();
    if (!trimmed) {
      setAskWarning("Enter a question before asking.");
      return;
    }

    setQuestion("");
    setIsAsking(true);

    try {
      const result = await askQuestion(sessionId, trimmed);
      setConversation((prev) => [
        ...prev,
        { id: crypto.randomUUID(), question: trimmed, result },
      ]);
    } catch (error) {
      setAskError(error.message || "Failed to generate an answer.");
    } finally {
      setIsAsking(false);
    }
  }

  function handleAskSubmit(event) {
    event.preventDefault();
    submitQuestion(question);
  }

  function toggleEvidence(turnId) {
    setExpandedEvidence((prev) => ({
      ...prev,
      [turnId]: !prev[turnId],
    }));
  }

  async function handleCopyAnswer(turnId, answerText) {
    try {
      await navigator.clipboard.writeText(answerText);
      setCopiedTurnId(turnId);
      setTimeout(() => {
        setCopiedTurnId((current) => (current === turnId ? null : current));
      }, 1800);
    } catch {
      // Clipboard access may be unavailable in restricted contexts.
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">
            <SparkIcon />
          </div>
          <div>
            <div className="brand-name">InquiroAI</div>
            <div className="brand-tag">Grounded Document RAG</div>
          </div>
        </div>

        <div className="sidebar-block">
          <div className="block-header">
            <h2>Knowledge Base</h2>
            <span className="format-pills">PDF &bull; DOCX &bull; PPTX</span>
          </div>

          <div
            className={`dropzone ${isDragging ? "dropzone-active" : ""}`}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            onClick={() => !isIndexing && fileInputRef.current?.click()}
            role="button"
            tabIndex={0}
            onKeyDown={(event) => {
              if ((event.key === "Enter" || event.key === " ") && !isIndexing) {
                event.preventDefault();
                fileInputRef.current?.click();
              }
            }}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.pptx"
              multiple
              onChange={handleFileChange}
              className="file-input-hidden"
            />
            <div className="dropzone-icon">
              <UploadCloudIcon />
            </div>
            <div className="dropzone-title">
              {isIndexing ? "Indexing documents..." : "Drop files or click to browse"}
            </div>
            <div className="dropzone-subtitle">
              Multi-file upload with page, slide &amp; paragraph citations
            </div>
          </div>
        </div>

        {selectedFiles.length > 0 && (
          <div className="sidebar-block file-block">
            <div className="file-section-header">
              <span className="file-count">
                {selectedFiles.length} file{selectedFiles.length > 1 ? "s" : ""} loaded
              </span>
              <button
                type="button"
                className="ghost-button"
                onClick={handleClearDocuments}
                disabled={isIndexing}
              >
                Clear all
              </button>
            </div>

            <ul className="file-list">
              {selectedFiles.map((file) => {
                const meta = getFileTypeMeta(file.name);
                return (
                  <li key={`${file.name}-${file.size}`} className="file-item">
                    <span className={`file-badge ${meta.className}`}>{meta.label}</span>
                    <div className="file-meta">
                      <span className="file-name" title={file.name}>
                        {file.name}
                      </span>
                      <span className="file-size">{formatFileSize(file.size)}</span>
                    </div>
                  </li>
                );
              })}
            </ul>

            {indexStats && (
              <div className="stats-grid">
                <div className="stat-card">
                  <span className="stat-value">{indexStats.unitCount}</span>
                  <span className="stat-label">Pages / Units</span>
                </div>
                <div className="stat-card">
                  <span className="stat-value">{indexStats.chunkCount}</span>
                  <span className="stat-label">Vector Chunks</span>
                </div>
              </div>
            )}
          </div>
        )}

        <div className="sidebar-footer">
          <div className="tech-pill">MiniLM-L6-v2 &bull; Chroma Cosine &bull; Groq</div>
        </div>
      </aside>

      <div className="workspace">
        <header className="topbar">
          <div className="topbar-left">
            <h1 className="topbar-title">Ask Your Documents</h1>
            <span
              className={`status-pill ${
                isIndexing
                  ? "status-indexing"
                  : isReady
                  ? "status-ready"
                  : "status-idle"
              }`}
            >
              <span className="status-dot" />
              {isIndexing
                ? "Indexing..."
                : isReady
                ? `Ready • ${indexStats?.chunkCount || 0} chunks`
                : "No documents indexed"}
            </span>
          </div>

          {conversation.length > 0 && (
            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                setConversation([]);
                setExpandedEvidence({});
                setAskError("");
                setAskWarning("");
              }}
              disabled={isAsking}
            >
              Clear chat
            </button>
          )}
        </header>

        <div className="messages-scroll">
          {isIndexing && (
            <div className="banner banner-info" role="status">
              <span className="spinner" aria-hidden="true" />
              <span>Extracting text, chunking boundaries, and building Chroma index...</span>
            </div>
          )}

          {indexNotice && (
            <div
              className={`banner ${
                indexNotice.type === "success" ? "banner-success" : "banner-error"
              }`}
              role="status"
            >
              {indexNotice.text}
            </div>
          )}

          {!isReady && !isIndexing && (
            <div className="empty-state">
              <div className="empty-hero">
                <div className="empty-icon">
                  <SparkIcon />
                </div>
                <h2>Chat directly with your documents</h2>
                <p>
                  Upload PDFs, Word documents, or PowerPoint decks from the sidebar.
                  InquiroAI indexes every page, paragraph, table row, and slide locally
                  and generates answers strictly grounded in your files.
                </p>
              </div>

              <div className="pipeline-cards">
                <div className="pipeline-card">
                  <span className="step-num">01</span>
                  <h3>Upload Formats</h3>
                  <p>PDF pages, DOCX paragraphs &amp; tables, and PPTX slides extracted with exact locations.</p>
                </div>
                <div className="pipeline-card">
                  <span className="step-num">02</span>
                  <h3>Semantic Search</h3>
                  <p>Local MiniLM embeddings indexed in an isolated Chroma cosine vector store.</p>
                </div>
                <div className="pipeline-card">
                  <span className="step-num">03</span>
                  <h3>Cited Answers</h3>
                  <p>Groq answers only from retrieved chunks and refuses out-of-scope questions.</p>
                </div>
              </div>
            </div>
          )}

          {isReady && conversation.length === 0 && !isAsking && (
            <div className="starter-box">
              <div className="starter-heading">Try a starter question</div>
              <div className="starter-chips">
                {STARTER_PROMPTS.map((prompt) => (
                  <button
                    key={prompt}
                    type="button"
                    className="starter-chip"
                    onClick={() => submitQuestion(prompt)}
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="chat-thread">
            {conversation.map((turn) => {
              const isRefusal =
                turn.result.answer?.trim() === REFUSAL_SENTENCE;
              const isEvidenceOpen = Boolean(expandedEvidence[turn.id]);

              return (
                <article key={turn.id} className="turn-block">
                  <div className="message-row message-user">
                    <div className="msg-bubble user-bubble">
                      {turn.question}
                    </div>
                  </div>

                  <div className="message-row message-assistant">
                    <div className="assistant-avatar" aria-hidden="true">
                      <SparkIcon />
                    </div>
                    <div className="assistant-card">
                      <div className="assistant-card-header">
                        <span className="assistant-label">InquiroAI</span>
                        <button
                          type="button"
                          className="copy-button"
                          onClick={() =>
                            handleCopyAnswer(turn.id, turn.result.answer)
                          }
                        >
                          {copiedTurnId === turn.id ? (
                            <>
                              <CheckIcon />
                              <span>Copied</span>
                            </>
                          ) : (
                            <>
                              <CopyIcon />
                              <span>Copy</span>
                            </>
                          )}
                        </button>
                      </div>

                      <div
                        className={`assistant-answer ${
                          isRefusal ? "answer-refusal" : ""
                        }`}
                      >
                        {turn.result.answer}
                      </div>

                      {!isRefusal && turn.result.sources?.length > 0 && (
                        <div className="citations-block">
                          <span className="citations-label">Sources</span>
                          <div className="citations-list">
                            {turn.result.sources.map((item) => (
                              <span
                                key={`${item.file}-${item.source}`}
                                className="citation-pill"
                              >
                                {item.file} &middot; {item.source}
                              </span>
                            ))}
                          </div>
                        </div>
                      )}

                      {turn.result.chunks?.length > 0 && (
                        <div className="evidence-wrapper">
                          <button
                            type="button"
                            className="evidence-toggle"
                            onClick={() => toggleEvidence(turn.id)}
                          >
                            {isEvidenceOpen ? "Hide" : "Inspect"} retrieved chunks (
                            {turn.result.chunks.length})
                          </button>

                          {isEvidenceOpen && (
                            <div className="evidence-list">
                              {turn.result.chunks.map((chunk, index) => {
                                const matchLabel = formatSimilarity(
                                  chunk.distance
                                );
                                return (
                                  <div
                                    key={`${chunk.file}-${chunk.source}-${index}`}
                                    className="evidence-item"
                                  >
                                    <div className="evidence-meta">
                                      <span>
                                        {chunk.file} &bull; {chunk.source}
                                      </span>
                                      {matchLabel && (
                                        <span className="match-badge">
                                          {matchLabel}
                                        </span>
                                      )}
                                    </div>
                                    <p className="evidence-text">{chunk.text}</p>
                                  </div>
                                );
                              })}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </article>
              );
            })}

            {isAsking && (
              <div className="message-row message-assistant">
                <div className="assistant-avatar" aria-hidden="true">
                  <SparkIcon />
                </div>
                <div className="assistant-card thinking-card">
                  <span className="spinner" aria-hidden="true" />
                  <span>Searching your documents and generating grounded answer...</span>
                </div>
              </div>
            )}

            <div ref={chatEndRef} />
          </div>
        </div>

        <footer className="composer-dock">
          {askWarning && (
            <div className="banner banner-warning" role="alert">
              {askWarning}
            </div>
          )}

          {askError && (
            <div className="banner banner-error" role="alert">
              {askError}
            </div>
          )}

          <form className="composer-form" onSubmit={handleAskSubmit}>
            <input
              id="question-input"
              type="text"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
              placeholder={
                isReady
                  ? "Ask anything about your uploaded documents..."
                  : "Upload PDF, DOCX, or PPTX files in the sidebar to start..."
              }
              disabled={!isReady || isAsking || isIndexing}
            />
            <button
              type="submit"
              className="send-button"
              disabled={!isReady || isAsking || isIndexing}
            >
              <SendIcon />
              <span>{isAsking ? "Asking" : "Ask"}</span>
            </button>
          </form>
        </footer>
      </div>
    </div>
  );
}
