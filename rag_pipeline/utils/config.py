"""Configuration management for RAG pipeline."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""
    
    # GitHub
    GITHUB_TOKEN: str = os.getenv("GITHUB_TOKEN", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://localhost/ossify")
    
    # Groq API
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    # ChromaDB
    CHROMADB_PATH: str = os.getenv("CHROMADB_PATH", "./vector_store")
    CHROMADB_COLLECTION: str = "ossify_documents"
    
    # Embeddings
    EMBEDDINGS_MODEL: str = os.getenv("EMBEDDINGS_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
    
    # Repository
    REPO_OWNER: str = os.getenv("REPO_OWNER", "")
    REPO_NAME: str = os.getenv("REPO_NAME", "")
    
    # Feature flags
    USE_PERSISTENT_CHROMADB: bool = os.getenv("USE_PERSISTENT_CHROMADB", "false").lower() == "true"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"


class DevelopmentConfig(Config):
    """Development configuration (in-memory ChromaDB)."""
    USE_PERSISTENT_CHROMADB = False
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration (persistent ChromaDB)."""
    USE_PERSISTENT_CHROMADB = True
    DEBUG = False


def get_config() -> Config:
    """Get appropriate configuration based on environment."""
    env = os.getenv("ENVIRONMENT", "development")
    if env == "production":
        return ProductionConfig()
    return DevelopmentConfig()
