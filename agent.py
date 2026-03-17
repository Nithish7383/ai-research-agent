import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain.agents import initialize_agent, AgentType, Tool
from langchain_community.tools import DuckDuckGoSearchRun

load_dotenv()

# LLM
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0
)

# Search tool
search = DuckDuckGoSearchRun()

from tools import search_web
from langchain.agents import Tool

tools = [
    Tool(
        name="Search",
        func=search_web,
        description="Search the internet for information about any topic"
    )
]

# Create agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)