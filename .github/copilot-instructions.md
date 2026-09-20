# hth-ai-playground - Copilot Instructions

## Project purpose

This repository is a personal AI playground for learning, experimenting,
and understanding modern AI technologies.

The primary goal is:

**Understand the technology by building it.**
This is a learning and experimentation repository, not a production-ready
framework or generic application template.

Keep implementations educational, traceable, reproducible, and easy to explain.

---

## Core principles
- Prefer small, inspectable experiments over abstraction-heavy code.
- Make the individual steps of a pipeline visible.
- Prefer transparent implementations over hidden framework magic.
- Keep code easy to explain in a workshop, demo, or lab session.
- Use explicit and descriptive names.
- Keep data flow understandable.
- Preserve the learning intent when extending or improving existing code.
- Do not refactor working educational code merely for stylistic reasons.

When there is a choice between:
1. a highly abstract solution, and
2. a slightly more explicit solution that makes the underlying mechanism easier
   to understand,

prefer the explicit solution.

---

## Repository context

The repository contains experiments and proof-of-concepts around:
- Generative AI
- Large Language Models (LLMs)
- Retrieval Augmented Generation (RAG)
- Embeddings
- Vector similarity
- Vector databases
- Qdrant
- OpenAI APIs
- Local AI infrastructure
- Docker-based services
- AI-assisted development
- Agents and MCP
- Python automation and tooling

The repository is expected to grow over time.

New experiments should fit naturally into the existing learning-oriented structure.

---

## Coding expectations

### Python

Prefer Python for:
- experiments
- scripts
- utilities
- RAG pipelines
- AI prototypes
- notebooks

Use clear and descriptive names.

Examples:
```text
manual_retriever
qdrant_retriever
chunk_documents
build_context
query_embedding
```
