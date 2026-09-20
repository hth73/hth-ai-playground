# AGENTS.md

## Purpose

This repository is a personal AI playground for learning, experimenting, and understanding modern AI technologies.

The primary goal is:

**Understand the technology by building it.**

This is a learning and experimentation repository, not a production-ready framework or a generic application template.

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
- Prefer the explicit solution when a simple, more understandable implementation is available.

---

## Repository context

This repository contains experiments and proof-of-concepts around:

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

New experiments should fit naturally into the existing learning-oriented structure.

---

## Coding expectations

### Python

Prefer Python for experiments, scripts, utilities, RAG pipelines, AI prototypes, and notebooks.

Use clear and descriptive names.

Prefer readable and explicit Python code:

- small, focused functions
- simple control flow
- straightforward data transformations
- understandable naming conventions
- minimal unnecessary abstraction

Avoid introducing frameworks or libraries unless they provide meaningful value.

When the code is educational, prefer readable code over clever or compact code.

Use `snake_case` for variables and functions, `PascalCase` for classes, and descriptive module names.

Keep the main execution flow easy to follow from top to bottom.

### RAG guidance

Treat the RAG pipeline as a visible sequence of stages:

```text
Documents
  ↓
Text extraction
  ↓
Chunking
  ↓
Metadata
  ↓
Embeddings
  ↓
Vector database
  ↓
Query embedding
  ↓
Similarity search
  ↓
Retrieved chunks
  ↓
Context
  ↓
Prompt
  ↓
LLM
  ↓
Answer
```

Do not hide these stages behind unnecessary abstractions when the purpose is to understand the mechanism.

Keep these concerns explicit:

- document ingestion
- chunking
- metadata
- vector generation
- query embedding
- similarity search
- context construction
- prompt composition

Document model and dimensionality assumptions clearly, especially when using vector databases.

### Documentation

Documentation is part of the learning process.

It should explain:

- what was built
- why it was built
- how it works
- what the experiment demonstrates
- any limitations or trade-offs

Prefer clear, concise, factual writing and practical examples over marketing language or abstraction.

When a README already exists, update it instead of creating duplicate documentation.

---

## Operational rules

- Keep configuration explicit and transparent.
- Use environment variables for secrets, API keys, and tokens.
- Do not hard-code credentials in source files.
- Do not expose secrets in logs or debugging output.
- Handle expected errors clearly and user-friendly.
- Keep prompts and model choices easy to inspect when they are educationally relevant.
- Make implementation details visible when the experiment is meant to teach the technology.
- Do not claim features are implemented unless the code actually supports them.

---

## What to avoid

- Overly abstract or generic application layers
- Unnecessary refactors of working educational code
- Hidden data flow or invisible pipeline steps
- Marketing-style documentation
- Vague or duplicated explanations
- Hardcoded secrets or credentials
- Unclear chunking or embedding assumptions
- Rewriting working experiments just for style

---

## Working style

When contributing to this repository, favor work that is:

- understandable
- small in scope
- explicit in flow
- educational in value
- traceable to the concept being demonstrated

The goal is not to optimize for the most polished production template; the goal is to make the technology understandable.
