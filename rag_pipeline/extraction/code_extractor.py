"""Extract code files from repository for RAG indexing."""

import os
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CodeExtractor:
    """Extract code files from repository."""
    
    SUPPORTED_EXTENSIONS = {
        ".py", ".js", ".ts", ".tsx", ".jsx",
        ".java", ".cpp", ".c", ".go", ".rs",
        ".md", ".txt", ".yaml", ".yml", ".json",
    }
    
    IGNORE_DIRS = {".git", ".venv", "node_modules", "__pycache__", ".pytest_cache", "dist", "build"}
    
    def __init__(self, repo_path: str):
        """
        Initialize code extractor.
        
        Args:
            repo_path: Path to repository root directory
        """
        self.repo_path = Path(repo_path)
        if not self.repo_path.exists():
            raise ValueError(f"Repository path not found: {repo_path}")
    
    def extract_files(self) -> List[Dict[str, Any]]:
        """
        Extract all code files from repository.
        
        Returns:
            List of documents with structure:
            {
                "file_path": str,
                "content": str,
                "language": str,
                "size_bytes": int,
                "module": str,
            }
        """
        documents = []
        
        for file_path in self.repo_path.rglob("*"):
            if not file_path.is_file():
                continue
            
            # Skip ignored directories
            if any(ignored in file_path.parts for ignored in self.IGNORE_DIRS):
                continue
            
            # Check file extension
            if file_path.suffix not in self.SUPPORTED_EXTENSIONS:
                continue
            
            try:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
                rel_path = file_path.relative_to(self.repo_path)
                
                document = {
                    "file_path": str(rel_path),
                    "content": content,
                    "language": self._detect_language(file_path.suffix),
                    "size_bytes": file_path.stat().st_size,
                    "module": self._extract_module(rel_path),
                }
                
                documents.append(document)
                logger.debug(f"Extracted: {rel_path}")
            
            except Exception as e:
                logger.warning(f"Failed to extract {file_path}: {e}")
                continue
        
        logger.info(f"Extracted {len(documents)} code files")
        return documents
    
    def _detect_language(self, extension: str) -> str:
        """Detect programming language from file extension."""
        language_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".jsx": "javascript",
            ".java": "java",
            ".cpp": "cpp",
            ".c": "c",
            ".go": "go",
            ".rs": "rust",
            ".md": "markdown",
            ".txt": "text",
            ".yaml": "yaml",
            ".yml": "yaml",
            ".json": "json",
        }
        return language_map.get(extension, "unknown")
    
    def _extract_module(self, file_path: Path) -> str:
        """Extract module name from file path."""
        parts = file_path.parts
        if len(parts) > 1:
            return parts[0]
        return "root"
