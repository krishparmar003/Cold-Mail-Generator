# Cold Mail Generator

Paste a company's careers page URL → get a personalized cold email instantly.

Built with LangChain, Groq (LLaMA 3.1), ChromaDB, and Streamlit.

---

## How it works

1. Scrapes the careers page
2. LLM extracts job details (title, skills, experience) as JSON
3. Matches your portfolio links from a vector store based on required skills
4. LLM writes a personalized cold email using the job + your portfolio

<img width="1400" height="520" alt="architecture" src="https://github.com/user-attachments/assets/42288312-1e14-4043-adc8-e233e55d8826" />


---

## Setup

```bash
git <--repo link-->
cd Cold-Mail-Generator
pip install -r requirements.txt
```

Create a `.env` file:
```
GROQ_API_KEY=your_key_here
```
Get your free key at [console.groq.com](https://console.groq.com)

```bash
cd app
streamlit run main.py
```

---

## Tech Stack
- **LLM** — LLaMA 3.1-8b via Groq
- **Orchestration** — LangChain
- **Vector Store** — ChromaDB
- **Scraping** — Selenium + BeautifulSoup4
- **UI** — Streamlit

## Acknowledgements
Inspired by [codebasics](https://github.com/codebasics/project-genai-cold-email-generator)
