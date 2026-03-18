import logging
from langchain.tools import Tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_community.utilities import DuckDuckGoSearchAPIWrapper

logger = logging.getLogger(__name__)


def build_tools() -> list:
    """
    Build and return the list of tools available to the agent.
    Uses DuckDuckGo — free, no API key required.
    """
    # DuckDuckGoSearchAPIWrapper gives more control (num results, region, etc.)
    wrapper = DuckDuckGoSearchAPIWrapper(
        max_results=5,
        region="wt-wt",        # worldwide results
        safesearch="moderate",
        time="y",              # results from the past year (keeps answers fresh)
    )

    ddg_search = DuckDuckGoSearchRun(api_wrapper=wrapper)

    tools = [
        Tool(
            name="web_search",
            func=ddg_search.run,
            description=(
                "Use this tool to search the web for current events, facts, "
                "news, or any question that needs up-to-date information. "
                "Input should be a clear and specific search query string. "
                "Use this tool before answering any factual question."
            ),
        )
    ]

    logger.info("Tools built: DuckDuckGo search")
    return tools