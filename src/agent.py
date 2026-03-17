from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType, Tool
from src.tools import search_web

load_dotenv()

# -------- System Prompt --------
system_prompt = """
You are an AI Research Assistant.

Your job is to:
- search the internet
- summarize reliable information
- provide concise explanations
- cite sources when possible

Always answer in this format:

### Answer
<clear explanation>

### Sources
- source link
- source link
"""

# -------- LLM --------
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    temperature=0
)

# -------- Tools --------
tools = [
    Tool(
        name="Search",
        func=search_web,
        description="Search the internet for information"
    )
]

# -------- Agent --------
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=False,
    agent_kwargs={"system_message": system_prompt}
)