# Requirements – Local RAG Chatbot

## 1. Project Purpose

The Local RAG Chatbot is a practical learning project designed to understand and demonstrate the basic concepts of Retrieval-Augmented Generation (RAG).

The project combines Python, Streamlit, Ollama, Qdrant, and Docker Compose in a small, fully local application.

The main objective is not to build a production-ready system, but to gain hands-on experience with the individual components and understand how they work together.

The implementation should remain simple, transparent, and easy to maintain.

---

## 2. Learning Objectives

The project should provide practical experience in the following areas:

- Understanding the RAG architecture and data flow.
- Processing documents with Python.
- Extracting and splitting text into chunks.
- Generating embeddings with a local model.
- Storing and searching vectors in Qdrant.
- Understanding similarity search and retrieval results.
- Building prompts from retrieved context.
- Generating answers with a local LLM through Ollama.
- Developing a graphical interface with Streamlit.
- Running and connecting services with Docker Compose.
- Testing individual components and the complete RAG pipeline.
- Understanding the advantages and limitations of local AI models.

The code should be written in a beginner-friendly style, with clear responsibilities, meaningful comments, and straightforward logic.

---

## 3. Functional Requirements

### FR-01: Local Application

The application must run locally without external AI APIs.

All document processing, embedding generation, vector search, and answer generation must use the local environment.

### FR-02: Document Support

The initial version must support:

- PDF
- TXT
- Markdown

Additional formats are not required for the first implementation.

### FR-03: Document Ingestion

The application must be able to:

1. Read documents from a local directory or through the Streamlit upload interface.
2. Extract and normalize their text.
3. Split the text into smaller chunks.
4. Generate embeddings.
5. Store the chunks, vectors, and basic metadata in Qdrant.

A simple full re-indexing process is sufficient for the initial version.

### FR-04: Question Answering

Users must be able to enter questions through the Streamlit interface.

The application must:

1. Generate an embedding for the question.
2. Search Qdrant for relevant chunks.
3. Build a context from the retrieved results.
4. Construct a prompt containing the context and question.
5. Send the prompt to the local Ollama model.
6. Display the generated answer.

### FR-05: Source References

The chatbot must display the source documents used to generate an answer.

Where practical, the interface should also show the relevant chunk information.

### FR-06: Chatbot Interface

The Streamlit application must provide a simple chatbot interface.

It should include:

- Document upload
- Basic indexing status
- Question input
- Answer display
- Source references
- A small conversation history

A simple session-based chat history is sufficient.

### FR-07: Debug Interface

The application must provide a separate debug tab for learning and troubleshooting.

The debug interface should display the main processing steps:

- User question
- Retrieved chunks
- Similarity scores
- Source metadata
- Assembled context
- Final prompt
- Generated answer

The debug interface must use the same RAG processing logic as the chatbot tab.

### FR-08: Containerized Environment

The application must be startable using Docker Compose.

The environment must include:

- Streamlit
- Ollama
- Qdrant

The document ingestion process may be executed as an on-demand command rather than a permanently running service.

### FR-09: Data Persistence

Ollama models and Qdrant data must persist across container restarts.

The application must not require models to be downloaded or documents to be indexed again after every restart.

### FR-10: Error Handling

The application should provide understandable error messages for common problems, such as:

- Unsupported document formats
- Empty documents
- Failed document extraction
- Ollama not available
- Qdrant not available
- Missing or invalid configuration

Error handling should remain simple and appropriate for a learning project.

---

## 4. Non-Functional Requirements

### NFR-01: Simplicity

The implementation should favor readable and understandable code over complex abstractions.

Only functionality required for the learning objectives and initial demo should be implemented.

### NFR-02: Modularity

The Python code should separate the main responsibilities of document processing, embeddings, vector storage, retrieval, prompt construction, and generation.

The modules should remain small and easy to test.

### NFR-03: Resource Efficiency

The application must be suitable for testing in a Linux virtual machine running under VirtualBox.

The initial setup should use CPU-based inference and a small, quantized language model.

The final model selection must be based on practical tests of memory consumption, response time, and answer quality.

### NFR-04: Reproducibility

The environment should be reproducible through Docker Compose and documented configuration.

### NFR-05: Privacy

Documents and questions must remain within the local environment.

No external AI services are required.

### NFR-06: Testability

Individual Python modules should be testable independently.

The complete application must also be tested with a small set of sample documents and questions.

### NFR-07: Documentation

The project must document:

- Architecture
- Requirements
- Implementation steps
- Setup and startup instructions
- Basic usage
- Important technical decisions

The documentation should support learning and make the project understandable to other developers.

---

## 5. Out of Scope

The following features are explicitly excluded from the initial version:

- Production deployment
- Multi-user support
- User authentication and authorization
- High availability
- Distributed processing
- Automatic incremental indexing
- Automatic detection and removal of deleted documents
- Persistent conversation history
- OCR for scanned documents
- Advanced retrieval strategies
- Reranking
- Complex evaluation frameworks
- Integration with external AI APIs
- Kubernetes deployment

These features may be considered in future iterations if they provide a clear learning benefit.

---

## 6. Acceptance Criteria

The initial version is considered complete when:

- [ ] The application starts successfully using Docker Compose.
- [ ] Streamlit provides both the Chatbot and Debug Chatbot tabs.
- [ ] Ollama runs a locally available chat model.
- [ ] Qdrant stores document embeddings and metadata.
- [ ] At least one supported document can be indexed.
- [ ] A user can ask a question about the indexed document.
- [ ] The chatbot generates an answer using retrieved context.
- [ ] The answer displays its source document.
- [ ] The debug tab displays the main RAG processing steps.
- [ ] The application works without external AI APIs.
- [ ] Models and vector data persist after container restarts.
- [ ] The core Python modules have basic tests.
- [ ] Setup and usage instructions are documented.

---

## 7. Learning Approach

The implementation will follow a step-by-step approach.

Each module will be introduced with a short explanation of its purpose and its place in the RAG pipeline.

The preferred workflow is:

1. Understand the component.
2. Implement a minimal working version.
3. Test the component independently.
4. Integrate it into the application.
5. Review the result and discuss possible improvements.

The project should prioritize understanding the underlying technology over rapid implementation or feature completeness.

---

## 8. Summary

The Local RAG Chatbot is a small, fully local learning project.

It demonstrates the fundamental RAG workflow using Python, Streamlit, Ollama, Qdrant, and Docker Compose.

The initial implementation focuses on document ingestion, vector search, context construction, and local answer generation.

The scope is intentionally limited to keep the project manageable, understandable, and suitable for hands-on learning and technical demonstrations.
