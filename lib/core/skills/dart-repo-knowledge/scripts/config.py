"""Configuration management for dart-repo-knowledge.

Supports loading configuration from:
1. CLI arguments (highest priority)
2. .repoknowledge.toml file
3. Default values

Example .repoknowledge.toml:
    [source]
    directory = "lib"

    [jira]
    base_url = "https://mekari.atlassian.net/browse/"
    ticket_pattern = "[A-Z]+-\\d+"
    git_depth = 20

    [pr]
    base_url = "https://bitbucket.org/org/repo/pull-requests/"
    pr_pattern = "pull request #(\\d+)"

    [chroma]
    path = "chroma_db"
    collection = "auto"

    [processing]
    workers = 0
    skip_jira = false
    skip_pr = false
"""
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any

# Try to import tomli, fall back to tomllib (Python 3.11+)
try:
    import tomli
    HAS_TOMLI = True
except ImportError:
    HAS_TOMLI = False
    try:
        import tomllib
        HAS_TOMLLIB = True
    except ImportError:
        HAS_TOMLLIB = False


@dataclass
class JiraConfig:
    """Jira ticket extraction configuration."""
    base_url: str = "https://mekari.atlassian.net/browse/"
    ticket_pattern: str = r"[A-Z]+-\d+"
    git_depth: int = 20
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JiraConfig":
        """Create from dictionary, ignoring extra keys."""
        return cls(
            base_url=data.get("base_url", cls.base_url),
            ticket_pattern=data.get("ticket_pattern", cls.ticket_pattern),
            git_depth=data.get("git_depth", cls.git_depth),
            enabled=data.get("enabled", True),
        )


@dataclass
class PRConfig:
    """Pull request link extraction configuration."""
    base_url: str = ""
    pr_pattern: str = r"pull request #(\d+)"
    enabled: bool = True

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PRConfig":
        """Create from dictionary, ignoring extra keys."""
        return cls(
            base_url=data.get("base_url", cls.base_url),
            pr_pattern=data.get(
                "pr_pattern", cls.pr_pattern,
            ),
            enabled=data.get("enabled", True),
        )


@dataclass
class ChromaConfig:
    """ChromaDB configuration."""
    path: str = "chroma_db"
    collection: Optional[str] = None  # None = auto-detect from repo name

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ChromaConfig":
        """Create from dictionary, ignoring extra keys."""
        return cls(
            path=data.get("path", cls.path),
            collection=data.get("collection", cls.collection),
        )


@dataclass
class ProcessingConfig:
    """Processing configuration."""
    workers: int = 0  # 0 = auto-detect
    skip_jira: bool = False
    skip_pr: bool = False
    skip_json: bool = False
    skip_verify: bool = False

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingConfig":
        """Create from dictionary, ignoring extra keys."""
        return cls(
            workers=data.get("workers", cls.workers),
            skip_jira=data.get("skip_jira", cls.skip_jira),
            skip_pr=data.get("skip_pr", cls.skip_pr),
            skip_json=data.get("skip_json", cls.skip_json),
            skip_verify=data.get(
                "skip_verify", cls.skip_verify,
            ),
        )


@dataclass
class Config:
    """Main configuration container."""
    source_dir: Optional[str] = None
    version: Optional[str] = None
    dataset_dir: str = "dataset"
    jira: JiraConfig = field(default_factory=JiraConfig)
    pr: PRConfig = field(default_factory=PRConfig)
    chroma: ChromaConfig = field(default_factory=ChromaConfig)
    processing: ProcessingConfig = field(
        default_factory=ProcessingConfig,
    )

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create from dictionary."""
        jira_data = data.get("jira", {})
        pr_data = data.get("pr", {})
        chroma_data = data.get("chroma", {})
        processing_data = data.get("processing", {})
        source_data = data.get("source", {})

        return cls(
            source_dir=source_data.get("directory"),
            dataset_dir=data.get("dataset", "dataset"),
            jira=JiraConfig.from_dict(jira_data),
            pr=PRConfig.from_dict(pr_data),
            chroma=ChromaConfig.from_dict(chroma_data),
            processing=ProcessingConfig.from_dict(
                processing_data,
            ),
        )


def load_config(config_path: Optional[str] = None) -> Config:
    """Load configuration from .repoknowledge.toml file.

    Args:
        config_path: Path to config file. If None, searches upward from cwd.

    Returns:
        Config object with values loaded from file or defaults.
    """
    # Find config file
    if config_path is None:
        cwd = Path.cwd()
        for parent in [cwd, *cwd.parents]:
            candidate = parent / ".repoknowledge.toml"
            if candidate.exists():
                config_path = str(candidate)
                break

    if config_path is None or not os.path.exists(config_path):
        return Config()

    # Load TOML
    with open(config_path, "rb") as f:
        if HAS_TOMLI:
            data = tomli.load(f)
        elif HAS_TOMLLIB:
            data = tomllib.load(f)
        else:
            # No TOML library available, return defaults
            return Config()

    return Config.from_dict(data)
