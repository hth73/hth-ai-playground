---
description: "RAG-specific guidance for document ingestion, chunking, embeddings, vector databases, retrieval, context construction, and LLM integration."
applyTo: "01-rag/**/*.py, 01-rag/**/*.md"
---

# RAG Instructions

## Purpose

The RAG experiments in this repository are intended to understand how
Retrieval Augmented Generation works internally.

The primary goal is not to build the most abstract or production-ready
RAG framework.

The primary goal is:

**Understand the RAG pipeline by building and inspecting it.**

Keep the individual stages visible, understandable, and easy to explain.

## Core RAG principle

Keep the conceptual RAG pipeline explicit:

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

Do not hide these stages behind unnecessary abstractions when the purpose
of the experiment is to understand the mechanism.

Each stage should have a clear responsibility.

## Document ingestion

Treat document ingestion as a separate stage.

The ingestion process may include:

1. Loading the document.
2. Extracting text.
3. Splitting the text into chunks.
4. Creating metadata.
5. Generating embeddings.
6. Storing vectors and metadata.

Keep these steps identifiable in the implementation.

When possible, make it easy to inspect intermediate results such as:

- document count
- extracted text
- chunk count
- chunk content
- metadata
- embedding dimensions

Do not hide the complete ingestion process behind a single opaque function
if the experiment is intended to teach how ingestion works.

## Document sources

The RAG experiments may work with different document types such as:

- PDF
- TXT
- Markdown
- DOCX
- source code
- configuration files

Treat source-specific loading and extraction as separate concerns from
chunking and embedding.

The same conceptual pipeline should remain understandable regardless of
the document type.

## Chunking

Chunking is an important part of the RAG pipeline.

Keep chunking visible and understandable.

When changing chunking:

- explain the reason for the change
- keep chunk size understandable
- keep overlap understandable
- preserve source information
- make chunks traceable to their original document

Remember that chunking affects retrieval quality.

Avoid introducing complex semantic or hierarchical chunking strategies
unless the experiment specifically focuses on those techniques.

Start with simple and understandable chunking.

## Metadata

Metadata should remain visible and meaningful.

Typical metadata may include:

```text
source
file_type
document_id
chunk_id
chunk_number
```

Metadata should make it possible to understand where a retrieved chunk
originated.

When additional metadata is introduced, explain its purpose.

Do not remove useful metadata merely to simplify the implementation.

For future enterprise-oriented experiments, metadata may also contain
information related to:

```text
department
group
role
classification
permissions
```

However, permissions must be enforced by the application or retrieval
layer.

Do not rely on the LLM to hide information that the user is not
authorized to access.

## Embeddings

Keep the distinction between document embeddings and query embeddings clear.

Document embeddings are generated during ingestion:

```text
Document
    ↓
Embedding model
    ↓
Document embedding
    ↓
Vector database
```

A query embedding is generated when the user asks a question:

```text
User question
    ↓
Embedding model
    ↓
Query embedding
    ↓
Vector similarity search
```

The query embedding is generated at query time.

It is not retrieved from the vector database.

Document embeddings are stored in the vector database.

Keep this distinction visible in code and documentation.

## Embedding dimensions

When using an embedding model, document the relevant vector dimension
when it is important to the experiment.

For example:

```text
text-embedding-3-small
        ↓
1536 dimensions
        ↓
Qdrant collection
```

The vector dimension configured in the vector database must match the
dimension returned by the embedding model.

Do not change the embedding model or vector dimension without considering
the compatibility of the existing vector collection.

## Similarity

Similarity search is a central concept of vector-based retrieval.

Keep the underlying concept understandable.

For educational experiments, it is useful to distinguish between:

```text
Manual Retriever
→ compare the query embedding with vectors held in application memory

Qdrant Retriever
→ compare the query embedding with vectors stored in Qdrant
```

The conceptual operation is similar:

```text
Query vector
     ↓
Similarity comparison
     ↓
Ranking
     ↓
Most relevant vectors
```

Do not replace a manual similarity implementation with a vector database
when the manual implementation exists specifically to demonstrate the
underlying mechanism.

## Manual Retriever

A manual retriever is an educational reference implementation.

Its purpose is to demonstrate what happens conceptually during vector
search.

Keep the following stages visible:

```text
Question
    ↓
Query embedding
    ↓
Compare against document vectors
    ↓
Calculate similarity
    ↓
Sort results
    ↓
Select top-k
```

Do not remove or hide this implementation simply because Qdrant can
perform the search more efficiently.

The manual implementation provides an important reference for understanding
what a vector database is doing internally.

## Qdrant

When using Qdrant, keep the following concepts visible:

- collection
- vector dimensions
- distance metric
- point ID
- vector
- payload
- query vector
- similarity search
- top-k results

The conceptual Qdrant data model is:

```text
Point
├── ID
├── Vector
└── Payload
```

The vector represents the embedding.

The payload can contain the original text and metadata required by the
application.

Do not describe Qdrant as the RAG system itself.

Qdrant is the vector database and search component.

The RAG application orchestrates:

```text
Question
    ↓
Query embedding
    ↓
Qdrant search
    ↓
Retrieved chunks
    ↓
Context construction
    ↓
Prompt
    ↓
LLM
```

## Qdrant persistence

When Qdrant is used with Docker, make persistence explicit.

The vector database should use persistent storage when the experiment
depends on data surviving container restarts.

Do not assume that the original documents and the vector database are
the same thing.

Conceptually:

