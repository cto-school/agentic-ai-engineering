# What OpenClaw is, and why it gets a machine of its own

**OpenClaw** is an open-source personal assistant. You message it from apps you already use, such
as Telegram, WhatsApp, Slack or Discord, and it answers with a language model of your choice. Unlike
a chat website, it runs on a computer you control, keeps memory across conversations, and can act:
run commands, read and write files, browse, call APIs and use skills you add.

Everything in this course about agents applies to it. OpenClaw is an agent loop with tools, memory,
guardrails and channels, packaged as a product. This module does not build it; it deploys it well.

## The parts (diagram D57)

- **The gateway.** One long-running process on your machine. It holds the connections to the
  messaging platforms, routes each incoming message to an agent, runs the agent loop, and exposes
  a local control API on port 18789 (bound to the machine itself by default, not the internet).
- **Channels.** Adapters to messaging platforms. This module uses **Telegram**, because a Telegram
  bot takes two minutes to create and needs no phone-number linking.
- **Agents.** The assistant personalities. Each has a workspace folder, a system prompt, memory
  files, a set of tools it may use, and a **model**.
- **Providers.** Where the model runs. OpenClaw talks to Anthropic, OpenAI, Google, OpenRouter,
  local Ollama and others. This module uses **Google Gemini** through an API key from AI Studio.
- **Skills and tools.** Shell execution, file access, web fetch, browser control, and installable
  skills. Which of these an agent may use is configuration, and chapter C7 restricts it.
- **Configuration.** One file, `~/.openclaw/openclaw.json`, in JSON5 (JSON with comments). The
  gateway watches it and applies most changes without a restart.

The flow for one message (diagram D59): you type in Telegram → Telegram's servers deliver it to the
gateway's bot connection → the gateway checks that you are allowed to talk to this bot → the agent
assembles its context (system prompt, memory, the conversation) → the model at Google decides on a
reply or a tool call → tools run on your machine → the reply goes back through Telegram.

## Why an always-on machine, and why its own

Two reasons, one practical and one about safety.

**Practical.** A personal assistant is only useful if it answers when you are not at your laptop.
The gateway must run all day, with a stable network connection, which means a small server. AWS
EC2 gives you one for a few dollars a month, and the Free plan credits for a new account cover
this module.

**Safety.** OpenClaw can execute shell commands and read files, because that is what makes it
useful. Its own documentation is direct about the main risk: most incidents are not exploits; they
are "someone messaged the bot and the bot did what they asked". Anything the model reads, including
a web page it fetched, can try to talk it into doing something. The defence the course teaches in
Day 3 applies: limit who can talk to it, limit what it can touch, and assume the model can be
manipulated. Running it on a dedicated machine with nothing personal on it is the single biggest
part of "limit what it can touch". Your laptop, with your browser sessions and documents, is the
wrong place.

Chapters C2 to C4 therefore build the machine carefully: no root user in daily use, key-only SSH,
a firewall that admits only you. Chapter C7 finishes with OpenClaw's own security audit.

## What you will need

- A credit or debit card and a phone number for AWS. The module stays inside the Free plan
  credits; chapter C2 sets a budget alert anyway.
- A Google account for the Gemini API key (free tier).
- A Telegram account.
- A terminal: PowerShell on Windows 10 or 11 (OpenSSH is built in), Terminal on macOS, any shell
  on Linux.

Budget about two hours for the AWS chapters the first time, and one hour for OpenClaw.

## Recap

- OpenClaw is a self-hosted assistant: a gateway process, channels such as Telegram, agents with tools and memory, and a model provider such as Gemini.
- It needs an always-on machine, and for safety a machine of its own with nothing personal on it.
- The module builds that machine first (AWS, EC2, SSH hardening), then installs and secures OpenClaw.
