import os
import logging
from langchain_groq import ChatGroq
from langchain.agents import AgentType, initialize_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import MessagesPlaceholder
from langchain_core.messages import SystemMessage

from src.tools import build_tools
from config.prompts import SYSTEM_PROMPT, FORCED_SEARCH_PREFIX

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
GROQ_MODEL = "llama-3.3-70b-versatile"
MEMORY_WINDOW = 10
TEMPERATURE = 0.2
MAX_ITERATIONS = 8   # increased — agent must search before answering


def build_agent():
    """
    Build and return a CONVERSATIONAL LangChain agent with:
      - Per-session ConversationBufferWindowMemory (no cross-user bleed)
      - Groq LLM with streaming enabled
      - DuckDuckGo search tool
      - FORCED_SEARCH_PREFIX that makes web_search mandatory on every query
      - Iteration limit to prevent runaway calls
    """
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise EnvironmentError(
            "GROQ_API_KEY is not set. Please add it to your .env file."
        )

    # -----------------------------------------------------------------------
    # LLM
    # -----------------------------------------------------------------------
    llm = ChatGroq(
        api_key=groq_api_key,
        model_name=GROQ_MODEL,
        temperature=TEMPERATURE,
        streaming=True,
    )

    # -----------------------------------------------------------------------
    # Tools
    # -----------------------------------------------------------------------
    tools = build_tools()

    # -----------------------------------------------------------------------
    # Memory
    # -----------------------------------------------------------------------
    memory = ConversationBufferWindowMemory(
        k=MEMORY_WINDOW,
        memory_key="chat_history",
        return_messages=True,
    )

    # -----------------------------------------------------------------------
    # Agent
    # Key fix: FORCED_SEARCH_PREFIX is injected as `prefix` in agent_kwargs.
    # This is prepended to the ReAct scratchpad and instructs the agent that
    # its FIRST action must always be web_search before it can give a Final Answer.
    # -----------------------------------------------------------------------
    agent = initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
        memory=memory,
        verbose=True,
        max_iterations=MAX_ITERATIONS,
        early_stopping_method="generate",
        handle_parsing_errors=True,
        agent_kwargs={
            "system_message": SystemMessage(content=SYSTEM_PROMPT),
            "extra_prompt_messages": [
                MessagesPlaceholder(variable_name="chat_history")
            ],
            "prefix": FORCED_SEARCH_PREFIX,
        },
    )

    logger.info(f"Agent built — model={GROQ_MODEL}, memory={MEMORY_WINDOW} turns")
    return agent