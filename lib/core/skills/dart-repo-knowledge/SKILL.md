---
name: dart-repo-knowledge
description: Generates RAG (Retrieval-Augmented Generation) knowledge from any Dart codebase by extracting dartdoc comments, converting to Markdown, and embedding into a local ChromaDB vector store. Use when you need to build searchable knowledge from Dart source code for context enrichment in other skills/agents. Supports versioned snapshots, cross-version diffing, Jira ticket extraction, and PR extraction from git history.
user-invocable: true
argument-hint: 'Describe the knowledge task: generate, compare, or query. Optionally include source path, repo path, version, and collection name.'
---

# Dart Repo Knowledge

## Overview

Extract dartdoc documentation from any Dart project, convert it to
structured Markdown, chunk it, and embed it into a local ChromaDB
vector store. The resulting knowledge base is queried by the
`dart-knowledge-query` and `dart-knowledge-auditor` agents.

**Pipeline:** Dart source → dartdoc JSON → Markdown → Chunks → ChromaDB

### Key Capabilities

- Versioned, reproducible collection names
  (e.g. `my_library_v1_0_0`, `design_system_v2_22_0`)
- Jira ticket extraction from git history
- Pull request extraction from git history (optional)
- Cross-version API diffing (`--compare`)
- External pub-cache repo indexing via `--repo-dir`
- Query + collection management via unified CLI

## When to Use

- Index a Dart library from the current workspace
- Index a Dart package from pub-cache or an external git repo
- Generate reproducible versioned collections
- Ensure Jira and PR metadata are embedded correctly
- Validate a generated collection with query smoke checks

Load the deeper branching logic from
[maintenance playbook](./references/maintenance-playbook.md) when the
issue involves coverage gaps, retrieval failures, or external-repo
mistakes.

---

## Prerequisites

### 1. Check Python

```bash
python3 --version
```

### 2. Create Virtual Environment & Install Dependencies

```bash
cd .claude/skills/dart-repo-knowledge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install dartdoc_json

```bash
dart pub global activate dartdoc_json
```

Verify: `dartdoc_json --help`

If the command fails, add `~/.pub-cache/bin` to PATH:

```bash
export PATH="$PATH:$HOME/.pub-cache/bin"
```

---

## Quick Start

```bash
cd .claude/skills/dart-repo-knowledge
source venv/bin/activate

# Generate from current project (auto-detect everything)
python3 main.py

# Specify source dir, version, and collection base name
python3 main.py --source /path/to/lib --version v2.2.0 \
  --collection my_library

# Index a pub-cache or external git repo
python3 main.py \
  --source ~/.pub-cache/git/my-package-.../lib \
  --repo-dir ~/.pub-cache/git/my-package-... \
  --version v2.22.0 --collection my_package

# Compare two versions
python3 main.py --compare --from-version v1.30.0 --to-version v2.2.0

# Skip JSON regeneration (reuse existing dataset)
python3 main.py --skip-json
```

**Collection naming:** base + version are normalized automatically.
`my_library` + `v2.22.0` → `my_library_v2_22_0`

---

## CLI Arguments

| Argument           | Default                            | Description                             |
| ------------------ | ---------------------------------- | --------------------------------------- |
| `--source`         | Current project `lib/`             | Path to Dart source directory           |
| `--version`        | Current git branch                 | Version label for collection naming     |
| `--collection`     | `{repo_name}`                      | Base ChromaDB collection name           |
| `--repo-dir`       | Current git root                   | Git repo dir for history extraction     |
| `--dataset`        | `dataset/`                         | Output dir for dartdoc JSON files       |
| `--chroma`         | `chroma_db/`                       | ChromaDB persistence directory          |
| `--git-depth`      | `20`                               | Max commits per file for extraction     |
| `--jira-url`       | _(project-specific)_               | Jira base URL                           |
| `--ticket-pattern` | `[A-Z]+-\d+`                       | Regex for Jira ticket IDs               |
| `--no-jira`        | —                                  | Skip Jira ticket extraction             |
| `--pr-url`         | _(empty)_                          | PR base URL                             |
| `--pr-pattern`     | `pull request #(\d+)`              | Regex with one capture group for PR IDs |
| `--no-pr`          | —                                  | Skip PR extraction                      |
| `--skip-json`      | —                                  | Reuse existing dataset, skip generation |
| `--skip-verify`    | —                                  | Skip the post-embed verification step   |
| `--compare`        | —                                  | Enable version comparison mode          |
| `--from-version`   | —                                  | Starting version for comparison         |
| `--to-version`     | —                                  | Target version for comparison           |

