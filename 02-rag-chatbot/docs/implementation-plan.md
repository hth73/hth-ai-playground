# Implementation Plan - Local RAG Chatbot

## 1. Objective

This implementation plan describes the development steps for the Local RAG Chatbot learning project.

The goal is to build a small, fully local RAG application while understanding the individual components and their interaction.

The implementation follows a step-by-step approach:

1. Understand the component.
2. Implement a minimal working version.
3. Test the component.
4. Integrate it into the application.
5. Document important findings.

The project prioritizes learning and readability over complexity or feature completeness.

---

## 2. Development Environment

### 2.1 Host System

The application will initially run directly on the Linux host.

Docker Compose is used to manage the application containers.

A separate VirtualBox environment is not required for the initial implementation.

### 2.2 Main Technologies

| Technology | Purpose |
|---|---|
| Python | RAG implementation |
| Streamlit | Graphical user interface |
| Ollama | Local LLM and embedding inference |
| Qdrant | Vector database |
| Docker Compose | Container orchestration |
| pytest | Automated tests |

### 2.3 Resource Considerations

The initial setup uses CPU-based inference.

A small quantized chat model will be selected and tested before larger models are considered.

The embedding model and chat model are evaluated separately.

Memory consumption, response time, and answer quality are considered during model selection.

---

## 3. Implementation Phases

### Phase 0 – Project Structure and Documentation

**Objective:** Establish a clear foundation before coding.

Tasks:

- [x] Create the project directory structure.
- [x] Document the system architecture.
- [x] Define the project requirements.
- [ ] Finalize the implementation plan.
- [ ] Review the documentation for consistency.

**Result:** A documented project structure with clearly defined scope and goals.

---

### Phase 1 – Review Existing RAG Implementation

**Objective:** Understand which parts of `01-rag` can be reused.

Tasks:

- Review the existing document loader.
- Review text extraction and chunking.
- Review embedding generation.
- Review Qdrant integration.
- Review retrieval and prompt construction.
- Identify code suitable for reuse.
- Copy and adapt selected modules into `02-rag-chatbot`.

The original `01-rag` project remains unchanged.

No runtime dependencies between the two projects are introduced.

**Result:** A small set of reusable Python modules and a clear understanding of their responsibilities.

---

### Phase 2 – Local Docker Environment

**Objective:** Start the required services locally.

Tasks:

- Create the Docker Compose configuration.
- Configure the Ollama container.
- Configure the Qdrant container.
- Configure persistent volumes.
- Configure the Docker network.
- Verify connectivity between services.
- Download and test a small chat model.
- Download and test an embedding model.

Initial services:

- Ollama
- Qdrant

Streamlit will be added when the application interface is introduced.

**Result:** Ollama and Qdrant are running locally and can communicate with the Python environment.

---

### Phase 3 – Document Processing

**Objective:** Read documents and prepare their content for indexing.

Tasks:

- Implement document loading.
- Support PDF, TXT, and Markdown.
- Extract and normalize text.
- Implement basic text chunking.
- Generate document and chunk identifiers.
- Handle empty or unsupported documents.
- Test the processing logic with sample files.

**Result:** Documents can be converted into manageable text chunks.

---

### Phase 4 – Embeddings and Vector Storage

**Objective:** Store document embeddings in Qdrant.

Tasks:

- Implement embedding generation through Ollama.
- Generate embeddings for document chunks.
- Create an independent Qdrant collection.
- Store vectors, text, and metadata.
- Verify collection configuration.
- Test vector insertion and retrieval.

**Result:** Document chunks are stored in Qdrant and can be retrieved through similarity search.

---

### Phase 5 – Retrieval and Prompt Construction

**Objective:** Build the core RAG query pipeline.

Tasks:

- Generate embeddings for user questions.
- Implement similarity search.
- Retrieve the most relevant chunks.
- Build a context from retrieved results.
- Construct a prompt containing the context and question.
- Include source information in the processing results.
- Test retrieval and prompt construction independently.

**Result:** A user question can retrieve relevant document content and produce a complete prompt.

---

### Phase 6 – Local Answer Generation

**Objective:** Generate answers using Ollama.

Tasks:

- Implement the Ollama generation client.
- Send the constructed prompt to the local chat model.
- Process the generated response.
- Return the answer and source references.
- Handle connection errors and missing models.
- Test the complete RAG pipeline from question to answer.

**Result:** The system can answer questions based on indexed documents.

---

### Phase 7 – Streamlit User Interface

**Objective:** Provide a graphical interface for the RAG application.

Tasks:

- Create the main Streamlit application.
- Implement the Chatbot tab.
- Implement the Debug Chatbot tab.
- Connect both tabs to the shared RAG Engine.
- Add document upload.
- Display indexing status.
- Add question input and answer display.
- Display source references.
- Display retrieved chunks and similarity scores in the debug view.
- Display the assembled context and final prompt.
- Add a small session-based chat history.

**Result:** A working graphical application with a user-friendly and a technical view.

---

### Phase 8 – Integration and Demo Preparation

**Objective:** Verify the complete application and prepare a reproducible demonstration.

Tasks:

- Test the complete Docker Compose environment.
- Verify persistence after container restarts.
- Test document upload and indexing.
- Test question answering.
- Verify source references.
- Verify debug information.
- Run the automated tests.
- Document startup and usage instructions.
- Prepare a small set of demonstration documents and questions.

**Result:** A functional local RAG chatbot suitable for learning and technical demonstrations.

---

## 4. Testing Strategy

Testing is performed throughout the implementation rather than only at the end.

### Unit Tests

Individual Python modules are tested independently.

Examples:

- Document loading
- Text splitting
- Metadata creation
- Context construction
- Prompt construction

### Integration Tests

Integration tests verify communication between components.

Examples:

- Python to Ollama
- Python to Qdrant
- Embedding generation and vector insertion
- Retrieval and context construction
- Complete question-answering pipeline

### Manual Tests

The graphical interface is tested manually.

Examples:

- Uploading documents
- Starting indexing
- Asking questions
- Reviewing answers and sources
- Inspecting the debug tab
- Restarting containers and verifying persisted data

---

## 5. Definition of Done

The initial learning project is complete when:

- The Docker Compose environment starts successfully.
- Ollama and Qdrant are available locally.
- Documents can be loaded and indexed.
- Embeddings are stored in Qdrant.
- Relevant chunks can be retrieved for a question.
- Ollama generates an answer using the retrieved context.
- The Streamlit chatbot displays answers and sources.
- The debug tab exposes the main RAG processing steps.
- Data persists across container restarts.
- Basic automated tests pass.
- The application can be demonstrated using documented startup instructions.

---

## 6. Future Extensions

Potential extensions are evaluated only after the initial version works.

Examples:

- Additional document formats
- Incremental indexing
- Improved retrieval strategies
- Reranking
- Persistent chat history
- Comparison with LlamaIndex
- GPU acceleration

These extensions are not prerequisites for completing the learning project.

---

## 7. Summary

The implementation follows a modular and incremental approach.

Each component is introduced, implemented, and tested before the next component is added.

The initial focus is a small, fully local RAG chatbot that demonstrates the complete workflow from document ingestion to answer generation.

The project remains intentionally simple to support learning, experimentation, and technical understanding.
