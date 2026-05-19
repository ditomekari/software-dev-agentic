#!/usr/bin/env python3
"""Read-only anchor query smoke checks for Dart knowledge collections."""

from __future__ import annotations

import argparse
from pathlib import Path

import chromadb


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run exact and semantic anchor checks on a collection."
    )
    parser.add_argument("collection_name")
    parser.add_argument("anchors", nargs="+", help="Anchor symbols to probe")
    parser.add_argument(
        "--chroma-path",
        default=(
            Path(__file__).resolve().parents[2]
            / "dart-repo-knowledge"
            / "chroma_db"
        ).as_posix(),
        help="Path to the ChromaDB directory",
    )
    parser.add_argument(
        "--semantic-results",
        type=int,
        default=3,
        help="Number of semantic results to print per anchor",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    client = chromadb.PersistentClient(path=args.chroma_path)
    collection = client.get_collection(args.collection_name)

    print(f"Collection: {collection.name}")
    print(f"Total embeddings: {collection.count()}")

    for anchor in args.anchors:
        print(f"\nAnchor: {anchor}")

        exact = collection.get(
            where_document={"$contains": anchor},
            limit=5,
        )
        exact_count = len(exact.get("ids", []))
        print(f"  Exact matches: {exact_count}")

        semantic = collection.query(
            query_texts=[anchor],
            n_results=args.semantic_results,
        )
        print("  Top semantic matches:")
        for index, (doc, meta, dist) in enumerate(
            zip(
                semantic["documents"][0],
                semantic["metadatas"][0],
                semantic["distances"][0],
            ),
            start=1,
        ):
            name = meta.get("name", "N/A")
            kind = meta.get("kind", "N/A")
            file_name = meta.get("file_name", "")
            print(
                f"    [{index}] {name} ({kind}) "
                f"dist={dist:.4f} file={file_name}"
            )
            print(f"        {(doc or '')[:160].replace(chr(10), ' ')}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
