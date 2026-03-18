import os
from langchain.agents import AgentExecutor, create_react_agent
from langchain_groq import ChatGroq
from langchain.memory import ConversationBufferWindowMemory
from langchain_core.prompts import PromptTemplate
from dotenv import load_dotenv
from src.tools import get_tools

load_dotenv()


# -------------------------------------------------------
# Custom ReAct prompt — research-focused, structured output
# -------------------------------------------------------
RESEARCH_PROMPT = PromptTemplate.from_template("""
You are an expert AI research assistant. Your job is to search the web and provide 
accurate, well-structured, and sourced answers to user questions.

You have access to the following tools:
{tools}

Use the following format STRICTLY:

Question: the input question you must answer
Thought: think about what you need to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat up to 4 times)
Thought: I now know the final answer
Final Answer: [Write a well-structured response with:
- A direct answer to the question
- Key facts and details
- Sources mentioned if available]

Previous conversation:
{chat_history}

Question: {input}
Thought: {agent_scratchpad}
""")


def build_agent() -> AgentExecutor:
    """
    Build and return a LangChain ReAct AgentExecutor with:
    - Groq LLM (fast inference)
    - DuckDuckGo web search tool
    - Sliding window conversation memory (last 5 turns)
    - Streaming enabled
    - Intermediate steps returned for UI display
    """

    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise ValueError("GROQ_API_KEY not found in environment. Check your .env file.")

    llm = ChatGroq(
        model="llama-3.3-70b-versatile",  # ✅ Updated — llama3-8b-8192 is decommissioned
        temperature=0,
        streaming=True,
        groq_api_key=groq_api_key,
    )

    tools = get_tools()

    # Window memory — keeps last 5 conversation turns
    # This prevents context overflow on long sessions
    memory = ConversationBufferWindowMemory(
        k=5,
        memory_key="chat_history",
        return_messages=False,  # Return as string, not message objects (ReAct needs string)
        input_key="input",
        output_key="output",
    )

    agent = create_react_agent(
        llm=llm,
        tools=tools,
        prompt=RESEARCH_PROMPT,
    )

    agent_executor = AgentExecutor(
        agent=agent,
        tools=tools,
        memory=memory,
        verbose=True,                  # Prints reasoning to terminal (helpful for debugging)
        handle_parsing_errors=True,    # Recovers from LLM formatting mistakes
        max_iterations=5,              # Prevents infinite loops
        max_execution_time=30,         # 30 second timeout per query
        return_intermediate_steps=True,  # Exposes tool calls to the UI
    )

    return agent_executor


# Singleton — one agent instance shared across all Streamlit reruns
agent_executor = build_agent()