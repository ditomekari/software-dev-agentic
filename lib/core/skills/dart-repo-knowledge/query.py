"""Query and collection management tool for ChromaDB knowledge bases.

One-shot and interactive query, plus collection inspection utilities
that replace the former MCP server tools.

CLI Usage:
  # List all collections
  python3 query.py --list-collections

  # Inspect a collection
  python3 query.py <collection> --info

  # Dump documents (paginated)
  python3 query.py <collection> --documents --limit 20 --offset 0

  # One-shot semantic query
  python3 query.py <collection> --query "MpTextStyles --n=5 --kind=class"

  # Interactive mode
  python3 query.py <collection>
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any

import chromadb


CHROMA_PATH = "chroma_db"
DEFAULT_RESULTS = 5


@dataclass(frozen=True)
class QueryInput:
    query_text: str
    n_results: int = DEFAULT_RESULTS
    where_filter: dict[str, str] | None = None


def parse_query_input(raw_query: str) -> QueryInput:
    """Parse inline query flags from freeform input."""
    parts = raw_query.split()
    n_results = DEFAULT_RESULTS
    where_filter = None
    query_words: list[str] = []

    for part in parts:
        if part.startswith("--n="):
            n_results = int(part[4:])
        elif part.startswith("--kind="):
            where_filter = {"kind": part[7:]}
        else:
            query_words.append(part)

    return QueryInput(
        query_text=" ".join(query_words),
        n_results=n_results,
        where_filter=where_filter,
    )


def get_client(chroma_path: str = CHROMA_PATH) -> chromadb.PersistentClient:
    """Return a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=chroma_path)


def get_collection(
    collection_name: str,
    chroma_path: str = CHROMA_PATH,
):
    client = get_client(chroma_path)
    return client.get_collection(collection_name)


# ---------------------------------------------------------------------------
# Collection management helpers (replace former MCP server tools)
# ---------------------------------------------------------------------------

def list_collections(client) -> list[dict[str, Any]]:
    """Return [{name, count}] for every collection in the client."""
    return [
        {"name": c.name, "count": c.count()}
        for c in client.list_collections()
    ]


def get_collection_info(collection) -> dict[str, Any]:
    """Return {name, count, metadata_keys} summary for a collection."""
    count = collection.count()
    metadata_keys: set[str] = set()
    if count > 0:
        sample = collection.get(limit=min(10, count), include=["metadatas"])
        for meta in sample.get("metadatas") or []:
            metadata_keys.update(meta.keys())
    return {
        "name": collection.name,
        "count": count,
        "metadata_keys": sorted(metadata_keys),
    }


