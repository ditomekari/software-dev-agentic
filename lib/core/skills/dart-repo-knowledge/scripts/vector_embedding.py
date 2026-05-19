"""Vector embedding and document chunking for ChromaDB.

This module provides the VectorEmbedding class which handles:
- Intelligent semantic chunking of Markdown documents
- Preserving context through header re-injection
- Embedding chunks into ChromaDB collections using batch API

The chunking strategy uses a two-pass approach:
1. Split at ## and ### Markdown headers
2. Further split oversized chunks at logical boundaries

Example:
    from chromadb import PersistentClient
    from src import VectorEmbedding, DocumentCreation

    client = PersistentClient(path="chroma_db")
    collection = client.get_or_create_collection("my_docs")

    for markdown, metadata in documents:
        VectorEmbedding.embed_to_chroma_db_collection(
            collection=collection,
            document=markdown,
            metadata=metadata
        )
"""

import re
import time
from chromadb import Collection
from typing import List, Dict, Any

class VectorEmbedding:
    @staticmethod
    def _overflow_split(
        text: str,
        chunk_size: int,
        prefix: str = "",
    ) -> List[str]:
        """Split oversized text at logical boundaries
        (paragraph > sentence > newline > word), re-injecting
        `prefix` at the start of every continuation piece so
        context is never lost.

        Args:
            text: Raw text to split.
            chunk_size: Maximum characters per chunk.
            prefix: Header(s) to prepend to every piece after
                the first (e.g. the method name that owns this
                text).

        Returns:
            List of character-bounded chunks, each starting
            with `prefix` except the first.
        """
        pieces: List[str] = []
        remaining = text
        first = True

        while remaining:
            head = "" if first else prefix
            first = False
            budget = chunk_size - len(head)

            if budget <= 0:
                # prefix alone is too large — hard-cut
                pieces.append(head + remaining[:chunk_size])
                remaining = remaining[chunk_size:]
                continue

            if len(remaining) <= budget:
                pieces.append(head + remaining)
                break

            # Prefer logical break points within budget
            para = remaining.rfind("\n\n", 0, budget)
            sent = remaining.rfind(". ", 0, budget)
            newl = remaining.rfind("\n", 0, budget)
            spc  = remaining.rfind(" ", 0, budget)

            if para > 0:
                cut = para + 2
            elif sent > 0:
                cut = sent + 2
            elif newl > 0:
                cut = newl + 1
            elif spc > 0:
                cut = spc + 1
            else:
                cut = budget  # hard break as last resort

            pieces.append(head + remaining[:cut])
            remaining = remaining[cut:]

        return pieces

    @staticmethod
    def chunk_markdown_document(
        document: str,
        chunk_size: int = 1000,
    ) -> List[str]:
        """Two-pass semantic chunking.

        Pass 1 — split at ``###`` member boundaries so each
        method / field / constructor becomes its own candidate
        chunk.  ``##`` class-level sections are treated as
        natural split points too.

        Pass 2 — any candidate that still exceeds ``chunk_size``
        is further split by :meth:`_overflow_split`, which
        re-injects the member header as a prefix into every
        continuation piece so the semantic anchor is never lost.

        Args:
            document: Markdown document produced by
                :class:`DocumentCreation`.
            chunk_size: Soft max characters per final chunk.

        Returns:
            List of chunks, each semantically coherent.
        """
        # Extract file-level title (# File: ...) for context
        title_match = re.search(
            r'^#\s+.+$', document, re.MULTILINE,
        )
        doc_title = (
            title_match.group(0) if title_match else ""
        )

        # --- Pass 1: split at ## and ### boundaries ----------
        # Pattern captures the header line itself so we can
        # use it as a continuation prefix in pass 2.
        member_pattern = re.compile(
            r'^(#{2,3}\s+.+)$', re.MULTILINE,
        )
        raw_parts = member_pattern.split(document)
        # raw_parts alternates: [pre-text, header, body, ...]

        # Pair each header with its body text
        candidates: List[str] = []
        if raw_parts[0].strip():
            candidates.append(raw_parts[0])

        i = 1
        while i < len(raw_parts):
            header = raw_parts[i]
            body   = raw_parts[i + 1] if i + 1 < len(raw_parts) else ""
            candidates.append(header + body)
            i += 2

        # --- Pass 2: overflow-split oversized candidates -----
        chunks: List[str] = []
        for candidate in candidates:
            if len(candidate) <= chunk_size:
                chunks.append(candidate)
            else:
                # Determine re-injection prefix: the first
                # line of the candidate (the header), plus the
                # doc title for full disambiguation.
                first_line = candidate.split("\n", 1)[0]
                prefix = (
                    doc_title + "\n" + first_line + " (cont.)\n\n"
                    if doc_title and first_line != doc_title
                    else first_line + " (cont.)\n\n"
                )
                chunks.extend(
                    VectorEmbedding._overflow_split(
                        candidate, chunk_size, prefix,
                    )
                )

        return [c for c in chunks if c.strip()]
    
    @staticmethod
    def embed_to_chroma_db_collection(
        collection: Collection,
        document: str,
        metadata: Dict[str, Any]
    ) -> None:
        """Chunk and embed a document into ChromaDB using batch API.

        Args:
            collection: ChromaDB collection instance.
            document: Markdown document to embed.
            metadata: Metadata dictionary for the document.
        """
        chunks = VectorEmbedding.chunk_markdown_document(
            document=document,
        )

        file_name = metadata.get("file_name", "unknown_file")
        name = metadata.get("name", "unknown_name")
        source = metadata.get("source", "")

        # Build stable chunk IDs
        source_key = (
            source
            .replace("/", "_")
            .replace("\\", "_")
            .replace(".", "_")
            if source else file_name
        )

        # Prepare batch data
        ids = []
        documents = []
        metadatas = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{source_key}_{name}_{i}"
            chunk_metadata = {
                "chunk_index": i,
                "total_chunks": len(chunks)
            }

            # Add component metadata
            for key, value in metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    chunk_metadata[key] = value
                elif isinstance(value, list) and all(
                    isinstance(item, (str, int, float, bool))
                    for item in value
                ):
                    chunk_metadata[key] = ", ".join(str(item) for item in value)

            ids.append(chunk_id)
            documents.append(chunk)
            metadatas.append(chunk_metadata)

        # Batch upsert (more efficient than individual adds)
        try:
            collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
        except Exception as e:
            print(f"Error upserting document {name}: {str(e)}")