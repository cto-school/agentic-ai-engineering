# Install OpenClaw and start the gateway

OpenClaw is a Node.js application. Its installer brings Node, installs the `openclaw` command, and
an onboarding wizard writes the configuration and registers the gateway as a service that starts
with the machine. Have your Gemini API key ready (chapter C7 explains where it comes from:
[aistudio.google.com/apikey](https://aistudio.google.com/apikey), **Create API key**).

## 1. Run the installer

Logged in as `ubuntu` (or the `openclaw` user if you created one):

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

The script installs Node (24 LTS if none is present; OpenClaw requires Node 22.22 or newer) and the
`openclaw` package. When it finishes, reload your shell so the command is found:

```bash
source ~/.bashrc
openclaw --version
```

If you would rather manage Node yourself, the equivalent is
`npm install -g openclaw@latest --allow-scripts=openclaw`.

## 2. Onboard

```bash
openclaw onboard --install-daemon
```

The wizard asks a handful of questions. The choices that matter for this module:

- **Model provider / auth**: choose the **Gemini API key** option and paste the key. (Later you can
  re-run just this step with `openclaw onboard --auth-choice gemini-api-key`.)
- **Workspace**: accept the default folder under your home directory. This is where the agent keeps
  its memory files and notes.
- **Channels**: skip for now; Telegram is chapter C6.
- **Gateway service**: yes. `--install-daemon` creates a systemd *user* service named
  `openclaw-gateway.service`.

The wizard writes `~/.openclaw/openclaw.json`. Open it once to see the shape; it is JSON5, so
comments and trailing commas are allowed:

```bash
cat ~/.openclaw/openclaw.json
```

## 3. Keep the service alive after you log out

A systemd *user* service normally stops when its user's last session ends. Tell Linux to keep your
user's services running:

```bash
sudo loginctl enable-linger $(whoami)
```

If the wizard did not install the service, or you need to re-create it later:

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway.service
```

## 4. Check

```bash
openclaw gateway status
openclaw doctor
```

A healthy status shows `Runtime: running` and `Connectivity probe: ok`. `doctor` lists anything
misconfigured and `openclaw doctor --fix` repairs the safe cases. Also confirm from the outside of
OpenClaw that the gateway is listening on the machine only:

```bash
ss -ltnp | grep 18789
```

The address should be `127.0.0.1:18789`, not `0.0.0.0`. That is the default (`gateway.bind:
"loopback"`); leave it. The security group and ufw from chapter C4 would block it anyway, and both
together are the intended posture.

Log out (`exit`), log in again, and run `openclaw gateway status` once more: still running. That is
linger doing its job.

## 5. Talk to it from the terminal

Before any channel is connected you can chat with the agent locally:

```bash
openclaw agent --message "Hello. In one sentence, what can you do?"
```

The reply comes from Gemini through your key. If it fails, the model is not configured yet;
chapter C7 sets it explicitly. Also try `openclaw tui` for a terminal chat window, `q` to leave.

## Useful commands

| Command | Purpose |
|---|---|
| `openclaw gateway status` | is it running, which version, which port |
| `openclaw logs --follow` | live log; Ctrl+C to stop |
| `openclaw config get <key>` / `set <key> <value>` / `validate` | read and change configuration safely |
| `openclaw doctor` / `--fix` | diagnose and repair |
| `systemctl --user restart openclaw-gateway.service` | restart the service |

## Recap

- One curl command installs Node and OpenClaw; `openclaw onboard --install-daemon` configures it and creates a user service.
- `loginctl enable-linger` keeps the gateway running after you log out.
- The gateway listens on `127.0.0.1:18789` only; `openclaw gateway status` and `openclaw doctor` confirm health.
