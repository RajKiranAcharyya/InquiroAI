import hashlib

import streamlit as st

from pdf_utils import extract_text_from_files
from qa_engine import AcademicQAEngine


st.set_page_config(page_title="InquiroAI", layout="wide")
st.title("InquiroAI")
st.write("Ask questions about your PDFs, Word documents, and PowerPoint presentations.")

with st.sidebar:
    st.subheader("Document upload")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or PPTX files",
        type=["pdf", "docx", "pptx"],
        accept_multiple_files=True,
    )
    if uploaded_files:
        st.caption(f"{len(uploaded_files)} file(s) selected")


def get_upload_signature(files):
    digest = hashlib.sha256()
    for file in files or []:
        digest.update(file.name.encode("utf-8"))
        digest.update(file.getvalue())
    return digest.hexdigest()


if "upload_signature" not in st.session_state:
    st.session_state.upload_signature = None
if "qa_engine" not in st.session_state:
    st.session_state.qa_engine = None
if "conversation" not in st.session_state:
    st.session_state.conversation = []

upload_signature = get_upload_signature(uploaded_files)
if upload_signature != st.session_state.upload_signature:
    st.session_state.upload_signature = upload_signature
    st.session_state.qa_engine = None
    st.session_state.conversation = []

    if uploaded_files:
        with st.spinner("Extracting text and building the search index..."):
            document_units = extract_text_from_files(uploaded_files)
            if document_units:
                st.session_state.qa_engine = AcademicQAEngine(document_units)

        if st.session_state.qa_engine:
            st.success("Documents are ready. Ask a question below.")
        else:
            st.error("No readable text was found in the uploaded documents.")

if st.session_state.qa_engine:
    st.subheader("Ask your documents")
    with st.form("question_form", clear_on_submit=True):
        question = st.text_input("Question")
        submitted = st.form_submit_button("Ask")

    if submitted:
        if not question.strip():
            st.warning("Enter a question before asking.")
        else:
            try:
                with st.spinner("Searching your documents and preparing an answer..."):
                    result = st.session_state.qa_engine.answer_question(question)
                st.session_state.conversation.append(
                    {"question": question, "result": result}
                )
            except (RuntimeError, ValueError) as error:
                st.error(str(error))

    for turn in reversed(st.session_state.conversation):
        with st.chat_message("user"):
            st.write(turn["question"])
        with st.chat_message("assistant"):
            st.write(turn["result"]["answer"])
            st.markdown("**Sources**")
            for file_name, location in turn["result"]["sources"]:
                st.write(f"{file_name}, {location}")
else:
    st.info("Upload documents in the sidebar to begin.")
