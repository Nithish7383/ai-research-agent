import streamlit as st
from src.agent import agent

# ---------------------------
# Page Config
# ---------------------------

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔎",
    layout="centered"
)

# ---------------------------
# CSS Fix (better spacing)
# ---------------------------

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------------
# Sidebar
# ---------------------------

with st.sidebar:

    st.title("🔎 AI Research Assistant")

    st.write(
        "AI-powered research assistant that searches the web and summarizes answers."
    )

    st.markdown("---")

    st.subheader("Tech Stack")

    st.write("• LangChain")
    st.write("• Groq LLM")
    st.write("• DuckDuckGo Search")
    st.write("• Streamlit")

    st.markdown("---")

    if st.button("🗑 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

    st.caption("Built by Nithish")

# ---------------------------
# Header
# ---------------------------

st.title("🔎 AI Research Assistant")
st.caption("Search the web and get summarized answers.")

st.markdown("---")

# ---------------------------
# Chat Memory
# ---------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------
# Chat Container
# ---------------------------

chat_container = st.container()

with chat_container:

    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# ---------------------------
# Chat Input (Fixed Bottom)
# ---------------------------

prompt = st.chat_input("Ask a question...")

# ---------------------------
# Handle User Prompt
# ---------------------------

if prompt:

    # Save user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):

        with st.spinner("Researching..."):

            try:
                response = agent.run(prompt)

            except Exception:
                response = "⚠️ Rate limit reached. Please try again later."

        st.markdown(response)

    # Save assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )