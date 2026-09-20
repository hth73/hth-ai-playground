---
description: "Python-specific guidance for experiments, scripts, utilities, and AI prototypes."
applyTo: "**/*.py, **/*.ipynb"
---

# Python Instructions

## General principles

- Prefer readable and explicit Python code.
- Keep functions small and focused on one responsibility.
- Use descriptive names for variables, functions, classes, and modules.
- Prefer simple solutions over unnecessary abstractions.
- Keep the data flow visible, especially in educational experiments.
- Do not introduce a framework or library unless it provides meaningful value.
- Preserve existing working code when making small changes.
- Avoid refactoring educational code merely for stylistic reasons.
- Prefer understandable code over clever or overly compact code.
- Keep the implementation proportional to the size and purpose of the experiment.

## Code structure

Prefer clear and linear code when it helps explain the underlying concept.

For example:

```text
input
  ↓
process
  ↓
transform
  ↓
output
```

When a pipeline contains multiple conceptual stages, keep those stages visible in the code.

Use functions when they improve readability or isolate a meaningful piece of functionality.

Do not split simple educational code into excessive numbers of modules, classes, or helper functions.

Avoid introducing classes when a simple function or straightforward procedural implementation is easier to understand.

When a script represents a learning experiment, keep the main execution flow easy to follow from top to bottom.

## Naming

Use descriptive names that explain the purpose of the value or operation.

Prefer:

```python
query_embedding
document_chunks
similarity_scores
manual_retriever
build_context()
```

over:

```python
q
data
tmp
x
helper()
```

Use:

- `snake_case` for variables and functions
- `PascalCase` for classes
- descriptive module names
- meaningful constant names

Avoid unnecessary abbreviations.

Names should describe the concept being demonstrated, especially in educational code.

## Functions

Functions should generally have one clear responsibility.

Prefer:

```python
def chunk_documents(documents):
    ...
```

over functions that perform unrelated tasks such as loading files, splitting text, creating embeddings, storing vectors, calling the LLM, and displaying Streamlit output all in one function.

However, do not create excessive helper functions merely to make a file appear more modular.

For small educational examples, a clear linear implementation can be preferable to many tiny functions.

## Type hints

Use type hints when they improve readability or make interfaces clearer.

Do not introduce complex typing constructs merely to satisfy static analysis in a small educational experiment.

Prefer understandable types over overly sophisticated generic types.

Example:

```python
def build_context(chunks: list[str]) -> str:
    ...
```

Do not add elaborate type abstractions when they provide no practical benefit to the experiment.

## Comments and docstrings

Comments should explain why something is done when the reason is not obvious from the code.

For educational code, comments may additionally explain an important technical concept.

Prefer:

```python
# Generate a new embedding for the user's question.
# This vector is compared with the document vectors stored in Qdrant.
query_vector = embeddings.embed_query(question)
```

over:

```python
# Generate embedding
query_vector = embeddings.embed_query(question)
```

Do not write comments that simply repeat what the code already says.

Use docstrings for functions or classes when they clarify purpose, parameters, return values, or important behavior.

## Error handling

Handle expected errors explicitly.

Error messages should explain:

- what failed
- why it may have failed
- what the user can do about it

For Streamlit applications, prefer a clean user-facing error message over exposing an unnecessary Python traceback.

Example:

```python
try:
    connect_to_service()
except Exception:
    st.error(
        "The service is not available. "
        "Please check whether the required container is running."
    )
    st.stop()
```

Do not silently ignore unexpected errors.

Avoid overly broad exception handling when a more specific exception can reasonably be used.

## Configuration

Keep configuration explicit and easy to understand.

Use environment variables for:

- API keys
- passwords
- tokens
- other sensitive configuration

Example:

```python
import os

api_key = os.getenv("OPENAI_API_KEY")
```

Do not hard-code credentials in Python source files.

Do not print secrets during debugging.

Configuration that is not sensitive may remain visible in the code when doing so improves the educational value of the experiment.

## AI and API usage

When working with AI APIs:

- Keep model configuration explicit.
- Keep prompts visible where educationally useful.
- Keep API calls easy to identify in the code.
- Document important model choices when appropriate.
- Make it clear which data is sent to an external service.
- Never expose API keys or other credentials.

Prefer explicit configuration such as:

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.3,
)
```

over hiding important model parameters in unnecessary configuration layers.

When experimenting with different models, keep the model choice easy to change.

## Data flow

When implementing a data-processing or AI pipeline, keep the movement of data visible.

For example:

```text
document
   ↓
text extraction
   ↓
chunks
   ↓
embeddings
   ↓
vector store
   ↓
retrieval
   ↓
context
   ↓
LLM
   ↓
response
```

Use variable names that reflect these stages.

Avoid passing large amounts of unrelated state through generic objects or dictionaries when more explicit structures would make the code easier to understand.

## Dependencies

Before introducing a dependency:

1. Check whether the Python standard library is sufficient.
2. Check whether an existing project dependency already provides the required capability.
3. Consider whether the dependency helps the learning objective.
4. Prefer a simple implementation when it makes the underlying concept easier to understand.

Do not introduce a library merely to replace a few understandable lines of Python.

When a library is required, keep its purpose clear.

## Frameworks

Frameworks such as Streamlit, LangChain, Qdrant clients, or OpenAI libraries may be used when they are relevant to the experiment.

However, do not hide important learning concepts behind framework abstractions.

For example, if the purpose is to understand vector similarity, keep the similarity calculation visible before replacing it with a higher-level abstraction.

If the purpose is to understand Qdrant, keep the interaction with Qdrant understandable instead of hiding it behind unnecessary wrapper classes.

## Educational implementations

This repository contains learning experiments.

If an implementation intentionally demonstrates a concept manually, preserve that implementation.

Do not automatically replace:

- manual calculations
- intermediate variables
- debug output
- educational comments
- explicit pipeline stages
- simple reference implementations

with shorter framework-based alternatives.

The shortest implementation is not necessarily the best implementation for this repository.

## Existing code

When modifying existing Python code:

1. Understand the current implementation.
2. Identify the purpose of the existing code.
3. Preserve working behavior unless a change is required.
4. Make the smallest useful change.
5. Avoid unrelated cleanup.
6. Avoid changing the architecture without a clear reason.
7. Explain significant changes when appropriate.

Do not rewrite an entire educational script when a small targeted change is sufficient.

Do not remove working code merely because another implementation is shorter or more elegant.

## Refactoring

Refactor when it provides a clear benefit such as:

- fixing a bug
- improving readability
- removing actual duplication
- making an important concept easier to understand
- separating clearly unrelated responsibilities
- improving maintainability of code that is no longer experimental

Do not refactor solely because:

- a framework offers a shorter solution
- a different coding style is preferred
- a linter suggests a stylistic change
- the code could theoretically be more abstract

For educational code, preserving the learning value takes priority over maximum abstraction or minimal line count.

## Notebooks

Jupyter notebooks may be used for exploration and experiments.

Keep notebook cells logically structured.

Prefer a progression such as:

```text
1. Imports
2. Configuration
3. Input data
4. Processing
5. Intermediate results
6. Visualization or inspection
7. Conclusion
```

Avoid hiding important setup or processing inside large opaque cells.

When moving stable notebook code into a Python module, preserve the conceptual structure where practical.

## Reproducibility

Experiments should be reproducible where reasonably possible.

Document:

- required dependencies
- required services
- important environment variables
- required files or sample data
- relevant configuration
- commands needed to run the experiment

Avoid relying on undocumented local state.

If an experiment intentionally depends on a local service such as Qdrant, Docker, or Ollama, document that dependency.

## Output and debugging

During development, intermediate output can be useful for understanding the behavior of an experiment.

Examples include:

```text
number of documents
number of chunks
embedding dimensions
retrieved chunks
similarity scores
generated context
```

Do not remove useful educational output merely to make the code shorter.

However, never expose:

- API keys
- passwords
- access tokens
- private credentials
- sensitive document content

in logs or screenshots.

## Streamlit applications

When Python code is used with Streamlit:

- Keep the user interface readable.
- Prefer `st.error()` or `st.warning()` for expected user-facing errors.
- Use `st.info()` for guidance and expected prerequisites.
- Keep important intermediate RAG results visible when the purpose is educational.
- Avoid displaying raw Python tracebacks to users when a clear UI message is sufficient.
- Be aware that Streamlit reruns the script when the user interacts with the interface.

Do not introduce complex state-management abstractions unless they are actually required.

## Experimental code

Experimental code is allowed to be imperfect.

Do not automatically turn every experiment into production-quality software.

However:

- experimental limitations should be documented
- temporary assumptions should be visible
- dependencies should be understandable
- reproducibility should be maintained where practical
- potentially misleading shortcuts should be identified

The goal is to understand the technology, not to create a perfect production framework.

## Important rule

When there is a conflict between:

1. maximum abstraction
2. minimum number of lines
3. educational clarity

prefer educational clarity.

This repository is a laboratory.

The code should remain understandable to a developer who wants to learn how the underlying technology works.

