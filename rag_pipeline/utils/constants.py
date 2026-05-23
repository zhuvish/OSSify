"""Shared constants and system prompts for RAG pipeline."""

# Document types
DOCUMENT_TYPES = {
    "COMMIT": "commit",
    "PR": "pull_request",
    "ISSUE": "issue",
    "CODE": "code",
    "DISCUSSION": "discussion",
}

# Metadata keys for ChromaDB
METADATA_KEYS = {
    "AUTHOR": "author",
    "TIMESTAMP": "timestamp",
    "FILE_PATH": "file_path",
    "MODULE": "module",
    "REPO": "repository",
    "TYPE": "document_type",
    "LANGUAGE": "language",
    "PR_NUMBER": "pr_number",
    "ISSUE_NUMBER": "issue_number",
    "COMMIT_HASH": "commit_hash",
}

# System prompts
SYSTEM_PROMPTS = {
    "REPOSITORY_EXPERT": """You are an expert assistant about a GitHub repository. 
You have access to repository data including commits, PRs, issues, and code files.
When answering questions, cite specific commits, file names, or PRs with their metadata.
Always provide sources from the repository data provided.
Be concise and factual. If you don't know, say so.""",
    
    "CODE_ANALYST": """You are a code analyzer for a GitHub repository.
Analyze code snippets, commits, and changes provided.
Explain the intent, logic, and impact of code changes.
Reference specific files and line numbers when applicable.""",
}

# Chunking configuration
CHUNK_SIZE = 512  # tokens
CHUNK_OVERLAP = 50  # tokens
MIN_CHUNK_SIZE = 100  # tokens

# Retrieval configuration
TOP_K_RESULTS = 5
SIMILARITY_THRESHOLD = 0.3
MAX_CONTEXT_TOKENS = 6000  # Keep buffer below Groq 8K limit

# Embedding model
EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDINGS_DIMENSION = 384
