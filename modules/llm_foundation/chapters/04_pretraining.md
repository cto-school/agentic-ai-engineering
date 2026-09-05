# Pretraining: where the weights come from

A freshly built Transformer has billions of parameters set to random numbers and produces random
tokens. **Pretraining** is the process that turns those numbers into a model that can continue any
text plausibly. It is the most expensive step in the whole pipeline (diagram D62, first stage) and
the source of nearly everything the model knows.

## Step 1: the data

The training set is text, as much as can be gathered and cleaned:

- **Web crawls.** Snapshots of billions of pages (Common Crawl is the public one), filtered hard.
- **Books, papers, encyclopedias, forums.** Higher quality per token; over-sampled on purpose.
- **Code.** Public repositories. Code makes models better at reasoning as well as at code.
- **Multilingual text**, and increasingly **synthetic text** written by earlier models.

Cleaning is most of the work: remove boilerplate and navigation menus, drop pages with too little
real text, detect language, remove personal data where it can be found, filter toxic content, and
**deduplicate**. Duplicates matter more than you would guess: a paragraph seen a thousand times is
memorised rather than learned from. Frontier models train on 10 to 30 trillion tokens after
cleaning; a 4B model such as Gemma 3 on a few trillion.

The data has a date. Nothing after the last crawl exists for the model: that is the **knowledge
cutoff** that the course reminds you of whenever a question involves recent facts.

## Step 2: the objective

The task is the one from chapter F3, run in reverse. Take a document, feed it through the model, and
at every position compare the predicted distribution with the token that actually came next. The
loss is the **cross-entropy**: how much probability the model failed to give the true token, averaged
over all positions. Lower is better; a model with loss 2.0 (in the units usually reported) is
assigning the real next token about one chance in seven on average, which is already fluent text.

Then **backpropagation** computes, for every one of the billions of parameters, which direction
would have lowered the loss, and an optimiser (Adam and its relatives) nudges each parameter a tiny
step that way. Repeat for the next batch of documents. That is all. There are no rules, no
grammar, no facts entered by hand: everything the model can do emerges from predicting the next
token well across an enormous corpus, because predicting well requires modelling grammar, facts,
style, arithmetic and reasoning to the extent that they help.

## Step 3: the compute

Every batch is billions of matrix multiplications. Training runs on clusters of thousands of GPUs
(or TPUs), connected so that one model can be split across them: the layers over some machines,
the batch over others, the weight matrices themselves sliced when they do not fit. A frontier run
takes weeks to months and tens of millions of dollars in electricity and hardware time; a 1B model
can be trained in days on a few dozen GPUs.

Checkpoints are saved regularly, and the loss curve is watched like a patient's pulse. Runs fail:
hardware breaks, the loss spikes, a data bug is found. Much of the engineering is restarting
without losing days.

## Scaling laws

The most important empirical finding of the last five years: the loss falls predictably as you
increase three things together, the number of parameters, the number of training tokens, and the
compute spent. Doubling any one of them helps less than doubling all in proportion, and there is a
best ratio of tokens to parameters for a given budget (roughly 20 tokens per parameter for the best
loss, and far more when you care about cheap inference, which is why small models are now trained
on absurd amounts of data). This is why model releases talk about parameter counts and training
tokens: those two numbers predict quality before anything is measured.

## What a base model is like

The result of pretraining is a **base model**. Ask it "What is the capital of France?" and it may
answer "Paris", or continue with "What is the capital of Germany?" because quiz lists were in the
data, or write a paragraph of a geography textbook. It completes text; it does not know that it is
talking to someone or that questions want answers. It has no notion of being helpful, of refusing,
of a user and an assistant. The tags `-it` and `-instruct` in model names (Ollama module) mark the
models that have been taken further; chapter F5 is that further step.

## Recap

- Pretraining feeds trillions of cleaned, deduplicated tokens through the model and adjusts every parameter to predict the next token better; the data's date is the knowledge cutoff.
- The loss is cross-entropy; backpropagation and an optimiser do the adjusting on thousands of GPUs for weeks.
- Loss falls predictably with parameters, tokens and compute (scaling laws); the result is a base model that continues text but does not yet behave like an assistant.
