"""
Main orchestrator for generating RAG knowledge from Dart codebases.

Usage:
  # Generate from current project (auto-detect everything)
  python3 main.py

  # Specify source directory
  python3 main.py --source /path/to/dart/lib

  # Specify version and collection name
  python3 main.py --version v2.2.0 --collection mekari_pixel

  # Compare two versions (requires git repo)
  python3 main.py --compare --from-version v1.30.0 --to-version v2.2.0

  # Full example with all options
  python3 main.py --source /path/to/lib --version v2.2.0 \
    --collection my_lib --dataset ./dataset --chroma ./chroma_db
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time
from tqdm import tqdm

from scripts import (
    DartDocGenerator,
    DocumentCreation,
    GitHistory,
    RepoManager,
    VectorEmbedding,
    VersionComparison,
)

SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_DATASET = os.path.join(SKILL_DIR, "dataset")
DEFAULT_CHROMA = os.path.join(SKILL_DIR, "chroma_db")

# Ensure ~/.pub-cache/bin is in PATH for dartdoc_json
_pub_cache_bin = os.path.join(
    os.path.expanduser("~"), ".pub-cache", "bin",
)
if _pub_cache_bin not in os.environ.get("PATH", ""):
    os.environ["PATH"] = (
        os.environ.get("PATH", "") + os.pathsep + _pub_cache_bin
    )


def detect_defaults():
    """Auto-detect source_dir, version, and repo name from git."""
    defaults = {}
    try:
        toplevel = subprocess.check_output(
            ["git", "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
        defaults["source_dir"] = os.path.join(toplevel, "lib")
        defaults["repo_name"] = os.path.basename(toplevel)
        defaults["repo_dir"] = toplevel
    except (subprocess.CalledProcessError, FileNotFoundError):
        defaults["source_dir"] = None
        defaults["repo_name"] = "unknown"
        defaults["repo_dir"] = None

    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            text=True,
        ).strip()
        defaults["version"] = branch
    except (subprocess.CalledProcessError, FileNotFoundError):
        defaults["version"] = None

    return defaults


def get_env_with_pub_cache():
    """Return env dict with ~/.pub-cache/bin in PATH."""
    env = os.environ.copy()
    pub_cache_bin = os.path.join(
        os.path.expanduser("~"), ".pub-cache", "bin",
    )
    env["PATH"] = env.get("PATH", "") + os.pathsep + pub_cache_bin
    return env


def normalize_collection_part(value: str) -> str:
    """Normalize a collection-name segment for ChromaDB use."""
    normalized = re.sub(r"[^0-9A-Za-z]+", "_", value).strip("_")
    normalized = re.sub(r"_+", "_", normalized)
    return (normalized or "unknown").lower()


def build_collection_name(
    base_name: str,
    version: str | None = None,
) -> str:
    """Build a reproducible collection name.

    Examples:
        ``mekari_pixel`` + ``v2.22.0`` ->
        ``mekari_pixel_v2_22_0``
    """
    normalized_base = normalize_collection_part(base_name)
    if not version:
        return normalized_base

    normalized_version = normalize_collection_part(version)
    suffix = f"_{normalized_version}"
    if normalized_base.endswith(suffix):
        return normalized_base
    return f"{normalized_base}{suffix}"


def check_dartdoc_json():
    """Verify dartdoc_json is installed."""
    try:
        result = subprocess.run(
            ["which", "dartdoc_json"],
            capture_output=True,
            text=True,
            env=get_env_with_pub_cache(),
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False


def step_generate_json(source_dir, dataset_dir, version, workers=0):
    """Step 1: Generate dartdoc JSON from Dart source files."""
    print(f"\n{'='*60}")
    print("STEP 1: Generate dartdoc JSON")
    print(f"{'='*60}")
    print(f"  Source:  {source_dir}")
    print(f"  Output:  {dataset_dir}")
    print(f"  Version: {version or '(none)'}")
    _w = workers if workers > 0 else min(8, os.cpu_count() or 4)
    print(f"  Workers: {_w} (parallel)")

    output_dir = DartDocGenerator.generate_json(
        source_dir=source_dir,
        output_dir=dataset_dir,
        version=version,
        workers=workers,
    )

    json_count = len([
        f for f in os.listdir(output_dir) if f.endswith(".json")
    ])
    print(f"\n  Generated {json_count} JSON documentation files.")
    return output_dir


def step_extract_git_history(
    source_dir, repo_dir, jira_url, depth,
    ticket_pattern=r"[A-Z]+-\d+",
    pr_url="",
    pr_pattern=r"pull request #(\d+)",
):
    """Step 1.5: Extract Jira tickets and PR links from git
    history."""
    print(f"\n{'='*60}")
    print("STEP 1.5: Extract Jira Tickets & PRs from Git History")
    print(f"{'='*60}")
    print(f"  Repo:       {repo_dir}")
    print(f"  Jira URL:   {jira_url}")
    print(f"  PR URL:     {pr_url or '(no hyperlinks)'}")
    print(f"  Depth:      {depth} commits per file")
    print(f"  Pattern:    {ticket_pattern}")
    print(f"  PR pattern: {pr_pattern}")

    git_history = GitHistory(
        repo_dir=repo_dir,
        jira_base_url=jira_url,
        depth=depth,
        ticket_pattern=ticket_pattern,
        pr_base_url=pr_url,
        pr_pattern=pr_pattern,
    )
    ticket_map = git_history.build_source_ticket_map(
        source_dir=source_dir,
    )
    pr_map = git_history.build_source_pr_map(
        source_dir=source_dir,
    )

    total_files = len(ticket_map)
    total_tickets = len(set(
        t for ts in ticket_map.values() for t in ts
    ))
    total_prs = len(set(
        p for ps in pr_map.values() for p in ps
    ))
    print(
        f"\n  Found {total_tickets} unique tickets "
        f"across {total_files} files."
    )
    print(
        f"  Found {total_prs} unique pull requests "
        f"across {len(pr_map)} files."
    )
    return git_history, ticket_map, pr_map


def step_embed(
    json_dir,
    chroma_path,
    collection_name,
    git_history=None,
    ticket_map=None,
    pr_map=None,
):
    """Step 2: Convert JSON to Markdown and embed into ChromaDB."""
    print(f"\n{'='*60}")
    print("STEP 2: Convert to Markdown & Embed into ChromaDB")
    print(f"{'='*60}")
    print(f"  JSON dir:   {json_dir}")
    print(f"  ChromaDB:   {chroma_path}")
    print(f"  Collection: {collection_name}")
    if git_history:
        print(f"  Jira:       enabled")
        print(f"  PRs:        {'enabled' if pr_map else 'disabled'}")

    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_or_create_collection(
        name=collection_name,
    )

    json_files = [
        f for f in os.listdir(json_dir) if f.endswith(".json")
    ]

    # Build reverse lookups: source path -> tickets/PRs
    source_ticket_lookup = {}
    if ticket_map:
        for src_path, tickets in ticket_map.items():
            source_ticket_lookup[src_path] = tickets

    source_pr_lookup = {}
    if pr_map:
        for src_path, prs in pr_map.items():
            source_pr_lookup[src_path] = prs

    print(f"\n  Processing {len(json_files)} JSON files...")

    total_docs = 0
    errors = 0
    start_time = time.time()

    with tqdm(total=len(json_files), desc="Embedding", unit="file") as pbar:
        for json_file in json_files:
            file_path = os.path.join(json_dir, json_file)
            file_name = os.path.splitext(json_file)[0]

            try:
                with open(file_path, "r") as f:
                    json_data = json.load(f)

                # Resolve Jira tickets and PRs from source
                jira_md = ""
                jira_list = None
                pr_md = ""
                pr_list = None
                if git_history and json_data:
                    source = None
                    for item in json_data:
                        if "source" in item:
                            source = item["source"]
                            break
                    if source:
                        if source in source_ticket_lookup:
                            jira_list = (
                                source_ticket_lookup[source]
                            )
                            jira_md = (
                                git_history
                                .format_tickets_markdown(
                                    jira_list,
                                )
                            )
                        if source in source_pr_lookup:
                            pr_list = (
                                source_pr_lookup[source]
                            )
                            pr_md = (
                                git_history
                                .format_prs_markdown(
                                    pr_list,
                                )
                            )

                documents = (
                    DocumentCreation
                    .create_markdown_document_from_dart_doc_json(
                        file_name=file_name,
                        json_data=json_data,
                        jira_tickets_markdown=jira_md,
                        jira_tickets_list=jira_list,
                        pr_tickets_markdown=pr_md,
                        pr_list=pr_list,
                    )
                )

                for markdown, metadata in documents:
                    VectorEmbedding.embed_to_chroma_db_collection(
                        collection=collection,
                        document=markdown,
                        metadata=metadata,
                    )
                    total_docs += 1
            except Exception as e:
                errors += 1
                if errors <= 5:
                    pbar.write(f"    Error: {json_file}: {e}")

            # Update progress bar with stats
            elapsed = time.time() - start_time
            rate = total_docs / elapsed if elapsed > 0 else 0
            pbar.set_postfix({
                "docs": total_docs,
                "errs": errors,
                "docs/s": f"{rate:.1f}"
            })
            pbar.update(1)

    elapsed = time.time() - start_time
    rate = len(json_files) / elapsed if elapsed > 0 else 0

    print(f"\n  Done. {total_docs} documents embedded, {errors} errors.")
    print(f"  Collection count: {collection.count()}")
    print(f"  Processing rate: {rate:.2f} files/second")
    print(f"  Total time: {elapsed:.1f} seconds")
    return collection


def step_verify(chroma_path, collection_name):
    """Step 3: Verify embeddings with sample queries."""
    print(f"\n{'='*60}")
    print("STEP 3: Verify Embeddings")
    print(f"{'='*60}")

    import chromadb

    client = chromadb.PersistentClient(path=chroma_path)
    collection = client.get_collection(collection_name)

    print(f"  Collection: {collection.name}")
    print(f"  Total embeddings: {collection.count()}")

    sample_queries = ["widget", "bloc state", "repository"]
    for query in sample_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2,
        )
        print(f"\n  Query: '{query}'")
        for doc, meta in zip(
            results["documents"][0],
            results["metadatas"][0],
        ):
            name = meta.get("name", "N/A")
            kind = meta.get("kind", "N/A")
            print(f"    -> {name} ({kind})")

    print(f"\n  Verification complete.")


def step_compare(dataset_dir, from_version, to_version):
    """Compare two versions and print the diff."""
    print(f"\n{'='*60}")
    print("VERSION COMPARISON")
    print(f"{'='*60}")
    print(f"  From: {from_version}")
    print(f"  To:   {to_version}")

    result = VersionComparison.compare_versions(
        dataset_dir=dataset_dir,
        from_version=from_version,
        to_version=to_version,
    )

    summary = result["summary"]
    print(f"\n  Added:    {summary['added']} components")
    print(f"  Removed:  {summary['removed']} components")
    print(f"  Modified: {summary['modified']} components")

    if result["added_components"]:
        print("\n  + Added:")
        for c in result["added_components"]:
            print(f"    + {c['name']} ({c['kind']})")

    if result["removed_components"]:
        print("\n  - Removed:")
        for c in result["removed_components"]:
            print(f"    - {c['name']} ({c['kind']})")

    if result["modified_components"]:
        print("\n  ~ Modified:")
        for c in result["modified_components"]:
            changes = list(c["changes"].keys())
            print(f"    ~ {c['name']} ({c['kind']}): {', '.join(changes)}")

    return result


def main():
    defaults = detect_defaults()

    parser = argparse.ArgumentParser(
        description="Generate RAG knowledge from Dart codebase dartdoc.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--source",
        default=defaults.get("source_dir"),
        help="Path to Dart source directory (default: current project lib/)",
    )
    parser.add_argument(
        "--version",
        default=defaults.get("version"),
        help="Version tag or branch name (default: current git branch)",
    )
    parser.add_argument(
        "--collection",
        default=None,
        help="ChromaDB collection name (default: {repo_name})",
    )
    parser.add_argument(
        "--dataset",
        default=DEFAULT_DATASET,
        help=f"Dataset output directory (default: {DEFAULT_DATASET})",
    )
    parser.add_argument(
        "--chroma",
        default=DEFAULT_CHROMA,
        help=f"ChromaDB persistence path (default: {DEFAULT_CHROMA})",
    )
    parser.add_argument(
        "--skip-json",
        action="store_true",
        help="Skip JSON generation (reuse existing dataset)",
    )
    parser.add_argument(
        "--skip-verify",
        action="store_true",
        help="Skip verification step",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=0,
        help=(
            "Parallel workers for JSON generation "
            "(default: 0 = auto, min(8, cpu_count))"
        ),
    )
    parser.add_argument(
        "--git-depth",
        type=int,
        default=20,
        help="Max git commits per file for ticket extraction (default: 20)",
    )
    parser.add_argument(
        "--jira-url",
        default="https://jurnal.atlassian.net/browse/",
        help="Jira base URL for ticket links",
    )
    parser.add_argument(
        "--no-jira",
        action="store_true",
        help="Skip Jira ticket extraction from git history",
    )
    parser.add_argument(
        "--ticket-pattern",
        default=r"[A-Z]+-\d+",
        help="Regex pattern for ticket IDs (default: [A-Z]+-\\d+)",
    )
    parser.add_argument(
        "--pr-url",
        default="",
        help=(
            "Pull request base URL, e.g. "
            "https://bitbucket.org/org/repo/pull-requests/"
        ),
    )
    parser.add_argument(
        "--no-pr",
        action="store_true",
        help="Skip pull request extraction from git history",
    )
    parser.add_argument(
        "--pr-pattern",
        default=r"pull request #(\d+)",
        help=(
            "Regex (with one capture group for the PR ID) "
            "to extract PRs from commit messages "
            "(default: pull request #(\\d+))"
        ),
    )

    # Version comparison mode
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Compare two versions instead of generating",
    )
    parser.add_argument(
        "--from-version",
        help="Starting version for comparison",
    )
    parser.add_argument(
        "--to-version",
        help="Target version for comparison",
    )
    parser.add_argument(
        "--repo-dir",
        default=defaults.get("repo_dir"),
        help="Git repo directory for version checkout",
    )

    args = parser.parse_args()

    # Resolve base collection name and versioned target collection name.
    if not args.collection:
        repo_name = defaults.get("repo_name", "unknown")
        args.collection = repo_name
    args.collection = build_collection_name(args.collection)

    print(f"RAG Knowledge Generator")
    print(f"{'='*60}")

    # --- Version comparison mode ---
    if args.compare:
        if not args.from_version or not args.to_version:
            parser.error("--compare requires --from-version and --to-version")
        if not args.repo_dir:
            parser.error("--compare requires --repo-dir or a git repository")

        repo = RepoManager(args.repo_dir)

        # Generate for from_version
        print(f"\nGenerating docs for {args.from_version}...")
        repo.checkout(args.from_version, force=True)
        step_generate_json(
            args.source, args.dataset, args.from_version,
            workers=args.workers,
        )
        step_embed(
            os.path.join(args.dataset, args.from_version),
            args.chroma,
            build_collection_name(args.collection, args.from_version),
        )

        # Generate for to_version
        print(f"\nGenerating docs for {args.to_version}...")
        repo.checkout(args.to_version, force=True)
        step_generate_json(
            args.source, args.dataset, args.to_version,
            workers=args.workers,
        )
        step_embed(
            os.path.join(args.dataset, args.to_version),
            args.chroma,
            build_collection_name(args.collection, args.to_version),
        )

        # Compare
        step_compare(args.dataset, args.from_version, args.to_version)
        return

    # --- Standard generation mode ---
    # Preflight checks
    if not args.source or not os.path.isdir(args.source):
        parser.error(
            f"Source directory not found: {args.source}\n"
            "Use --source to specify the Dart lib/ path."
        )

    if not check_dartdoc_json():
        print(
            "ERROR: dartdoc_json not found. Install with:\n"
            "  dart pub global activate dartdoc_json\n"
            "  export PATH=\"$PATH:$HOME/.pub-cache/bin\""
        )
        sys.exit(1)

    print(f"  Source:     {args.source}")
    print(f"  Version:    {args.version or '(none)'}")
    target_collection = build_collection_name(
        args.collection,
        args.version,
    )
    print(f"  Collection: {target_collection}")
    print(f"  Dataset:    {args.dataset}")
    print(f"  ChromaDB:   {args.chroma}")
    _w = args.workers if args.workers > 0 else min(
        8, os.cpu_count() or 4
    )
    print(f"  Workers:    {_w} (parallel JSON generation)")
    print(f"  Jira:       {'disabled' if args.no_jira else args.jira_url}")
    print(f"  PRs:        {'disabled' if args.no_pr else (args.pr_url or '(no hyperlinks)')}")
    print(f"  Git depth:  {args.git_depth}")
    if not args.no_jira:
        print(f"  Pattern:    {args.ticket_pattern}")
    if not args.no_pr:
        print(f"  PR pattern: {args.pr_pattern}")

    # Step 1: Generate JSON
    if args.skip_json:
        json_dir = args.dataset
        if args.version:
            json_dir = os.path.join(args.dataset, args.version)
        print(f"\n  Skipping JSON generation, using: {json_dir}")
    else:
        json_dir = step_generate_json(
            args.source, args.dataset, args.version,
            workers=args.workers,
        )

    # Step 1.5: Extract Jira tickets and PRs from git history
    git_history = None
    ticket_map = None
    pr_map = None
    if not args.no_jira or not args.no_pr:
        repo_dir = args.repo_dir
        if repo_dir:
            git_history, ticket_map, pr_map = (
                step_extract_git_history(
                    source_dir=args.source,
                    repo_dir=repo_dir,
                    jira_url=args.jira_url,
                    depth=args.git_depth,
                    ticket_pattern=args.ticket_pattern,
                    pr_url=args.pr_url,
                    pr_pattern=args.pr_pattern,
                )
            )
            if args.no_jira:
                ticket_map = None
            if args.no_pr:
                pr_map = None

    # Step 2: Embed
    step_embed(
        json_dir,
        args.chroma,
        target_collection,
        git_history=git_history,
        ticket_map=ticket_map,
        pr_map=pr_map,
    )

    # Step 3: Verify
    if not args.skip_verify:
        step_verify(args.chroma, target_collection)

    print(f"\n{'='*60}")
    print("COMPLETE")
    print(f"{'='*60}")
    print(f"  Collection '{target_collection}' ready at {args.chroma}")
    print(f"  Query with: ./venv/bin/python3 query.py")


if __name__ == "__main__":
    main()
