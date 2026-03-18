# 🔎 AI Research Assistant

An **AI-powered research assistant** that searches the web in real time and returns summarised answers with source citations.

Built with **LangChain**, **Groq LLM**, **Tavily Search**, and **Streamlit**.

---

## ✨ Features

| Feature | Status |
|---|---|
| LLM Agent with real-time web search | ✅ |
| Streaming responses (token by token) | ✅ |
| Per-session conversation memory | ✅ |
| Source citations in every answer | ✅ |
| Tavily search (DuckDuckGo fallback) | ✅ |
| Graceful error handling (rate limits, API errors) | ✅ |
| Clear chat resets both UI and agent memory | ✅ |

---

## 🏗 Architecture

```
User Question
     ↓
Streamlit Chat UI  (per-session agent)
     ↓
LangChain Conversational Agent
  ├── ConversationBufferWindowMemory  (last 10 turns)
  └── Tavily Search Tool  (DuckDuckGo fallback)
     ↓
Groq LLM  (llama-3.1-8b-instant, streaming)
     ↓
Streaming Response → UI  +  Source Citations
```

---

## 📂 Project Structure

```
ai-research-agent/
│
├── app.py                  # Streamlit UI — streaming, per-session agent
│
├── src/
│   ├── agent.py            # Agent factory — memory, LLM, tools
│   └── tools.py            # Tavily search tool (DuckDuckGo fallback)
│
├── config/
│   └── prompts.py          # System prompt (edit here to change agent behaviour)
│
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚙️ Installation

```bash
git clone https://github.com/Nithish7383/ai-research-agent.git
cd ai-research-agent

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
GROQ_API_KEY=your_groq_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here   # optional — falls back to DuckDuckGo
```

Get your keys:
- Groq: https://console.groq.com
- Tavily: https://app.tavily.com  (free tier: 1000 searches/month)

Run:

```bash
streamlit run app.py
```

---

## 🔑 Key Fixes vs Original

| Issue | Original | Fixed |
|---|---|---|
| Agent memory | ❌ Stateless (forgot every turn) | ✅ `ConversationBufferWindowMemory` |
| Multi-user safety | ❌ Global agent shared across users | ✅ Per-session agent in `st.session_state` |
| Streaming | ❌ Spinner, waited for full response | ✅ `StreamlitCallbackHandler` streams tokens live |
| Search reliability | ❌ DuckDuckGo only (rate-limits heavily) | ✅ Tavily primary, DuckDuckGo fallback |
| Error handling | ❌ Bare `except` hid all errors | ✅ Specific handlers for rate limits, API errors |
| Prompt config | ❌ Buried in agent init | ✅ Versioned in `config/prompts.py` |
| Clear chat | ❌ Only cleared UI messages | ✅ Also resets agent's LangChain memory |

---

## 🚀 Planned Upgrades

- [ ] LangGraph multi-agent workflow (planner + researcher + writer)
- [ ] PDF / document ingestion tool
- [ ] Response caching for repeated queries
- [ ] Deploy to Streamlit Cloud