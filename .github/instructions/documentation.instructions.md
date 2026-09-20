---
description: "Documentation guidance for README files, technical notes, diagrams, examples, and learning documentation."
applyTo: "**/*.md"
---

# Documentation Instructions

## Purpose

Documentation in this repository should help the reader understand the
technology, the experiment, and the reasoning behind the implementation.

Documentation is part of the learning process.

The goal is not to produce marketing material or generic technical prose.

The goal is:

**Explain what was built, why it was built, and how it works.**

## Writing style

Prefer:

- clear language
- concise explanations
- factual statements
- short paragraphs
- meaningful headings
- practical examples
- technically accurate terminology
- step-by-step explanations where appropriate

Avoid:

- marketing language
- unnecessary buzzwords
- vague statements
- excessive repetition
- unnecessarily complicated wording
- claims that are not supported by the implementation

Write so that another developer can understand the experiment without
having to inspect every line of code first.

## Learning-oriented documentation

Documentation should explain the underlying concept, not only the commands
required to run the software.

Where appropriate, explain:

- what the technology is
- why it is used
- how it works
- where it is used in the project
- what the experiment demonstrates
- what limitations exist

Prefer concrete examples over abstract explanations.

For example:

```text
User question
      ↓
Query embedding
      ↓
Qdrant similarity search
      ↓
Top-k chunks
      ↓
Context
      ↓
Prompt
      ↓
LLM
      ↓
Answer
```

A simple diagram like this can often communicate a process more clearly
than several paragraphs of abstract explanation.

## Documentation structure

Where appropriate, documentation may contain sections such as:

1. Purpose
2. Architecture
3. Prerequisites
4. Installation
5. Configuration
6. How it works
7. Example usage
8. Important implementation details
9. Limitations
10. Troubleshooting
11. Future improvements

Not every document needs every section.

Use only the sections that make sense for the specific experiment.

Avoid creating sections simply to make a document appear complete.

## README files

When a README already exists:

- update the existing README
- preserve useful existing information
- avoid creating duplicate documentation
- keep examples synchronized with the implementation
- keep commands synchronized with the current project structure

Do not create a second document that explains the same thing unless there
is a clear reason to separate the information.

The README should remain the primary entry point for understanding an
experiment.

## Repository documentation

The repository-level README should explain the overall purpose of the
project.

It may describe:

- the purpose of the playground
- the learning philosophy
- the major experiments
- the repository structure
- important technologies
- how individual experiments are organized

Keep detailed implementation information in the README of the relevant
experiment when appropriate.

Avoid turning the root README into a complete manual for every project.

## Project documentation

A project-specific README should explain the individual experiment.

For example, a RAG project README may explain:

```text
Document
   ↓
Chunking
   ↓
Embedding
   ↓
Qdrant
   ↓
Retrieval
   ↓
Context
   ↓
LLM
```

It should also explain how to start the required services and run the
experiment.

Keep project-specific information close to the project it describes.

## Technical accuracy

Documentation must reflect the actual implementation.

Do not document features that do not exist yet as if they were already
implemented.

Clearly distinguish between:

```text
Implemented
Experimental
Planned
```

when appropriate.

For example:

```markdown
> **Status:** Experimental
```

or:

```markdown
> **Planned:** Hybrid search will be evaluated in a future experiment.
```

Do not silently present planned functionality as current functionality.

## Code examples

Use fenced code blocks with the appropriate language identifier.

Python:

```python
query_vector = embeddings.embed_query(question)
```

Shell commands:

```bash
docker compose up -d
```

YAML:

```yaml
services:
  qdrant:
    image: qdrant/qdrant:latest
```

JSON:

```json
{
  "model": "text-embedding-3-small"
}
```

Use the correct language identifier whenever practical.

## Commands

Commands in documentation should be directly usable where possible.

For example:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If a command depends on a specific directory, make that clear.

Example:

```bash
cd 01-rag
streamlit run ragchatbot/rag-chatbot-lab.py
```

Do not assume that the reader knows the current working directory.

## Configuration

Document important configuration requirements.

Examples include:

- environment variables
- API keys
- service URLs
- ports
- Docker containers
- local services
- model names
- vector dimensions

Never document real credentials.

Use placeholders or environment variables instead.

Example:

```text
OPENAI_API_KEY=<your-api-key>
```

Do not include actual API keys in documentation, screenshots, examples,
or code blocks.

## Architecture diagrams

Use ASCII diagrams when they improve understanding of architecture,
data flow, or dependencies.

Prefer simple diagrams that show relationships and direction.

Example:

```text
Documents
    │
    ▼
Ingestion
    │
    ▼
Embeddings
    │
    ▼
Qdrant
    │
    ▲
    │
Query → Embedding → Search
                    │
                    ▼
                  Context
                    │
                    ▼
                   LLM
```

