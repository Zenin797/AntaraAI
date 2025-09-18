"""
Tools configuration for the LTM application.

This module defines and configures the tools available to the agent.
"""
from langchain_community.tools import SearxSearchResults
from langchain_community.utilities import SearxSearchWrapper
from langchain_core.tools import StructuredTool
from typing import List

from config.app_config import get_config
from Tools.SystemMemoryManager import get_memory_usage
from core.memory_manager import search_recall_memories, save_recall_memory_knowledge_triple
from Tools.GmailTool import gmail_tools

save_recall_memory_tool = StructuredTool.from_function(
    func=save_recall_memory_knowledge_triple,
    name="save_recall_memory",
    description="Save memory to vectorstore for later semantic retrieval."
)

search_recall_memories_tool = StructuredTool.from_function(
    func=search_recall_memories,
    description="Search for relevant memories based on the current conversation context."
)

get_memory_usage_tool = StructuredTool.from_function(
    func=get_memory_usage,
    description="Get the current system memory usage as a float type percentage."
)

search_internet_tool = SearxSearchResults(
    num_results=5,
    wrapper=SearxSearchWrapper(searx_host=get_config("searx_host"))
)

all_tools = [
    save_recall_memory_tool,
    search_recall_memories_tool,
    get_memory_usage_tool,
    # *gmail_tools(),
]