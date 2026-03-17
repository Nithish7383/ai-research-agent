import streamlit as st
from src.agent import agent

st.set_page_config(page_title="AI Research Assistant", page_icon="🔎")

st.title("🔎 AI Research Assistant")

query = st.text_input("Ask a question")

if query:
    with st.spinner("Researching..."):
        response = agent.run(query)

    st.success("Answer")
    st.write(response)

st.markdown("---")

st.markdown("### Example Questions")
st.write("- What is a vector database?")
st.write("- How does RAG work?")
st.write("- What is an LLM agent?")