Keep diagrams consistent with the actual implementation.

Do not show components that do not exist.

## Tables

Use Markdown tables when they make structured information easier to
compare or understand.

Good examples include:

- configuration values
- project components
- technology comparisons
- pipeline stages
- supported file types

Avoid using tables for long prose.

## Screenshots and images

Use screenshots and diagrams when they provide useful visual information.

Images should:

- be relevant
- have a clear purpose
- reflect the current implementation
- be labelled where necessary

Avoid adding images merely for decoration.

If a screenshot becomes outdated because the UI or implementation changes,
update or remove it.

## Terminology

Use technical terms consistently.

For example, distinguish clearly between:

```text
Embedding
Vector
Vector database
Retriever
Context
Prompt
LLM
RAG
```

Do not use these terms interchangeably when they represent different
components or concepts.

When introducing an abbreviation for the first time, spell it out when
appropriate.

Example:

```text
Retrieval Augmented Generation (RAG)
```

After that, `RAG` may be used.

## Explaining architecture

When documenting architecture, explain both the components and the
relationship between them.

For example:

```text
Embedding Model
       │
       ▼
Document Vectors
       │
       ▼
    Qdrant
       ▲
       │
Query Vector
       │
       ▼
   Retriever
       │
       ▼
    Context
       │
       ▼
      LLM
```

Explain what each component is responsible for.

Do not describe the entire architecture as a single "AI system" when
the experiment is specifically intended to demonstrate the interaction
between several components.

## Learning progression

Documentation should support the progression from simple concepts to
more advanced concepts.

When appropriate, explain a concept in layers:

```text
Basic concept
    ↓
Simple implementation
    ↓
Framework implementation
    ↓
Advanced implementation
```

For example, a RAG experiment may first demonstrate manual similarity
search before introducing Qdrant.

Do not remove the simpler explanation merely because the later
implementation is more powerful.

## Experimental results

When documenting experiment results:

- describe what was tested
- describe the observed behavior
- distinguish observations from assumptions
- document relevant configuration
- mention limitations

Avoid presenting a single experiment as universal proof.

Prefer:

```text
In this experiment, the query returned...
```

over:

```text
This always returns...
```

when the result depends on the specific test data or configuration.

## Troubleshooting

When documenting troubleshooting information, use a clear structure:

```text
Problem
    ↓
Possible cause
    ↓
How to check
    ↓
How to resolve
```

Example:

```markdown
### Qdrant is not reachable

**Possible cause:** The Docker container is not running.

Check:

```bash
docker ps
```

Start Qdrant:

```bash
docker compose up -d qdrant
```
```

Prefer practical diagnostic steps over generic advice.

## Limitations

Document important limitations of experiments.

Examples include:

- experimental code
- local-only configuration
- limited document types
- lack of authentication
- simplified error handling
- no production security model
- small test dataset
- dependency on external APIs

Limitations are part of the documentation and should not be hidden.

## Security documentation

When documentation describes systems that handle data, mention relevant
security considerations.

For RAG systems in particular, document that authorization should be
enforced before unauthorized content is provided to the LLM.

Do not suggest that a prompt alone is a reliable security boundary.

Avoid including:

- API keys
- passwords
- tokens
- private URLs
- confidential document content

in documentation.

## Keeping documentation synchronized

When code changes affect documented behavior, update the relevant
documentation.

Examples:

- changing a port
- changing a model
- changing a collection name
- changing a file path
- changing a command
- changing a dependency
- changing the RAG pipeline

Do not leave documentation describing an old implementation.

## Avoid duplicate documentation

Before creating a new Markdown file:

1. Check whether the information already exists.
2. Determine whether the existing document should be updated.
3. Create a new document only when the information has a clear separate
   purpose.

Prefer a small number of useful documents over many fragmented files.

## Markdown conventions

Use:

- `#` for the document title
- `##` for major sections
- `###` for subsections
- fenced code blocks for code
- bullet lists for short collections
- numbered lists for ordered procedures
- tables for structured comparisons

Keep heading levels logically ordered.

Do not skip heading levels without a good reason.

## Documentation changes

When modifying documentation:

1. Check the existing document first.
2. Preserve useful existing content.
3. Update rather than duplicate information.
4. Keep terminology consistent.
5. Keep examples synchronized with the code.
6. Verify commands where practical.
7. Clearly distinguish implemented and planned functionality.

Do not rewrite an entire README when a targeted update is sufficient.

## Important rule

Documentation should make the project easier to understand, not merely
make it look more complete.

Prefer:

**Clear → Accurate → Understandable → Reproducible**

over:

**Long → Complex → Impressive**

The documentation is part of the laboratory.

It should help a developer understand not only what was built, but also
why it was built and how the underlying technology works.
