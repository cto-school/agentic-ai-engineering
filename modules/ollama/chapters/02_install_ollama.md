# Install Ollama on Windows, macOS or Linux

Installation takes a few minutes. The result on every platform is the same: a background server on
port 11434 and an `ollama` command in your terminal.

## Windows

1. Open [ollama.com/download](https://ollama.com/download) and download **OllamaSetup.exe**.
2. Run it. It installs for the current user, no administrator rights needed, and starts Ollama as a
   tray application (look for the llama icon near the clock). The tray app starts the server and
   keeps it running after reboots.
3. Open a **new** PowerShell window (the installer updates your PATH, which existing windows do not
   see) and confirm:

```powershell
ollama --version
```

If you prefer a package manager, `winget install Ollama.Ollama` does the same thing.

## macOS

1. Download the macOS application from [ollama.com/download](https://ollama.com/download), open the
   `.zip`/`.dmg`, and drag **Ollama** to Applications.
2. Launch it once. It asks to install the command-line tool and then lives in the menu bar.
3. In Terminal:

```bash
ollama --version
```

Homebrew users can run `brew install ollama` for the command-line server only; then you start the
server yourself with `ollama serve` (or `brew services start ollama` to keep it running).

## Linux

One command downloads and installs Ollama and registers it as a systemd service:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama --version
```

The installer creates an `ollama` system user and stores models under
`/usr/share/ollama/.ollama/models`. Check the service with `systemctl status ollama`.

## Confirm the server is up

The server answers a plain HTTP request. Open a browser at `http://localhost:11434` or run:

```bash
curl http://localhost:11434
```

```powershell
# Windows: PowerShell's own curl is an alias for Invoke-WebRequest; use the real binary
curl.exe http://localhost:11434
```

Expected reply, exactly:

```text
Ollama is running
```

If you get "connection refused", the server is not running. Start it in a terminal with
`ollama serve` (leave that terminal open) or start the tray/menu-bar app.

## Where things live

| | Models on disk | Server log |
|---|---|---|
| Windows | `C:\Users\<you>\.ollama\models` | `%LOCALAPPDATA%\Ollama\server.log` |
| macOS | `~/.ollama/models` | `~/.ollama/logs/server.log` |
| Linux | `/usr/share/ollama/.ollama/models` | `journalctl -u ollama` |

You do not need to touch these folders. It helps to know where the gigabytes go, and where to look
when something fails (chapter O6).

## Recap

- Windows and macOS: run the installer, open a new terminal, `ollama --version`.
- Linux: `curl -fsSL https://ollama.com/install.sh | sh` installs a systemd service.
- `curl http://localhost:11434` must say `Ollama is running` before you continue.
