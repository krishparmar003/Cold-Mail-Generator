# ✉️ Cold Mail Generator

Paste a company's careers page URL → get a personalized cold email instantly.

**Live Demo → [cold-mail-generatorbykrish.streamlit.app](https://cold-mail-generatorbykrish.streamlit.app/)**

Built with LangChain, Groq (LLaMA 3.3 70B), ChromaDB, and Streamlit.

---

## Architecture

<img width="1400" height="520" alt="architecture" src="https://github.com/user-attachments/assets/42288312-1e14-4043-adc8-e233e55d8826" />

---

## How it works

1. Scrapes the careers page from the URL you provide
2. LLM extracts job details (role, skills, experience) as JSON
3. Matches your portfolio links from a vector store based on required skills
4. LLM writes a personalized cold email using the job + your portfolio

---

## Tech Stack

| Layer | Tools |
|---|---|
| LLM | LLaMA 3.3 70B via Groq |
| Orchestration | LangChain |
| Vector Store | ChromaDB |
| Scraping | LangChain WebBaseLoader |
| UI | Streamlit |

---

## Run Locally

```bash
git clone https://github.com/krishparmar003/Cold-Mail-Generator.git
cd Cold-Mail-Generator
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```
Get your free key at [console.groq.com](https://console.groq.com)

```bash
streamlit run app.py
```

---

## Project Structure

```
Cold-Mail-Generator/
├── app.py               # Streamlit app
├── my_portfolio.csv     # Your portfolio data (techstack + links)
├── architecture.png     # Architecture diagram
├── requirements.txt
└── .gitignore
```
---

*MIT License*
