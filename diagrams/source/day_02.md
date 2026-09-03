# Day 2 diagram sources

## D06 — Document ingestion pipeline

```mermaid
flowchart LR
    D["Course documents"] --> P["Parse headings and text"]
    P --> C["Create inspectable chunks"]
    C --> E["Create embeddings"]
    E --> I["Vector index"]
    C --> K["Keyword index"]
```

## D07 — RAG query pipeline

```mermaid
flowchart LR
    Q["Question"] --> R["Retriever"]
    I[("Indexed chunks")] --> R
    R --> S["Top chunks + scores"]
    S --> G["Grounded generation"]
    Q --> G
    G --> A{"Evidence sufficient?"}
    A -->|"yes"| C["Answer + citations"]
    A -->|"no"| N["Abstain"]
```

Text alternative: retrieval chooses evidence before generation; insufficient evidence produces abstention.
