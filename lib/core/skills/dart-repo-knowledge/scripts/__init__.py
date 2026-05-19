"""Dart-Repo-Knowledge core modules.

This package provides functionality for:
- Generating dartdoc JSON from Dart source files
- Converting JSON to structured Markdown documents
- Extracting Jira tickets from git history
- Embedding documents into ChromaDB vector store
- Comparing API versions
- Configuration management via .repoknowledge.toml

Example:
    from src import DartDocGenerator, VectorEmbedding

    # Generate JSON documentation
    json_dir = DartDocGenerator.generate_json(
        source_dir="lib",
        output_dir="dataset"
    )
"""

from .config import Config, JiraConfig, PRConfig, ChromaConfig, ProcessingConfig, load_config
from .dart_doc_generator import DartDocGenerator
from .document_creation import DocumentCreation
from .git_history import GitHistory
from .repo_manager import RepoManager
from .vector_embedding import VectorEmbedding
from .version_comparison import VersionComparison

__all__ = [
    "Config",
    "JiraConfig",
    "PRConfig",
    "ChromaConfig",
    "ProcessingConfig",
    "load_config",
    "DartDocGenerator",
    "DocumentCreation",
    "GitHistory",
    "RepoManager",
    "VectorEmbedding",
    "VersionComparison",
]