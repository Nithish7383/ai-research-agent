import streamlit as st
from src.agent import agent

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔎",
    layout="centered"
)

# -------- Header --------
st.title("🔎 AI Research Assistant")
st.caption("Search the web and get summarized answers.")

st.markdown("---")

# -------- Chat Memory --------
if "messages" not in st.session_state:
    st.session_state.messages = []

# -------- Display Chat --------
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# -------- Input --------
prompt = st.chat_input("Ask a question...")

if prompt:

    # show user message
    st.session_state.messages.append(
        {"role": "user", "content": prompt}
    )

    with st.chat_message("user"):
        st.markdown(prompt)

    # generate response
    with st.chat_message("assistant"):
        with st.spinner("Researching..."):

            try:
                response = agent.run(prompt)

            except Exception:
                response = "⚠️ Rate limit reached. Please try again later."

        st.markdown(response)

    # save assistant response
    st.session_state.messages.append(
        {"role": "assistant", "content": response}
    )