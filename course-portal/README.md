# Agentic AI Engineering Course Portal

An interactive reader for the five-day Agentic AI Engineering curriculum, its two notebook tracks, and five standalone modules. Students use it alongside the classroom notebooks to read ahead, revise, or catch up.

## What students get

- **Getting started** page: how the site works, a module map that places every unit on one of three layers (understand the model, build the agent, give it memory and a home) plus the five-day path, suggested routes through the modules, cards for the standalone modules and the five days, the three steps before a notebook module, the API-key guide (the same text that opens every notebook), Google Colab configuration, and a progress reset.
- For every one of the 39 day sections, the 14 LangGraph-track sections and the 14 LangChain-track sections, three views:
  - **Learn**: why the section exists (the problem its recap names), the idea, an analogy, *How it works* (the mechanism in plain words, hand-written for the LangGraph track and taken from the diagram elsewhere), *What you will do in the notebook*, the key distinction, the common mistake, what to notice when running, and the section's recap (with folded checkpoint answers on the days). It no longer repeats the notebook's text; that lives in the Notebook tab.
  - **Notebook**: the complete section rendered cell by cell, explanations and code in running order.
  - **System view**: the section's architecture diagrams drawn from the Mermaid sources, with a text alternative.
- For each of the 34 chapters of the five standalone modules (Ollama, n8n, OpenClaw, LLM Foundation, Mem0), two views: **Learn** (the same beginner guide, then the full chapter with its theory, instructions and commands; the LLM Foundation chapters on tokens and sampling embed two interactive simulations, a trainable byte-pair tokenizer and a next-token predictor with a temperature slider) and **System view**. Modules have no notebook, so no Colab link and no Notebook tab.
- The sidebar lists one **Standalone modules** group (LangGraph first, then Ollama, n8n, OpenClaw, LLM Foundation and Mem0, LangChain last) above the **Five-day path**. Previous and next navigation stays inside a unit; the last section of a unit shows a card back to the module map. Sidebar search across titles, guides and explanations; per-section completion tracking stored in the browser; and one Colab link per notebook unit (next to the Learn tab and in the sidebar) that opens the complete notebook. Sections are never opened or downloaded individually, because definitions carry forward within a notebook.

## Run locally

```bash
pnpm install
pnpm dev
```

The portal copies and indexes the source notebooks during content generation:

```bash
pnpm content
```

`pnpm build` runs content generation automatically before creating the production build. The build also runs an alignment check across the canonical five-day syllabus, every day README, every day and track notebook file, copied portal notebooks, required projects, and referenced architecture diagrams, so the website and classroom material cannot silently drift apart.

## Google Colab links

After the repository is published on GitHub, open **Getting started** in the portal and enter the public repository as `owner/repository` plus its branch. The values are stored only in the current browser. Until a repository is configured, the Colab buttons lead back to the settings and students can download the notebooks instead.

## Content source

Do not edit `app/course-data.ts` or the copied files under `public/notebooks` by hand. Update the original notebooks in the parent course folders, or the Markdown chapters under `modules/<module>/chapters/` (and `content/lesson-guides.json` / `content/common-mistakes.json` for the beginner guides, keyed by notebook or chapter file name), then run `pnpm content` to refresh everything. A chapter embeds a simulation with an HTML comment such as `<!-- widget:tokenizer -->`; the widgets themselves live in `app/llm-playground.tsx`.
