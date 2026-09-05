# Agent 2: a research agent with tools

This agent looks things up, does arithmetic and fetches live data. It exercises the tool socket and
the *Let the model define this parameter* mechanism, and it shows the tool loop running several
rounds inside one execution.

## Build it

Start by duplicating Agent 1 (Overview → the workflow's menu → **Duplicate**) and renaming the copy
`Agent 2 - Research agent`, or build the three nodes again. Then attach three tools to the
**Tool** socket of the AI Agent:

### Tool 1: Wikipedia

Add **Wikipedia**. It has no settings. Its built-in description tells the model it can search
Wikipedia for a topic.

### Tool 2: Calculator

Add **Calculator**. Also no settings. Language models are unreliable at arithmetic; this tool makes
them reliable.

### Tool 3: HTTP Request for the weather

Add **HTTP Request Tool** (the *tool* variant, not the ordinary HTTP Request node). Fill it in:

- **Description**: `Returns the current temperature and wind speed for given coordinates. Use
  after you know the latitude and longitude of the place the user asked about.`
- **Method**: GET
- **URL**:

```text
https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m
```

- Under **Placeholder Definitions**, add two placeholders named `latitude` and `longitude`, each with
  the description `decimal degrees` and type *number*.

Placeholders in braces are what the model fills in. Alternatively, in newer versions, hover over a
field and choose **Let the model define this parameter**; n8n writes a `$fromAI('latitude', ...)`
expression that does the same thing.

Open-Meteo needs no key. The model knows the coordinates of large cities; for small places it will
first search Wikipedia, which lists coordinates, and then call the weather tool. That is the loop.

### System message

Replace the system message with:

```text
You are a careful research assistant.
Use the Wikipedia tool for facts you are not sure about, the Calculator for any arithmetic,
and the weather tool for current conditions. Say which tool you used.
If a tool returns nothing useful, say so rather than inventing an answer.
```

Set **Max Iterations** (AI Agent → Options) to 8.

## Test it

Send these one at a time and read each answer:

```text
What is the current temperature in Reykjavik, and what is that in Fahrenheit?
Who founded the university in Uppsala, and how many years ago was that?
How far is Nairobi from the equator, roughly?
```

Now open **Executions** and click the latest run. The agent node shows several model calls in
sequence: a call that requests the weather tool, the tool's output, a call that requests the
calculator, its output, then the final text. Each tool sub-node lights up once per use. Count the
rounds and compare them with Max Iterations.

## When it goes wrong

- **The model answers from memory instead of using a tool.** Strengthen the system message ("Always
  use the Calculator for arithmetic, even simple sums"). Models trust themselves too much.
- **"Tool input did not match schema".** The model sent a string where the placeholder wanted a
  number. Improve the placeholder description ("decimal degrees, for example 64.13").
- **Max iterations reached.** The model loops, usually because a tool keeps returning something it
  cannot use. Read the tool outputs in the execution; fix the description or the URL.
- **Wikipedia returns the wrong article.** Tell the model in the system message to include the
  country in its search terms.

## What this shows

The agent node did not become smarter with three tools; it became more useful because you gave it
verified capabilities and described them well. The descriptions did the routing. Change the
weather tool's description to "Returns stock prices" and watch the model stop using it for weather,
even though the URL is unchanged. That is the lesson of Day 1 section 1.4, on a canvas.

## Recap

- Tools plug into the agent's Tool socket; Wikipedia and Calculator need no settings, HTTP Request Tool needs a description, a URL and model-filled placeholders.
- The Executions view shows every round of the loop: model call, tool, model call, answer.
- Tool descriptions are what the model reads to choose; write them for a colleague.
