import os
import uuid
import re
import streamlit as st
import pandas as pd
#import chromadb
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser

load_dotenv()

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Cold Mail Generator",
    page_icon="✉️",
    layout="centered",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Space Mono', monospace !important;
}

.stApp {
    background: #0a0a0a;
    color: #f0f0f0;
}

.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: #141414;
    border: 1px solid #2a2a2a;
    color: #f0f0f0;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
}

.stButton > button {
    background: #e8ff4a;
    color: #0a0a0a;
    font-family: 'Space Mono', monospace;
    font-weight: 700;
    border: none;
    border-radius: 6px;
    padding: 0.6rem 2rem;
    width: 100%;
    transition: all 0.2s;
}

.stButton > button:hover {
    background: #f5ff80;
    transform: translateY(-1px);
}

.email-output {
    background: #141414;
    border: 1px solid #2a2a2a;
    border-left: 3px solid #e8ff4a;
    border-radius: 8px;
    padding: 1.5rem;
    white-space: pre-wrap;
    font-family: 'DM Sans', sans-serif;
    font-size: 0.95rem;
    line-height: 1.7;
    color: #e0e0e0;
    margin-top: 1rem;
}

.tag {
    display: inline-block;
    background: #1e1e1e;
    border: 1px solid #333;
    color: #e8ff4a;
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    padding: 2px 8px;
    border-radius: 4px;
    margin: 2px;
}

.section-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    color: #666;
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ── LLM setup ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_llm():
    return ChatGroq(
        temperature=0,
        groq_api_key=os.environ["GROQ_API_KEY"],
        model_name="llama-3.3-70b-versatile"
    )


# ── ChromaDB setup ────────────────────────────────────────────────────────────
@st.cache_resource
def get_collection():
    df = pd.read_csv("my_portfolio.csv")
    client = chromadb.PersistentClient("./vectorstore")
    collection = client.get_or_create_collection(name="portfolio")
    if not collection.count():
        for _, row in df.iterrows():
            collection.add(
                documents=row["Techstack"],
                metadatas={"links": row["Links"]},
                ids=[str(uuid.uuid4())]
            )
    return collection


# ── Scrape + extract job JSON ─────────────────────────────────────────────────
def scrape_job(url: str):
    loader = WebBaseLoader(url)
    data = loader.load()
    page_data = data[0].page_content

    llm = get_llm()
    prompt_extract = PromptTemplate.from_template("""
        ### SCRAPED TEXT FROM WEBSITE:
        {page_data}

        ### INSTRUCTION:
        The scraped text is from the career's page of a website.
        Your job is to extract the job postings and return them in JSON format containing the following keys:
        `role`, `experience`, `skills` and `description`.
        Only return valid JSON. No preamble.
        ### VALID JSON (NO PREAMBLE):
    """)
    chain = prompt_extract | llm | JsonOutputParser()
    return chain.invoke({"page_data": page_data})


# ── Generate cold email ───────────────────────────────────────────────────────
def generate_email(job: dict):
    collection = get_collection()
    skills = job.get("skills", [])
    query = ", ".join(skills) if isinstance(skills, list) else str(skills)
    links = collection.query(query_texts=[query], n_results=2).get("metadatas", [])

    llm = get_llm()
    prompt_email = PromptTemplate.from_template("""
        ### JOB DESCRIPTION:
        {job_description}

        ### INSTRUCTION:
        You are Krish, an AI/ML Engineer. You are writing a cold email to the hiring team regarding the job mentioned above.
        Showcase your relevant skills and experience to fulfill their needs.
        Also add the most relevant ones from the following portfolio links to showcase your work: {link_list}
        Write a professional, concise cold email. Do not provide a preamble.
        ### EMAIL (NO PREAMBLE):
    """)
    chain = prompt_email | llm
    res = chain.invoke({"job_description": str(job), "link_list": links})
    return res.content


# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown("## ✉️ Cold Mail Generator")
st.markdown("<p style='color:#666; font-family:DM Sans; margin-top:-0.5rem;'>Paste a job posting URL → get a personalised cold email instantly.</p>", unsafe_allow_html=True)

st.markdown("---")

url = st.text_input("", placeholder="https://careers.company.com/job/...", label_visibility="collapsed")

if st.button("Generate Email"):
    if not url.strip():
        st.warning("Please enter a job URL.")
    else:
        with st.spinner("Scraping job posting..."):
            try:
                job_data = scrape_job(url.strip())
            except Exception as e:
                st.error(f"Could not scrape URL: {e}")
                st.stop()

        # Show extracted job info
        with st.expander("📋 Extracted Job Details", expanded=False):
            if isinstance(job_data, list):
                job_data = job_data[0]
            st.markdown(f"**Role:** {job_data.get('role', 'N/A')}")
            st.markdown(f"**Experience:** {job_data.get('experience', 'N/A')}")
            skills = job_data.get("skills", [])
            if skills:
                st.markdown("**Skills:**")
                st.markdown(" ".join([f'<span class="tag">{s}</span>' for s in skills]), unsafe_allow_html=True)

        with st.spinner("Writing your cold email..."):
            try:
                if isinstance(job_data, list):
                    job_data = job_data[0]
                email = generate_email(job_data)
            except Exception as e:
                st.error(f"Error generating email: {e}")
                st.stop()

        st.markdown("<div class='section-label'>Generated Email</div>", unsafe_allow_html=True)
        st.markdown(f"<div class='email-output'>{email}</div>", unsafe_allow_html=True)
        st.download_button("⬇ Download Email", email, file_name="cold_email.txt", mime="text/plain")
