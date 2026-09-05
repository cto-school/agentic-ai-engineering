# Get the model ready with a Gemini key, then run it day to day

The onboarding wizard in C5 probably configured Gemini already. This chapter makes that explicit,
so that you can change models on purpose, and then covers the small routine that keeps a personal
server healthy: audit, logs, updates, backups and cost.

## 1. The API key

1. Open [aistudio.google.com/apikey](https://aistudio.google.com/apikey), sign in, **Create API key**.
2. Give it to OpenClaw either by re-running the auth step of onboarding:

```bash
openclaw onboard --auth-choice gemini-api-key
```

or by setting the environment variable the gateway reads. OpenClaw accepts `GEMINI_API_KEY` or
`GOOGLE_API_KEY`. For a systemd user service, the cleanest place is a small environment file that
the service reads; the wizard route stores the key in OpenClaw's own credential store and is
simpler. Use the wizard.

The Gemini API has a free tier with per-minute and per-day limits that comfortably cover a
personal assistant; a paid tier on the same key removes the limits. Costs are per token, as with
every provider in this course.

## 2. Choose the model

The primary model is one config key. Model ids are `provider/model`:

```bash
openclaw models list --provider google
openclaw config set agents.defaults.model.primary "google/gemini-2.5-flash"
```

`gemini-2.5-flash` is fast and inexpensive and a good default for chat. `models list` shows the
current ids, including newer *pro* models for harder tasks; the documentation's own example uses a
Gemini 3.1 preview. Change the id, and the gateway applies it without a restart. Test:

```bash
openclaw agent --message "Which model are you, and what is 17 times 23?"
```

Then the same question through Telegram. Both should answer with the model you set.

You can also register **fallback** models under `agents.defaults.model.fallbacks` so that a rate
limit on one provider falls through to another, and you can point OpenClaw at OpenRouter with the
course key if you prefer one bill for everything.

## 3. Limit what the agent may do

This is the third security question from C1: assume the model can be manipulated and make the
damage small. Two settings do most of the work, and the audit command checks them.

```bash
openclaw security audit
```

It reports on inbound access, tool "blast radius", filesystem permissions, network exposure and
sandbox settings, and `openclaw security audit --fix` applies the safe fixes. A conservative
baseline to put in `openclaw.json` for a messaging assistant:

```json5
{
  gateway: { bind: "loopback" },
  tools: {
    profile: "messaging",
    exec: { security: "deny", ask: "always" },
  },
}
```

`profile: "messaging"` keeps the conversational tools and drops the ones that change the machine;
`exec.security: "deny"` refuses shell commands outright, and `ask: "always"` means that where a
command is allowed, the agent must ask you first. Loosen these one at a time when you find a task
that needs it, and run the audit again after every change. Docker-based sandboxing for tools is
available if you later want the agent to run code; the documentation describes it.

Run `openclaw doctor` after editing the file; a typo that fails validation is reported there, and
`openclaw config validate` checks before you save.

## 4. Daily operation

**Logs.** `openclaw logs --follow` shows messages arriving, model calls and tool use. Read it the
first day; it is the equivalent of the trace printed in the course notebooks.

**Restart and status.** `openclaw gateway status`; `systemctl --user restart
openclaw-gateway.service` if something is stuck; `openclaw gateway install --force` re-creates the
service definition after you change gateway settings such as the port.

**Updates.** Re-run the installer (`curl -fsSL https://openclaw.ai/install.sh | bash`) or
`npm install -g openclaw@latest --allow-scripts=openclaw`, then `openclaw doctor` and
`openclaw gateway status`. Read the release notes first; OpenClaw moves quickly.

**Backups.** Everything that is yours lives in two places: `~/.openclaw` (configuration and
credentials) and the workspace folder (memory and notes). Copy them off the machine occasionally:

```bash
# from your laptop
scp -r openclaw:~/.openclaw ./openclaw-backup-$(date +%F)
```

**Cost.** Three meters: the EC2 instance (hours running; stop it when away), the public IPv4
address (hourly, small), and Gemini tokens. Check **Billing → Bills** in AWS monthly and the budget
alert from C2 will tell you about surprises. When the course is over, **Terminate** the instance,
release any Elastic IP, and delete the Telegram bot with BotFather's `/deletebot` or revoke its
token.

**Machine hygiene.** Once a month: `ssh openclaw`, `sudo apt update && sudo apt upgrade -y`,
`sudo reboot` if a kernel changed, `openclaw gateway status` afterwards. Unattended upgrades cover
security patches between visits.

## What you built, in course terms

| OpenClaw | Course concept |
|---|---|
| gateway loop with tools | Day 1 agent loop; Day 5 harness |
| workspace memory files | Day 3 long-term memory |
| `dmPolicy`, allowlists, mention gating | Day 3 permissions: who may issue instructions |
| `tools.profile`, `exec.security`, sandbox | Day 3 policy between proposal and side effect |
| `security audit`, logs | Day 4 and 5 observability and evaluation |
| prompt injection through fetched pages | Day 3 and the LangGraph track's injection attack |

## Recap

- A Gemini key from AI Studio goes in through `openclaw onboard --auth-choice gemini-api-key`; the model is `agents.defaults.model.primary`, for example `google/gemini-2.5-flash`.
- Restrict tools (`profile: "messaging"`, `exec.security: "deny"`) and run `openclaw security audit` after every configuration change.
- Operate it with logs, status, updates, backups of `~/.openclaw`, and stop or terminate the instance to control cost.
