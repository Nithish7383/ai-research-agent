import re
import logging
import streamlit as st
from dotenv import load_dotenv
from langchain.callbacks import StreamlitCallbackHandler

load_dotenv()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
)
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔎",
    layout="centered",
)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------
st.markdown("""
<style>
.block-container { padding-top: 2rem; padding-bottom: 2rem; }
.stChatMessage { border-radius: 12px; }

.source-box {
    background-color: #1e1e2e;
    border-left: 3px solid #7c83fd;
    padding: 0.6rem 1rem;
    border-radius: 6px;
    margin-top: 0.8rem;
    font-size: 0.85rem;
}
.source-box a { color: #7c83fd; text-decoration: none; }
.source-box a:hover { text-decoration: underline; }

/* Starter question pills */
.starter-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 0.5rem;
    margin-top: 1.2rem;
}
.starter-btn {
    background: transparent;
    border: 1px solid rgba(124,131,253,0.35);
    border-radius: 10px;
    padding: 0.55rem 0.75rem;
    font-size: 0.82rem;
    color: #a0a8f8;
    cursor: pointer;
    text-align: left;
    line-height: 1.4;
    transition: background 0.15s;
    width: 100%;
}
.starter-btn:hover { background: rgba(124,131,253,0.1); }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Starter questions
# ---------------------------------------------------------------------------
STARTER_QUESTIONS = [
    "🚀 Latest AI news this week",
    "🏏 Virat Kohli's recent cricket stats",
    "💹 What is the current Bitcoin price?",
    "🌍 Latest news from Tamil Nadu",
    "🧬 Recent breakthroughs in cancer research",
    "🎬 Top movies releasing this month",
]

# ---------------------------------------------------------------------------
# Per-session agent init
# ---------------------------------------------------------------------------
if "agent" not in st.session_state:
    try:
        from src.agent import build_agent
        st.session_state.agent = build_agent()
        logger.info("New agent created for session.")
    except EnvironmentError as e:
        st.error(f"🚨 Configuration error: {e}")
        st.stop()
    except Exception as e:
        st.error(f"🚨 Failed to initialise agent: {e}")
        logger.exception("Agent init failed.")
        st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "pending_prompt" not in st.session_state:
    st.session_state.pending_prompt = None

# ---------------------------------------------------------------------------
# Helper — render response + sources
# ---------------------------------------------------------------------------
def render_response_with_sources(text: str):
    url_pattern = r'https?://[^\s\)\]\,\>\"\']+'
    urls = list(dict.fromkeys(re.findall(url_pattern, text)))

    clean_text = re.sub(url_pattern, '', text)
    clean_text = re.sub(r'\n{3,}', '\n\n', clean_text).strip()
    st.markdown(clean_text)

    if urls:
        sources_html = '<div class="source-box"><strong>🔗 Sources</strong><br>'
        for url in urls:
            domain = re.sub(r'https?://(www\.)?', '', url).split('/')[0]
            sources_html += f'<a href="{url}" target="_blank">↗ {domain}</a><br>'
        sources_html += '</div>'
        st.markdown(sources_html, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Helper — run agent and return response string
# ---------------------------------------------------------------------------
def run_agent(user_prompt: str) -> str:
    st_cb = StreamlitCallbackHandler(
        st.container(),
        expand_new_thoughts=False,
        collapse_completed_thoughts=True,
    )
    try:
        return st.session_state.agent.run(input=user_prompt, callbacks=[st_cb])
    except ValueError as e:
        logger.warning(f"Max iterations: {e}")
        return (
            "⚠️ The agent reached its search limit. "
            "Try rephrasing or breaking into smaller questions."
        )
    except Exception as e:
        error_str = str(e).lower()
        logger.exception(f"Agent run failed: '{user_prompt}'")
        if "rate limit" in error_str or "429" in error_str:
            return "⚠️ Rate limit reached. Please wait a few seconds and try again."
        elif "api key" in error_str or "authentication" in error_str:
            return "🚨 API key error. Please check your GROQ_API_KEY in .env."
        return f"⚠️ Unexpected error: {e}"

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.title("🔎 AI Research Assistant")
    st.write(
        "Ask anything — the agent searches the web in real time and "
        "summarises the answer with sources."
    )
    st.markdown("---")

    st.subheader("⚙️ Tech Stack")
    st.write("• LangChain (Conversational Agent)")
    st.write("• Groq LLM  (llama-3.3-70b-versatile)")
    st.write("• DuckDuckGo Search  (free, no API key)")
    st.write("• Streamlit  (streaming UI)")
    st.markdown("---")

    st.subheader("🧠 Memory")
    msg_count = len(st.session_state.messages)
    st.write(f"Messages this session: **{msg_count}**")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        from src.agent import build_agent
        st.session_state.agent = build_agent()
        st.rerun()

    # ── Export chat ──────────────────────────────────────────────────────────
    if st.session_state.messages:
        st.markdown("---")
        st.subheader("⬇️ Export")
        chat_export = "\n\n".join(
            f"{'You' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
            for m in st.session_state.messages
        )
        st.download_button(
            label="📄 Download chat as .md",
            data=chat_export,
            file_name="research_session.md",
            mime="text/markdown",
            use_container_width=True,
        )

    st.markdown("---")
    st.caption("Built by Nithish · powered by Groq + DuckDuckGo")

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.title("🔎 AI Research Assistant")
st.caption("Real-time web search · Summarised answers · Source citations")
st.markdown("---")

# ---------------------------------------------------------------------------
# Render chat history
# ---------------------------------------------------------------------------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            render_response_with_sources(message["content"])
        else:
            st.markdown(message["content"])

# ---------------------------------------------------------------------------
# Empty state — starter questions
# ---------------------------------------------------------------------------
if not st.session_state.messages:
    st.markdown("#### 💡 Try asking...")
    cols = st.columns(2)
    for i, question in enumerate(STARTER_QUESTIONS):
        with cols[i % 2]:
            if st.button(question, key=f"starter_{i}", use_container_width=True):
                # Strip the emoji prefix before sending to agent
                clean_q = re.sub(r'^[\U00010000-\U0010ffff\u2600-\u26FF\u2700-\u27BF]\s*', '', question).strip()
                st.session_state.pending_prompt = clean_q
                st.rerun()

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
prompt = st.chat_input("Ask a research question...") or st.session_state.pending_prompt

if st.session_state.pending_prompt:
    st.session_state.pending_prompt = None

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response = run_agent(prompt)
        render_response_with_sources(response)

    st.session_state.messages.append({"role": "assistant", "content": response})