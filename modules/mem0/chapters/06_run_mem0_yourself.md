# Run Mem0 yourself: the library with Ollama, the server, and MCP

The Platform is the quickest start. Three reasons to run Mem0 on your own machine instead: the
data must not leave it, you want zero cost for experiments, or you want to see the moving parts.
This chapter does all three, and none of them needs a cloud account (diagram D69).

## Option 1: the open-source library in your process

```bash
pip install mem0ai
```

With no configuration, `Memory()` uses OpenAI for extraction (`gpt-5-mini`) and embeddings
(`text-embedding-3-small`), a Qdrant vector store written to disk under `/tmp/qdrant`, and a SQLite
history file at `~/.mem0/history.db`. That needs an `OPENAI_API_KEY`. To run entirely locally,
point both the model and the embedder at Ollama.

Pull an embedding model next to the Gemma model from the Ollama module:

```bash
ollama pull nomic-embed-text
ollama pull gemma3:4b
```

Then configure:

```python
from mem0 import Memory

config = {
    "llm": {
        "provider": "ollama",
        "config": {"model": "gemma3:4b", "temperature": 0.1, "max_tokens": 2000,
                   "ollama_base_url": "http://localhost:11434"},
    },
    "embedder": {
        "provider": "ollama",
        "config": {"model": "nomic-embed-text", "embedding_dims": 768,
                   "ollama_base_url": "http://localhost:11434"},
    },
    "vector_store": {
        "provider": "qdrant",
        "config": {"collection_name": "course_memories", "path": "./mem0_qdrant",
                   "embedding_model_dims": 768},
    },
}
memory = Memory.from_config(config)

memory.add([{"role": "user", "content": "I'm Asha, vegetarian, and I prefer meetings after 10:00."}],
           user_id="course_fictional_asha")
print(memory.search("What does Asha eat?", filters={"user_id": "course_fictional_asha"}))
```

The API is the same as the client's: `add`, `search`, `get_all`, `get`, `update`, `delete`,
`delete_all`, `history`. Two differences to expect:

- **Extraction quality follows the model.** A 4B model extracts facts less reliably than the
  Platform's; expect an occasional missed or clumsy fact, and read the results. Custom prompts exist
  for this (`custom_fact_extraction_prompt` in the config) if you want to tune it.
- **Retrieval is vector similarity plus entity overlap**, without the Platform's keyword and
  temporal signals or its reranker (a reranker can be configured separately).

Everything is on disk in the two paths above; delete the folder and the file to start clean. The
dimension numbers must agree: `nomic-embed-text` produces 768-dimensional vectors, so both the
embedder and the vector store say 768. A mismatch is the most common first error.

Supported providers, if you want others: LLMs `openai`, `anthropic`, `gemini`, `groq`, `ollama`,
`aws_bedrock`, `azure_openai`, `litellm`; embedders `openai`, `gemini`, `azure_openai`, `ollama`,
`huggingface`, `vertexai`, `aws_bedrock`; vector stores `qdrant`, `pgvector`, `chroma`, `pinecone`,
`redis`, `weaviate`, `milvus`, `elasticsearch`. Using Gemini for extraction with local Qdrant is a
good middle path: better facts, still your disk.

## Option 2: the self-hosted server with a dashboard

The open-source repository ships the same REST API shape as the Platform plus a web dashboard, as a
Docker Compose stack with PostgreSQL and pgvector.

```bash
git clone https://github.com/mem0ai/mem0.git
cd mem0/server
cp .env.example .env          # set OPENAI_API_KEY (or ANTHROPIC_API_KEY / GOOGLE_API_KEY) and JWT_SECRET
make bootstrap                # builds, starts, runs migrations, creates the admin and prints an API key
```

Generate `JWT_SECRET` with `openssl rand -base64 48`. When it is up:

| Component | Address |
|---|---|
| REST API | `http://localhost:8888` |
| dashboard | `http://localhost:3000` (setup wizard on first run) |

`make bootstrap` prints an API key starting `m0sk_`; the dashboard's setup wizard shows it once too.
Clients send it as an `X-API-Key` header, and the endpoints mirror the Platform's, so the n8n
recipe from chapter M4 works against your own server by changing the URL and the header. On the
OpenClaw module's EC2 machine this stack runs comfortably on a `t3.medium`; keep port 8888 and 3000
closed in the security group and reach them through an SSH tunnel.

`make up` starts the stack without creating an admin, for the browser-first route.

## Option 3: Mem0 over MCP, for coding tools

Mem0 also serves its memory to tools that speak the Model Context Protocol, which the course meets
in Day 5 and the LangGraph track. The hosted server is `https://mcp.mem0.ai/mcp`; a client
configuration for Cursor, and the same shape for Claude Code, Windsurf, VS Code and others, is:

```json
{
  "mcpServers": {
    "mem0-mcp": { "type": "http", "url": "https://mcp.mem0.ai/mcp" }
  }
}
```

The first tool use opens a browser sign-in, or you send your API key as a bearer token. The tools
exposed are the operations from this module by other names: `add_memory`, `search_memories`,
`get_memories`, `get_memory`, `update_memory`, `delete_memory`, `delete_all_memories`, plus entity
and event management. An agent given these tools decides for itself when to remember, which is the
tool-based design chapter M4 mentioned.

## Which option when

| Situation | Choose |
|---|---|
| learning, experiments, no data leaves the laptop | library with Ollama |
| a product with many users and no infrastructure team | Platform |
| a team that needs the dashboard and API on its own servers | self-hosted server |
| giving a coding assistant memory across sessions | MCP |

## Recap

- `Memory.from_config` with `ollama` as both LLM and embedder, and a Qdrant store on disk, runs the whole layer locally; keep embedding dimensions consistent (768 for nomic-embed-text).
- `make bootstrap` in the repository's `server/` folder starts the REST API on 8888 and the dashboard on 3000 with PostgreSQL and pgvector.
- `https://mcp.mem0.ai/mcp` exposes add, search, get, update and delete as MCP tools to coding assistants.