---

## Querying Collections

`query.py` is the unified read-only CLI. It replaces the former MCP
server and provides all collection management tools as plain functions
importable by other agents.

```bash
cd .claude/skills/dart-repo-knowledge

# List all available collections
./venv/bin/python3 query.py --list-collections

# Inspect a collection (count + metadata keys)
./venv/bin/python3 query.py <collection> --info

# Dump paginated documents
./venv/bin/python3 query.py <collection> --documents --limit 10

# Filter documents by kind
./venv/bin/python3 query.py <collection> --documents --kind class

# Filter documents by exact name (full content, no truncation)
./venv/bin/python3 query.py <collection> --documents --name MyWidget

# Combine filters (also shows full content because --name is set)
./venv/bin/python3 query.py <collection> --documents --kind class --name MyWidget

# One-shot semantic query
./venv/bin/python3 query.py <collection> \
  --query "spacing widget --n=5 --kind=class"

# Interactive query loop
./venv/bin/python3 query.py <collection>
```

### Inline query flags

Inside `--query` and the interactive loop:

- `--n=<count>` — number of results
- `--kind=<kind>` — filter by kind metadata

### Document truncation

By default `--documents` truncates each chunk to 160 characters for
browsing. When `--name` is provided the full content of every chunk
is shown (no truncation), making it suitable for deep inspection of
a specific symbol.

### Collection helper functions (for agents)

```python
from query import (
    get_client, get_collection,
    list_collections, get_collection_info,
    get_collection_documents, build_where_filter,
    format_collection_list, format_collection_info,
    format_documents,
)

client = get_client("chroma_db")
print(format_collection_list(list_collections(client)))

col = get_collection("<collection_name>")
print(format_collection_info(get_collection_info(col)))

data = get_collection_documents(col, limit=20, offset=0)
print(format_documents(data))  # truncated preview

# Filter by name — pass truncate=False for full content
where = build_where_filter(name="MySymbolName")
data = get_collection_documents(col, limit=20, where_filter=where)
print(format_documents(data, truncate=False))
```

---

## Smoke Checks

After generation, use the anchor smoke script to validate key symbols:

```bash
./venv/bin/python3 scripts/anchor_query_smoke.py \
  <collection_name> SymbolA SymbolB SymbolC \
  --semantic-results 3
```

---

## Pipeline Detail

1. **Auto-detect** source dir, version, and repo name from git
2. **Check** that `dartdoc_json` is installed
3. **Step 1 — Generate JSON:** Runs `dartdoc_json` on every `.dart`
   file, filters files without useful documentation
4. **Step 1.5 — Extract git history:** Scans commits for Jira
   ticket IDs (`[A-Z]+-\d+`) and PR IDs per source file
5. **Step 2 — Embed:** Converts JSON to structured Markdown (with
   Jira and PR sections), chunks it, embeds into ChromaDB with
   ticket and PR metadata
6. **Step 3 — Verify:** Runs sample queries to confirm collection

---

## Common Issues

| Issue                             | Solution                                                                |
| --------------------------------- | ----------------------------------------------------------------------- |
| `dartdoc_json: command not found` | `dart pub global activate dartdoc_json`; add `~/.pub-cache/bin` to PATH |
| Empty dataset                     | Verify `--source` path contains `.dart` files                           |
| `Collection not found`            | Run full generation first                                               |
| `ModuleNotFoundError: chromadb`   | Activate venv: `source venv/bin/activate`                               |
| Missing Jira tickets              | Use `--repo-dir` when indexing pub-cache repos                          |

---

## File Reference

```
.claude/skills/dart-repo-knowledge/
├── SKILL.md              # This file
├── main.py               # Orchestrator — full generation pipeline
├── query.py              # Query + collection management CLI
├── requirements.txt      # Python deps: chromadb, sentence-transformers
├── pyproject.toml
├── .gitignore            # Excludes chroma_db/, dataset/, venv/
├── scripts/
│   ├── __init__.py       # Exports all pipeline modules
│   ├── config.py
│   ├── dart_doc_generator.py
│   ├── document_creation.py
│   ├── git_history.py
│   ├── repo_manager.py
│   ├── vector_embedding.py
│   ├── version_comparison.py
│   └── anchor_query_smoke.py
└── references/
    └── maintenance-playbook.md
```