def get_collection_documents(
    collection,
    limit: int = 20,
    offset: int = 0,
    where_filter: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Return a paginated slice of raw documents from a collection."""
    kwargs: dict[str, Any] = {
        "limit": limit,
        "offset": offset,
        "include": ["documents", "metadatas"],
    }
    if where_filter:
        kwargs["where"] = where_filter
    result = collection.get(**kwargs)
    return {
        "ids": result.get("ids", []),
        "documents": result.get("documents", []),
        "metadatas": result.get("metadatas", []),
        "count": len(result.get("ids", [])),
    }


def build_where_filter(
    kind: str | None = None,
    library: str | None = None,
    name: str | None = None,
) -> dict[str, str] | None:
    """Build a ChromaDB where filter from optional kind/library/name args."""
    conditions: list[dict[str, str]] = []
    if kind:
        conditions.append({"kind": {"$eq": kind}})
    if library:
        conditions.append({"library": {"$eq": library}})
    if name:
        conditions.append({"name": {"$eq": name}})
    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def format_collection_list(collections: list[dict[str, Any]]) -> str:
    """Format list_collections output for the terminal."""
    if not collections:
        return "No collections found."
    lines = ["Available collections:"]
    for c in collections:
        lines.append(f"  {c['name']} ({c['count']} docs)")
    return "\n".join(lines)


def format_collection_info(info: dict[str, Any]) -> str:
    """Format get_collection_info output for the terminal."""
    keys = ", ".join(info["metadata_keys"]) or "(none)"
    return (
        f"Collection : {info['name']}\n"
        f"Documents  : {info['count']}\n"
        f"Meta keys  : {keys}"
    )


def format_documents(
    data: dict[str, Any],
    truncate: bool = True,
) -> str:
    """Format get_collection_documents output for the terminal.

    When *truncate* is False the full document text is shown.
    """
    output: list[str] = []
    for i, (doc_id, doc, meta) in enumerate(
        zip(data["ids"], data["documents"], data["metadatas"]),
        start=1,
    ):
        name = meta.get("name", doc_id)
        kind = meta.get("kind", "?")
        text = doc or ""
        output.append(f"\n  [{i}] {name} ({kind})")
        output.append(f"      {text[:160] if truncate else text}")
    return "\n".join(output) if output else "(no documents)"


def run_query(collection, query_input: QueryInput):
    kwargs = {
        "query_texts": [query_input.query_text],
        "n_results": query_input.n_results,
    }
    if query_input.where_filter:
        kwargs["where"] = query_input.where_filter
    return collection.query(**kwargs)


def format_results(results) -> str:
    output: list[str] = []
    for i, (doc, meta, dist) in enumerate(
        zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        ),
        start=1,
    ):
        name = meta.get("name", "N/A")
        kind = meta.get("kind", "N/A")
        file_name = meta.get("file_name", "")
        source = meta.get("source", "")
        chunk_index = meta.get("chunk_index", "")
        total_chunks = meta.get("total_chunks", "")
        desc = meta.get("description", "")[:80]
        jira = meta.get("jira_tickets", "")
        prs = meta.get("pull_request_ids", "")
        chunk_label = (
            f" [chunk {chunk_index}/{int(total_chunks) - 1}]"
            if chunk_index != "" and total_chunks != ""
            else ""
        )
        output.append(f"\n  [{i}] {name} ({kind}){chunk_label}  dist={dist:.4f}")
        output.append(f"      file: {file_name} ({source})")
        if desc:
            output.append(f"      desc: {desc}")
        if jira:
            output.append(f"      jira: {jira}")
        if prs:
            output.append(f"      prs: {prs}")
        output.append("      ---")
        output.append(f"      {(doc or '')[:200]}")

    return "\n".join(output)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Query and inspect ChromaDB knowledge collections."
        )
    )
    parser.add_argument(
        "collection_name",
        nargs="?",
        help="Collection to query or inspect. Omit with --list-collections.",
    )
    # Collection management
    parser.add_argument(
        "--list-collections",
        action="store_true",
        help="List all available collections and their document counts.",
    )
    parser.add_argument(
        "--info",
        action="store_true",
        help="Show collection info (count, metadata keys).",
    )
    parser.add_argument(
        "--documents",
        action="store_true",
        help="Dump documents (paginated).",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=20,
        help="Max documents to return with --documents (default: 20).",
    )
    parser.add_argument(
        "--offset",
        type=int,
        default=0,
        help="Offset for --documents pagination (default: 0).",
    )
    # Shared filters
    parser.add_argument(
        "--kind",
        help="Filter by kind metadata (e.g. class, function).",
    )
    parser.add_argument(
        "--library",
        help="Filter by library metadata.",
    )
    parser.add_argument(
        "--name",
        help="Filter by exact name metadata (e.g. PDAMInputScreen).",
    )
    # Query mode
    parser.add_argument(
        "--query",
        help=(
            "Run one semantic query and exit. "
            "Supports inline flags: --n=5 --kind=class"
        ),
    )
    # Path override
    parser.add_argument(
        "--chroma",
        default=CHROMA_PATH,
        help=f"Path to ChromaDB directory (default: {CHROMA_PATH}).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    # --list-collections: no collection needed
    if args.list_collections:
        client = get_client(args.chroma)
        print(format_collection_list(list_collections(client)))
        return 0

    if not args.collection_name:
        parser.error(
            "collection_name is required unless --list-collections is set."
        )

    # --info
    if args.info:
        try:
            col = get_collection(args.collection_name, args.chroma)
        except Exception as exc:
            print(f"Error: {exc}")
            return 1
        print(format_collection_info(get_collection_info(col)))
        return 0

    # --documents
    if args.documents:
        try:
            col = get_collection(args.collection_name, args.chroma)
        except Exception as exc:
            print(f"Error: {exc}")
            return 1
        where = build_where_filter(args.kind, args.library, args.name)
        data = get_collection_documents(
            col, limit=args.limit, offset=args.offset,
            where_filter=where,
        )
        print(
            f"Collection: {args.collection_name} "
            f"(showing {data['count']} / offset {args.offset})"
        )
        print(format_documents(data, truncate=args.name is None))
        return 0

    # --query (one-shot) or interactive
    try:
        collection = get_collection(args.collection_name, args.chroma)
    except Exception as exc:
        print(
            f"Error: Could not get collection "
            f"'{args.collection_name}': {exc}"
        )
        return 1

    if args.query:
        query_input = parse_query_input(args.query)
        results = run_query(collection, query_input)
        print(f"Collection: {collection.name}")
        print(f"Total embeddings: {collection.count()}")
        print(format_results(results))
        return 0

    interactive_loop(collection)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
