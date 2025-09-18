"""
Graph construction for the LTM application.
"""

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from core.state import State
from core.agent import agent, load_memories, route_tools
from core.tools import all_tools

def build_graph(model_with_tools):
    """Build the conversation graph with memory capabilities.
    
    Args:
        model_with_tools: The language model with bound tools
        
    Returns:
        Compiled graph ready for execution
    """
    print("Loading Graph...")
    # Create the graph and add nodes
    builder = StateGraph(State)
    
    # Add nodes
    builder.add_node("load_memories", load_memories)
    builder.add_node("agent", lambda state, config: agent(state, model_with_tools))
    builder.add_node("tools", ToolNode(all_tools))
    
    # Add edges to the graph
    builder.add_edge(START, "load_memories")
    builder.add_edge("load_memories", "agent")
    builder.add_conditional_edges("agent", route_tools, ["tools", END])
    builder.add_edge("tools", "agent")
    
    # Compile the graph
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

def pretty_print_stream_chunk(chunk):
    """Format and print stream chunks from the graph execution.
    
    Args:
        chunk: A chunk of data from the graph's stream method
    """
    for node, updates in chunk.items():
        print(f"Update from node: {node}")
        if "messages" in updates:
            updates["messages"][-1].pretty_print()
        else:
            print(updates)
        print("\n")