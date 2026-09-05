# Talk to Ollama from programs

The chat prompt is for you. Programs use the HTTP server underneath it, and that server speaks two
dialects: Ollama's own API and an OpenAI-compatible one. The second matters most, because it is the
request shape the whole course already uses (diagram D52).

## Ollama's native API

Two endpoints do most of the work. `/api/generate` takes a single prompt:

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "gemma3:4b",
  "prompt": "Why is the sky blue? One sentence.",
  "stream": false
}'
```

`/api/chat` takes a message list with roles, exactly like the `chat()` helper in Day 1:

```bash
curl http://localhost:11434/api/chat -d '{
  "model": "gemma3:4b",
  "messages": [
    {"role": "system", "content": "You are terse."},
    {"role": "user", "content": "Name one use of a tokenizer."}
  ],
  "stream": false
}'
```

With `"stream": false` you get one JSON object back, with the reply under `message.content` and
token counts under `prompt_eval_count` (input) and `eval_count` (output). Without it, the server
streams one JSON line per token, which is how the terminal prompt shows words as they arrive.

On Windows, PowerShell's `curl` is not curl. Either call `curl.exe`, or use PowerShell's own
request cmdlet:

```powershell
$body = @{ model = "gemma3:4b"; prompt = "Why is the sky blue? One sentence."; stream = $false } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:11434/api/generate -Method Post -Body $body -ContentType "application/json"
```

## The OpenAI-compatible endpoint

The server also answers at `/v1/...` in the format that the OpenAI SDK, OpenRouter and most tools
expect:

```bash
curl http://localhost:11434/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ollama" \
  -d '{
    "model": "gemma3:4b",
    "messages": [{"role": "user", "content": "Say hello in five words."}]
  }'
```

The API key can be any non-empty string; Ollama ignores it, but SDKs refuse to send a request
without one.

This is the point of the chapter. Every course notebook creates its model client with a base URL and
a model name. Pointing it at Ollama is two changed strings:

```python
from openai import OpenAI

client = OpenAI(base_url="http://localhost:11434/v1", api_key="ollama")   # was OpenRouter
reply = client.chat.completions.create(
    model="gemma3:4b",                                                     # was openai/gpt-oss-120b
    messages=[{"role": "user", "content": "Say hello in five words."}],
)
print(reply.choices[0].message.content)
```

The same substitution works in LangChain (`ChatOpenAI(base_url=..., model="gemma3:4b")`), in n8n
(the *Ollama Chat Model* node, or the OpenAI node with a custom base URL when self-hosting), and in
most agent frameworks. Tool calling works with Gemma 3 through this endpoint, although a 4B model
chooses tools less reliably than the hosted models the course uses; expect to add a retry.

One limitation: Google Colab runs in the cloud and cannot reach `localhost` on your laptop. The
Ollama route is for running the course code on your own machine.

## The Python package

If you would rather not go through the OpenAI shape, `pip install ollama` gives a thin client over
the native API:

```python
import ollama
response = ollama.chat(model="gemma3:4b", messages=[{"role": "user", "content": "Hi"}])
print(response["message"]["content"])
```

## Recap

- The server speaks Ollama's native `/api/chat` and an OpenAI-compatible `/v1/chat/completions`.
- Any OpenAI-style client works by changing the base URL to `http://localhost:11434/v1` and the model name to your tag.
- Colab cannot see your laptop; use the local route when running course code locally.
