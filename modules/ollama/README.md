# Ollama module — Gemma 3 on your own laptop

**Outcome:** a small open-weights model (Gemma 3) running locally on a standard laptop with no
dedicated graphics card, used from the terminal, customised with a Modelfile, and reachable from
programs through the same request shape the course uses for hosted models.

This module is independent of the five days and of the LangChain and LangGraph tracks. It contains
no notebook: every chapter is theory, a diagram and terminal instructions you follow on your own
machine (Windows, macOS or Linux).

| Chapter | File | You learn | You do |
|---|---|---|---|
| O1 | `01_what_ollama_is.md` | what "running a model locally" means; weights, quantisation, the Ollama server | check your laptop's RAM and CPU |
| O2 | `02_install_ollama.md` | where Ollama lives on each operating system | install Ollama and confirm the server answers |
| O3 | `03_choose_a_model_for_a_laptop.md` | model sizes, quantisation, the memory rule of thumb, Gemma 3 variants | pick the Gemma 3 size for your machine |
| O4 | `04_pull_and_run_gemma.md` | the Ollama CLI, the chat prompt, slash commands, model management | pull Gemma 3 and hold a conversation in the terminal |
| O5 | `05_talk_to_ollama_from_programs.md` | the local REST API and the OpenAI-compatible endpoint | send requests with curl and point a course notebook at Ollama |
| O6 | `06_customise_and_troubleshoot.md` | Modelfiles, parameters, environment variables, common failures | create a tutor model and fix the usual problems |

Diagrams D50 to D52 in [`diagrams/source/ollama.md`](../../diagrams/source/ollama.md).