```text
Original documents
        │
        ├── Source of truth
        │
        ▼
   Ingestion
        │
        ▼
   Qdrant index
```

Qdrant is primarily a retrieval index and vector store.

The original documents may still be required for:

- re-indexing
- changing embedding models
- updating documents
- auditing
- displaying original sources
- rebuilding the vector database

## Retrieval

Retrieval should be treated as a separate stage from generation.

The retriever should:

1. Generate or receive a query embedding.
2. Search the vector database.
3. Select relevant results.
4. Return the relevant chunks and metadata.

Keep retrieval results inspectable during educational experiments.

Useful information may include:

```text
source
chunk number
similarity score
document ID
chunk text
```

Do not hide retrieval results when they are important for understanding
why an answer was generated.

## Top-k

When using top-k retrieval, keep the value visible and understandable.

For example:

```python
top_k = 5
```

Explain the purpose of top-k when it is relevant.

Top-k controls how many retrieved results are passed into the next stage.

Do not introduce dynamic retrieval strategies unless the experiment
specifically focuses on them.

## Context construction

Retrieved chunks become the context supplied to the LLM.

Keep this transition visible:

```text
Qdrant results
      ↓
Retrieved chunks
      ↓
Context
      ↓
Prompt
      ↓
LLM
```

When practical, allow the retrieved context to be inspected.

The context is an important diagnostic tool.

If the answer is incorrect, inspect the retrieved context before assuming
that the LLM itself is the problem.

## Prompt construction

Keep system instructions and user input clearly separated.

A basic RAG prompt should make it clear that the model should answer
using the supplied context.

For example:

```text
System instructions
        +
Retrieved context
        +
User question
        ↓
       LLM
```

The model should not be encouraged to invent information that is not
contained in the retrieved context when the experiment is testing
grounded RAG behavior.

If the required information is not present in the context, prefer a
response that clearly states that the information could not be found.

## Grounding

RAG experiments should distinguish between:

```text
Information found in retrieved context
```

and:

```text
Information supplied by the model from its general knowledge
```

When testing a grounded RAG pipeline, the answer should be based on the
retrieved context.

A useful test is to ask a question that is unrelated to the uploaded
documents.

The system should demonstrate that it does not simply answer from the
LLM's general knowledge when the RAG prompt requires context grounding.

## LLM

Keep the role of the LLM separate from retrieval.

The LLM does not automatically search Qdrant.

The application orchestrates the process:

```text
Application
    │
    ├── Query embedding
    │
    ├── Qdrant retrieval
    │
    ├── Context construction
    │
    └── LLM request
             ↓
           Answer
```

Do not describe the LLM as the vector database or the retriever.

Keep these components conceptually separate:

```text
Embedding model
Vector database
Retriever
RAG application
LLM
```

## RAG versus chat history

Do not confuse RAG with conversation memory.

RAG retrieves external information from a knowledge source.

Conversation history is previous interaction context.

Conceptually:

```text
RAG
→ retrieve external knowledge

Chat history
→ retain previous conversation context
```

If conversation memory is introduced later, document it as a separate
mechanism.

## Security and permissions

For enterprise-oriented RAG experiments, access control must be enforced
before unauthorized data reaches the LLM.

The correct conceptual flow is:

```text
User
  ↓
Authentication
  ↓
Authorization
  ↓
Retrieval with security filtering
  ↓
Authorized context
  ↓
LLM
```

Do not retrieve all documents and rely on the LLM to decide which
information it should hide.

Security filtering belongs in the application or retrieval layer.

## Framework usage

Libraries such as:

- LangChain
- Qdrant Client
- OpenAI SDK
- Streamlit

may be used where they provide useful functionality.

However, do not allow framework abstractions to hide important RAG concepts.

If the purpose of an experiment is to understand retrieval, keep retrieval
visible.

If the purpose is to compare implementations, keep the comparison clear.

Do not introduce an additional framework merely because it provides a
shorter implementation.

## Educational priority

When choosing between:

1. a highly abstract implementation
2. a very short implementation
3. an explicit implementation that exposes the RAG mechanism

prefer the implementation that best supports understanding.

The goal is to understand the technology before optimizing it.

Do not prematurely introduce:

- complex agent frameworks
- rerankers
- hybrid search
- advanced query rewriting
- sophisticated memory systems
- complex orchestration layers

unless the experiment specifically focuses on those topics.

## Existing RAG laboratory code

Treat existing RAG laboratory code as educational material.

Do not remove:

- manual retrieval
- intermediate output
- similarity calculations
- metadata
- retrieved context
- explicit pipeline stages
- educational comments

merely because a framework can provide a shorter implementation.

If a clean chatbot implementation is required, prefer creating a separate
implementation rather than destroying the educational laboratory.

The laboratory should remain useful as a reference implementation.

## Changes to RAG experiments

When modifying a RAG experiment:

1. Identify which RAG stage is affected.
2. Preserve the other stages.
3. Keep the data flow understandable.
4. Make the smallest useful change.
5. Explain changes that affect retrieval behavior.
6. Do not hide important learning concepts behind abstractions.
7. Consider whether existing indexed data remains compatible.

Before changing embeddings, vector dimensions, collection structure, or
metadata, consider the impact on existing Qdrant data.

## Important rule

The RAG laboratory should remain something a developer can inspect and
understand from beginning to end.

Prefer:

**Understand → Build → Inspect → Experiment → Improve**

over:

**Abstract → Hide → Optimize**
