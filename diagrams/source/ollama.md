# Ollama module diagram sources

## D50 — Ollama on a laptop

```mermaid
flowchart LR
    T["Terminal: ollama run"] -->|"HTTP on port 11434"| S["Ollama server"]
    P["Your program or notebook"] -->|"HTTP on port 11434"| S
    S --> R["Runner built on llama.cpp"]
    R -->|"loads once, keeps in RAM"| W["GGUF file: weights + tokenizer + chat template"]
    R -->|"tokens"| S
```

Text alternative: the terminal command and any program are clients that send HTTP requests to the Ollama server on port 11434; the server hands the request to a runner built on llama.cpp, which loads the quantised GGUF file into RAM once and streams tokens back.

## D51 — Choosing a Gemma 3 size for the machine

```mermaid
flowchart TD
    A["How much RAM?"] --> B{"8 GB"}
    A --> C{"16 GB"}
    A --> D{"32 GB or more"}
    B -->|"start here"| E["gemma3:1b"]
    B -->|"with other apps closed"| F["gemma3:4b"]
    C --> F
    D --> F
    D -->|"quality over speed"| G["gemma3:12b"]
```

Text alternative: the decision starts from the laptop's RAM; 8 GB points to gemma3:1b with 4b as a later experiment, 16 GB to gemma3:4b, and 32 GB or more to 4b or 12b depending on whether speed or quality matters.

## D52 — Programs talking to the local server

```mermaid
flowchart LR
    N["OpenAI-style client: base_url localhost:11434/v1"] -->|"/v1/chat/completions"| S["Ollama server"]
    C["curl or ollama package"] -->|"/api/chat"| S
    S --> M["gemma3:4b"]
    M -->|"reply + token counts"| S
```

Text alternative: an OpenAI-style client, such as the course's chat helper with its base URL changed, reaches the model through the compatible /v1 endpoint, while curl or the ollama package use the native /api/chat endpoint; both end at the same local model, which returns the reply and token counts.
