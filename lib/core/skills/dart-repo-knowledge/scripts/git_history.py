import os
import re
import subprocess
from typing import Dict, List, Optional


# Default Jira base URL
DEFAULT_JIRA_BASE_URL = "https://jurnal.atlassian.net/browse/"

# Default regex for Jira ticket IDs (e.g., MC-1234)
DEFAULT_TICKET_PATTERN = r"[A-Z]+-\d+"

# Default PR base URL (empty = no hyperlink, just #ID)
DEFAULT_PR_BASE_URL = ""

# Default regex for PR IDs extracted from Bitbucket merge
# commits, e.g. "Merged in feature/x (pull request #123)"
DEFAULT_PR_PATTERN = r"pull request #(\d+)"


class GitHistory:
    """Extracts Jira ticket IDs and pull request links from
    git commit history for source files.

    Example:
        ```python
        history = GitHistory(
            repo_dir="/path/to/repo",
            jira_base_url=(
                "https://jurnal.atlassian.net/browse/"
            ),
            pr_base_url=(
                "https://bitbucket.org/org/repo"
                "/pull-requests/"
            ),
            depth=20,
        )
        tickets = history.get_tickets_for_file(
            "lib/features/savings/savings_bloc.dart"
        )
        # Returns: ["MC-1234", "BAAS-405"]

        prs = history.get_prs_for_file(
            "lib/features/savings/savings_bloc.dart"
        )
        # Returns: ["123", "456"]
        ```
    """

    def __init__(
        self,
        repo_dir: str,
        jira_base_url: str = DEFAULT_JIRA_BASE_URL,
        depth: int = 20,
        ticket_pattern: str = DEFAULT_TICKET_PATTERN,
        pr_base_url: str = DEFAULT_PR_BASE_URL,
        pr_pattern: str = DEFAULT_PR_PATTERN,
    ) -> None:
        self.repo_dir = repo_dir
        self.jira_base_url = jira_base_url.rstrip("/") + "/"
        self.depth = depth
        self.ticket_pattern = re.compile(ticket_pattern)
        self.pr_base_url = (
            pr_base_url.rstrip("/") + "/"
            if pr_base_url else ""
        )
        self._pr_pattern = re.compile(
            pr_pattern, re.IGNORECASE,
        )

        # Cache: source_path -> list of ticket IDs
        self._cache: Dict[str, List[str]] = {}

        # Cache: source_path -> list of PR IDs (as strings)
        self._pr_cache: Dict[str, List[str]] = {}

        # Cache: source_path -> raw git log output
        self._log_cache: Dict[str, str] = {}

    def _get_log_for_file(self, rel_path: str) -> str:
        """Fetch and cache raw git log output for a file.

        Args:
            rel_path: Repo-relative path to the source file.

        Returns:
            Raw git log stdout string, or empty string on
            error.
        """
        if rel_path in self._log_cache:
            return self._log_cache[rel_path]

        try:
            result = subprocess.run(
                [
                    "git", "log",
                    f"--max-count={self.depth}",
                    "--oneline",
                    "--", rel_path,
                ],
                capture_output=True,
                text=True,
                cwd=self.repo_dir,
            )
            output = (
                result.stdout if result.returncode == 0
                else ""
            )
            self._log_cache[rel_path] = output
            return output
        except (FileNotFoundError, OSError):
            self._log_cache[rel_path] = ""
            return ""

    def get_tickets_for_file(
        self,
        file_path: str,
    ) -> List[str]:
        """Extract unique Jira ticket IDs from git log
        for a specific file.

        Args:
            file_path: Absolute or repo-relative path
                to the source file.

        Returns:
            Sorted list of unique ticket IDs.
        """
        # Normalize to repo-relative path
        rel_path = file_path
        if os.path.isabs(file_path):
            rel_path = os.path.relpath(
                file_path, self.repo_dir,
            )

        if rel_path in self._cache:
            return self._cache[rel_path]

        log = self._get_log_for_file(rel_path)
        tickets = set(self.ticket_pattern.findall(log))
        sorted_tickets = sorted(tickets)
        self._cache[rel_path] = sorted_tickets
        return sorted_tickets

    def get_prs_for_file(
        self,
        file_path: str,
    ) -> List[str]:
        """Extract unique pull request IDs from git log
        for a specific file.

        The default pattern matches Bitbucket merge commits
        of the form:
        ``Merged in feature/branch (pull request #123)``

        Args:
            file_path: Absolute or repo-relative path
                to the source file.

        Returns:
            Sorted list of unique PR ID strings (numeric).
        """
        rel_path = file_path
        if os.path.isabs(file_path):
            rel_path = os.path.relpath(
                file_path, self.repo_dir,
            )

        if rel_path in self._pr_cache:
            return self._pr_cache[rel_path]

        log = self._get_log_for_file(rel_path)
        raw = self._pr_pattern.findall(log)
        # findall returns capture groups (the numeric IDs)
        prs = set(raw)
        sorted_prs = sorted(prs, key=lambda x: int(x))
        self._pr_cache[rel_path] = sorted_prs
        return sorted_prs

    def get_ticket_urls(
        self,
        tickets: List[str],
    ) -> List[str]:
        """Convert ticket IDs to full Jira URLs.

        Args:
            tickets: List of ticket IDs.

        Returns:
            List of full Jira browse URLs.
        """
        return [
            f"{self.jira_base_url}{ticket}"
            for ticket in tickets
        ]

    def format_tickets_markdown(
        self,
        tickets: List[str],
    ) -> str:
        """Format tickets as a Markdown section.

        Args:
            tickets: List of ticket IDs.

        Returns:
            Markdown string with linked tickets.
        """
        if not tickets:
            return ""

        lines = ["\n## Related Jira Tickets\n"]
        for ticket in tickets:
            url = f"{self.jira_base_url}{ticket}"
            lines.append(f"- [{ticket}]({url})")
        return "\n".join(lines)

    def build_source_ticket_map(
        self,
        source_dir: str,
    ) -> Dict[str, List[str]]:
        """Build a mapping of all Dart source files
        to their Jira tickets.

        Args:
            source_dir: Directory containing Dart files.

        Returns:
            Dict mapping source file paths to ticket
            ID lists.
        """
        ticket_map: Dict[str, List[str]] = {}
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".dart"):
                    file_path = os.path.join(root, file)
                    tickets = self.get_tickets_for_file(
                        file_path,
                    )
                    if tickets:
                        ticket_map[file_path] = tickets
        return ticket_map

    def get_pr_urls(
        self,
        pr_ids: List[str],
    ) -> List[str]:
        """Convert PR IDs to full pull request URLs.

        Args:
            pr_ids: List of PR ID strings (numeric).

        Returns:
            List of full PR URLs, or ``#ID`` fragments
            when no base URL is configured.
        """
        if not self.pr_base_url:
            return [f"#{pr_id}" for pr_id in pr_ids]
        return [
            f"{self.pr_base_url}{pr_id}"
            for pr_id in pr_ids
        ]

    def format_prs_markdown(
        self,
        pr_ids: List[str],
    ) -> str:
        """Format pull request IDs as a Markdown section.

        Args:
            pr_ids: List of PR ID strings (numeric).

        Returns:
            Markdown string with linked pull requests,
            or empty string when ``pr_ids`` is empty.
        """
        if not pr_ids:
            return ""

        lines = ["\n## Related Pull Requests\n"]
        for pr_id in pr_ids:
            if self.pr_base_url:
                url = f"{self.pr_base_url}{pr_id}"
                lines.append(f"- [#{pr_id}]({url})")
            else:
                lines.append(f"- #{pr_id}")
        return "\n".join(lines)

    def build_source_pr_map(
        self,
        source_dir: str,
    ) -> Dict[str, List[str]]:
        """Build a mapping of all Dart source files
        to their pull request IDs.

        Args:
            source_dir: Directory containing Dart files.

        Returns:
            Dict mapping source file paths to PR ID
            lists (numeric strings).
        """
        pr_map: Dict[str, List[str]] = {}
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".dart"):
                    file_path = os.path.join(root, file)
                    prs = self.get_prs_for_file(file_path)
                    if prs:
                        pr_map[file_path] = prs
        return pr_map
