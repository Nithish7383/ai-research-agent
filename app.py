import streamlit as st
from src.agent import agent_executor

# -------------------------------------------------------
# Page Config
# -------------------------------------------------------
st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🔎",
    layout="centered",
)

# -------------------------------------------------------
# Custom CSS
# -------------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .reasoning-step {
        background-color: #f8f9fa;
        border-left: 3px solid #6c757d;
        padding: 0.5rem 1rem;
        margin-bottom: 0.5rem;
        border-radius: 4px;
        font-size: 0.85rem;
    }
    .tool-badge {
        background-color: #e9ecef;
        padding: 2px 8px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 0.8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------------------------------------
# Sidebar
# -------------------------------------------------------
with st.sidebar:
    st.title("🔎 AI Research Assistant")
    st.write("AI-powered assistant that searches the web and summarizes answers.")
    st.markdown("---")

    st.subheader("⚙️ Tech Stack")
    st.write("• LangChain")
    st.write("• Groq LLM (LLaMA 3)")
    st.write("• DuckDuckGo Search")
    st.write("• Streamlit")
    st.markdown("---")

    st.subheader("🧠 Memory")
    st.caption("Agent remembers last 5 conversation turns.")

    show_reasoning = st.toggle("Show agent reasoning", value=True)
    st.markdown("---")

    if st.button("🗑 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.reasoning_steps = []
        # Reset agent memory too
        agent_executor.memory.clear()
        st.rerun()

    st.caption("Built by Nithish")

# -------------------------------------------------------
# Header
# -------------------------------------------------------
st.title("🔎 AI Research Assistant")
st.caption("Ask anything — I'll search the web and give you a structured answer.")
st.markdown("---")

# -------------------------------------------------------
# Session State Init
# -------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

if "reasoning_steps" not in st.session_state:
    st.session_state.reasoning_steps = []  # list of lists, one per assistant turn

# -------------------------------------------------------
# Render Chat History
# -------------------------------------------------------
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show reasoning steps below each assistant message (if toggled on)
        if (
            message["role"] == "assistant"
            and show_reasoning
            and i // 2 < len(st.session_state.reasoning_steps)
        ):
            steps = st.session_state.reasoning_steps[i // 2]
            if steps:
                with st.expander("🔍 Agent reasoning", expanded=False):
                    for step_num, step in enumerate(steps, 1):
                        action, observation = step
                        st.markdown(
                            f"""
                            <div class="reasoning-step">
                                <span class="tool-badge">Step {step_num} · {action.tool}</span><br>
                                <b>Query:</b> {action.tool_input}<br>
                                <b>Result:</b> {str(observation)[:400]}{'...' if len(str(observation)) > 400 else ''}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

# -------------------------------------------------------
# Chat Input
# -------------------------------------------------------
prompt = st.chat_input("Ask a research question...")

# -------------------------------------------------------
# Handle New User Message
# -------------------------------------------------------
if prompt:
    # 1. Store and display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Run agent and stream response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        status_placeholder = st.empty()

        full_response = ""
        intermediate_steps = []

        try:
            # Show live status while agent is thinking/searching
            status_placeholder.status("🔍 Researching...", state="running")

            result = agent_executor.invoke(
                {
                    "input": prompt,
                    "chat_history": agent_executor.memory.buffer if hasattr(agent_executor.memory, "buffer") else "",
                }
            )

            full_response = result.get("output", "Sorry, I could not generate a response.")
            intermediate_steps = result.get("intermediate_steps", [])

            # Clear status, show final answer
            status_placeholder.empty()
            response_placeholder.markdown(full_response)

            # Show reasoning expander immediately after response
            if show_reasoning and intermediate_steps:
                with st.expander("🔍 Agent reasoning", expanded=True):
                    for step_num, step in enumerate(intermediate_steps, 1):
                        action, observation = step
                        st.markdown(
                            f"""
                            <div class="reasoning-step">
                                <span class="tool-badge">Step {step_num} · {action.tool}</span><br>
                                <b>Query:</b> {action.tool_input}<br>
                                <b>Result:</b> {str(observation)[:400]}{'...' if len(str(observation)) > 400 else ''}
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

        except ValueError as e:
            status_placeholder.empty()
            full_response = f"⚠️ Agent error: {str(e)}"
            response_placeholder.markdown(full_response)

        except TimeoutError:
            status_placeholder.empty()
            full_response = "⏱️ Request timed out. Try a simpler or more specific question."
            response_placeholder.markdown(full_response)

        except Exception as e:
            status_placeholder.empty()
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "429" in error_msg:
                full_response = "⚠️ Rate limit reached. Please wait a moment and try again."
            elif "api key" in error_msg:
                full_response = "🔑 API key error. Check your GROQ_API_KEY in the .env file."
            else:
                full_response = f"❌ Unexpected error: {str(e)}"
            response_placeholder.markdown(full_response)

    # 3. Save assistant message and reasoning steps to session state
    st.session_state.messages.append({"role": "assistant", "content": full_response})
    st.session_state.reasoning_steps.append(intermediate_steps)