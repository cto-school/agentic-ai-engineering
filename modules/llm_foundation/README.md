# LLM Foundation module — How a large language model is built and how it works

**Outcome:** a working mental model of a large language model: how text becomes tokens and
vectors, what the Transformer does with them, how the next word is chosen, how a model is
pretrained and then post-trained into an assistant, what happens at inference time, and where the
limits come from. No code is required; two chapters carry an in-browser simulation you can play
with (a tokenizer you train yourself, and a next-token predictor with a temperature slider).

The module is independent of the five days and the tracks, and it is the one to read when a term
from the rest of the course (token, context window, temperature, hallucination, tool call) feels
like a black box.

| Chapter | File | Question it answers | Simulation |
|---|---|---|---|
| F1 | `01_from_text_to_tokens.md` | What does the model actually receive? | train a byte-pair tokenizer and tokenize your own text |
| F2 | `02_inside_the_transformer.md` | What happens between input and output? | |
| F3 | `03_predicting_the_next_token.md` | How is one word chosen, and what do temperature and top-p do? | a next-token predictor with a temperature slider |
| F4 | `04_pretraining.md` | Where do the billions of weights come from? | |
| F5 | `05_post_training.md` | How does a text-completer become an assistant that follows instructions? | |
| F6 | `06_inference_under_the_hood.md` | Why is input cheaper than output, what is a KV cache, how do tool calls really work? | |
| F7 | `07_limits_and_what_it_means_for_agents.md` | Why do models hallucinate, forget and get manipulated, and what does an agent builder do about it? | |

Diagrams D60 to D64 in [`diagrams/source/llm_foundation.md`](../../diagrams/source/llm_foundation.md).
