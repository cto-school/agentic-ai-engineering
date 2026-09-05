# Inference under the hood

Training happens once. Inference, running the finished model to answer a request, happens billions
of times a day, and its mechanics explain the prices, the latencies and the odd corners of every API
in this course (diagram D63).

## Prefill and decode

One request has two phases:

1. **Prefill.** The whole prompt (system message, history, tool schemas, your question) goes
   through the model in a single pass. All tokens are processed at once, in parallel, which GPUs
   are good at. The output is the first token and, more importantly, the internal state for every
   prompt token.
2. **Decode.** One token per pass, as in chapter F3. Each pass processes only the newest token,
   but must attend to everything before it. The passes are sequential; nothing can be parallelised
   across them.

Prefill is measured in *time to first token*; decode in *tokens per second*. This is why a
provider charges less per input token than per output token (often by a factor of three to five):
prefill is cheap parallel work, decode is expensive serial work. Long prompts are affordable; long
answers are not.

## The KV cache

During decode, attention at every layer needs the keys and values of all earlier tokens (chapter
F2). Recomputing them for every new token would make each pass as expensive as prefill. Instead they
are stored: the **KV cache**. It is the working memory of a running request.

Its size is the reason context windows cost RAM: for a 7B model, the cache is about half a
megabyte per token, so a 32,000-token context needs 16 GB before the weights are counted. Ollama's
`num_ctx` sets how much cache to reserve, which is why raising it can make a model that fitted stop
fitting. Providers that offer **prompt caching** are letting you reuse a prefill's KV cache across
requests that start with the same tokens, which is why a long fixed system prompt can be made cheap.

## Serving many users: batching

A single request uses a sliver of a GPU. Servers run dozens to hundreds of requests at once,
interleaving their decode steps into one big matrix multiplication per pass (continuous batching).
Your tokens per second depends on how busy the server is, and a request that arrives during a
burst waits in a queue: that is the variability you see in latency, and the rate limits are the
server protecting its batches.

## Quantisation, again

The weights are stored as 16-bit numbers in training. For inference they are rounded to 8 or 4
bits (chapter O1 of the Ollama module). Memory falls by two to four times, and because decode is
limited by how fast weights can be read from memory rather than by arithmetic, speed rises almost
as much. The quality cost is small for 8-bit and noticeable but acceptable for 4-bit; below that it
grows quickly. Quantisation-aware training (Gemma's `-qat` tags) reduces the cost by training with
the rounding in the loop.

## What a tool call really is

Nothing in the Transformer runs functions. A tool call is a **format**. The host (your code, or
LangChain, or n8n) writes the tool schemas into the prompt in the layout the model was post-trained
on; the model, when it decides to use a tool, emits a special token followed by the tool name and
JSON arguments, then an end token. The host parses that text, runs the function, appends the result
as a new tool message, and calls the model again. The model never waits for anything; every call is
still prompt in, tokens out.

Two consequences for the course:

- Day 1's manual loop is not a simplification of "real" tool calling; it *is* tool calling. The
  frameworks hide the parsing.
- A model can produce a malformed call, a call to a tool that does not exist, or arguments that
  violate the schema, because it is generating text. Validation on the host side (Day 1 and the
  LangGraph track's tool design section) is not optional.

## What structured output really is

Two mechanisms, and providers use one or both:

- **Training and prompting**: the model was post-trained to produce JSON when asked, and you
  supply the schema in the prompt. Usually works; sometimes does not.
- **Constrained decoding**: at every decode step, the server masks out every token that would make
  the output invalid under the schema, before sampling. The model literally cannot produce a
  wrong bracket. This is what "strict" JSON modes do, and it is why they can guarantee shape but
  not correctness of the values.

## Streaming

Because decode produces one token at a time, the server can send each one as it appears. Streaming
is not a special mode of the model; it is the server not waiting until the end token. The token
counts in the final usage message are the same either way.

## Recap

- Prefill processes the prompt in parallel and is cheap; decode produces one token per sequential pass and is expensive, hence input tokens cost less than output tokens.
- The KV cache stores attention state per token, sets the memory cost of context, and is what prompt caching reuses.
- Tool calls and structured output are text formats produced by the model and parsed or constrained by the host; the model never runs anything.
