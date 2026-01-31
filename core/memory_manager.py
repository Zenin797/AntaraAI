"""
MongoDB-backed Memory Manager for LTM application.

This module creates a real connection to a MongoDB instance using `pymongo` and
initializes `langmem` memory tools with a Mongo-backed vector store.
This implementation will fail fast if MongoDB is not reachable so the application
operator is forced to configure a persistent database for production use.
"""

from __future__ import annotations

import logging
import os
from typing import List
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# External deps
from pymongo import MongoClient
from langchain_openai import OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings

# Langgraph / langmem store
from langgraph.store.mongodb import MongoStore
from langmem import create_manage_memory_tool, create_search_memory_tool

# Load environment
load_dotenv()

logger = logging.getLogger(__name__)

# --- MONGODB CONNECTION (FAIL FAST) ---
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
DATABASE_NAME = os.getenv("MONGODB_DATABASE", "ltm_database")
COLLECTION_NAME = os.getenv("MONGODB_COLLECTION", "memory_store")

# Create client and force a connection to ensure persistence is configured
try:
    mongo_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    # Force server selection to validate connection; will raise if unreachable
    mongo_client.server_info()
except Exception as e:
    logger.error("Failed to connect to MongoDB at %s: %s", MONGO_URI, e)
    raise RuntimeError(f"MongoDB connection failed: {e}") from e

# Expose db/collection for other modules
db = mongo_client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# --- EMBEDDINGS CONFIGURATION ---
# Attempt to use available, preferred embeddings in order
try:
    embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
    logger.info("Using OpenAI embeddings")
except Exception:
    try:
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        logger.info("Using Google Generative embeddings")
    except Exception:
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        logger.info("Falling back to HuggingFace embeddings")

# --- MONGODB VECTOR STORE ---
memory_store = MongoStore(
    client=mongo_client,
    database_name=DATABASE_NAME,
    collection_name=COLLECTION_NAME,
    index={
        "dims": getattr(getattr(embeddings, "model_kwargs", {}), "get", lambda *_: 384)("dimensions", 384) if hasattr(embeddings, "model_kwargs") else 384,
        "embed": embeddings,
        "fields": ["content"],
    },
)

# ==========================================================================
# Memory Schemas
# ==========================================================================
class Episode(BaseModel):
    """Episodic memory captures specific experiences and learning moments."""
    observation: str = Field(..., description="The context and setup - what happened")
    thoughts: str = Field(..., description="Internal reasoning process")
    action: str = Field(..., description="What was done")
    result: str = Field(..., description="Outcome and retrospective analysis")
    significance_score: int = Field(..., description="A 1-10 rating of significance")

class Triple(BaseModel):
    """Semantic memory stores factual information as triples."""
    subject: str = Field(..., description="The entity being described")
    predicate: str = Field(..., description="The relationship or property")
    object: str = Field(..., description="The target of the relationship")
    context: str | None = Field(None, description="Optional additional context")

class Procedural(BaseModel):
    """Procedural memory stores instructions, rules, and procedures."""
    task: str = Field(..., description="The task or process")
    steps: List[str] = Field(..., description="Step-by-step instructions")
    conditions: str | None = Field(None, description="When to apply this procedure")
    outcome: str | None = Field(None, description="Expected result")

class Associative(BaseModel):
    """Associative memory stores connections between concepts and ideas."""
    concept_a: str = Field(..., description="The first concept in the association")
    concept_b: str = Field(..., description="The second concept in the association")
    strength: float = Field(..., description="Strength of the association (0.0-1.0)")
    context: str | None = Field(None, description="Context in which the association was formed")

# ==========================================================================
# Memory Tools (LangMem)
# ==========================================================================
manage_episodic_memory_tool = create_manage_memory_tool(
    namespace=("memories", "{user_id}", "episodes"),
    store=memory_store
)
search_episodic_memory_tool = create_search_memory_tool(
    namespace=("memories", "{user_id}", "episodes"),
    store=memory_store
)

manage_semantic_memory_tool = create_manage_memory_tool(
    namespace=("memories", "{user_id}", "triples"),
    store=memory_store
)
search_semantic_memory_tool = create_search_memory_tool(
    namespace=("memories", "{user_id}", "triples"),
    store=memory_store
)

manage_procedural_memory_tool = create_manage_memory_tool(
    namespace=("memories", "{user_id}", "procedures"),
    store=memory_store
)
search_procedural_memory_tool = create_search_memory_tool(
    namespace=("memories", "{user_id}", "procedures"),
    store=memory_store
)

manage_associative_memory_tool = create_manage_memory_tool(
    namespace=("memories", "{user_id}", "associations"),
    store=memory_store
)
search_associative_memory_tool = create_search_memory_tool(
    namespace=("memories", "{user_id}", "associations"),
    store=memory_store
)

manage_general_memory_tool = create_manage_memory_tool(
    namespace=("memories", "{user_id}"),
    store=memory_store
)
search_general_memory_tool = create_search_memory_tool(
    namespace=("memories", "{user_id}"),
    store=memory_store
)

logger.info("✅ MongoDB-backed memory manager initialized and memory tools created")

