from langchain.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper


def get_tools():
    """Return all tools available to the agent."""

    wrapper = DuckDuckGoSearchAPIWrapper(max_results=5)
    search = DuckDuckGoSearchRun(
        name="web_search",
        description=(
            "Use this tool to search the web for current information. "
            "Input should be a search query string. "
            "Use this whenever the question requires recent or real-world data."
        ),
        api_wrapper=wrapper,
    )

    return [search, summarize_text]


@tool
def summarize_text(text: str) -> str:
    """
    Summarizes a long block of text into key points.
    Use this when you have retrieved long content and need to condense it.
    Input should be the raw text to summarize.
    """
    # Truncate to avoid context overflow — let the LLM summarize what it gets
    max_chars = 3000
    truncated = text[:max_chars]
    if len(text) > max_chars:
        truncated += "\n\n[Content truncated for length]"
    return truncated