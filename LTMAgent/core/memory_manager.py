from langchain_core.runnables import RunnableConfig
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
import uuid
from typing import List, Optional

from utils.utils import get_user_id, get_thread_id, KnowledgeTriple
from config.app_config import get_config

# Initialize the VectorStore where memories will be stored
print("Initializing Vector Store")
recall_vector_store = InMemoryVectorStore(HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2"))

# Cache configuration values to avoid repeated lookups
VECTOR_K_RESULTS = get_config("vector_k_results", 3)

def save_recall_memory(memory: str, config: RunnableConfig) -> str:
    """Save memory to vectorstore for later semantic retrieval."""
    # Get the user ID and thread ID from the configuration
    user_id = get_user_id(config)
    thread_id = get_thread_id(config)
    
    # Create a document with the memory content and user metadata
    document = Document(
        page_content=memory.strip(),  # Basic cleanup - just trim whitespace
        id=str(uuid.uuid4()), 
        metadata={
            "user_id": user_id, 
            "thread_id": thread_id,
            "timestamp": str(uuid.uuid1())
        }
    )
    
    # Add the document to the vector store
    recall_vector_store.add_documents([document])
    return memory

def search_recall_memories(query: str, config: RunnableConfig) -> List[str]:
    """Search for relevant memories."""
    # Get the user ID and thread ID from the configuration
    user_id = get_user_id(config)
    thread_id = get_thread_id(config)

    # Define a filter to get only memories for this user and thread
    def _filter_function(doc: Document) -> bool:
        doc_user_id = doc.metadata.get("user_id")
        doc_thread_id = doc.metadata.get("thread_id", "default")
        
        # Match by user_id and optionally by thread_id if specified
        if doc_user_id == user_id:
            # If no thread_id is specified in the configuration, return all user memories
            # Otherwise, only return memories from the current thread
            if thread_id == "default" or doc_thread_id == thread_id:
                return True
        return False

    # Get the number of results to return from cached configuration
    k_results = VECTOR_K_RESULTS
    
    # Search for relevant memories using vector similarity
    documents = recall_vector_store.similarity_search(
        query.strip(), k=k_results, filter=_filter_function
    )
    
    # Return just the content of the found documents
    return [document.page_content for document in documents]

def save_recall_memory_knowledge_triple(memories: List[KnowledgeTriple], config: RunnableConfig) -> str:
    """Save memory to vectorstore for later semantic retrieval."""
    # Get the user ID and thread ID from the configuration
    user_id = get_user_id(config)
    thread_id = get_thread_id(config)
    
    # Process each memory in the list
    for memory in memories:
        # Create a serialized representation of the knowledge triple
        serialized = " ".join(memory.values())
        
        # Create a document with the serialized content and metadata
        document = Document(
            page_content=serialized,
            id=str(uuid.uuid4()),
            metadata={
                "user_id": user_id,
                "thread_id": thread_id,
                "timestamp": str(uuid.uuid1()),
                **memory,
            },
        )
        
        # Add the document to the vector store
        recall_vector_store.add_documents([document])
    
    return memories