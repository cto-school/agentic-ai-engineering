# Agentic AI Engineering Course Portal

An interactive reader for the five-day Agentic AI Engineering curriculum. Students use it alongside the classroom notebooks to read ahead, revise, or catch up.

## What students get

- **Getting started** page: the course map (five days plus the separate LangChain track), how the course works in four lines, a course map of the five days (project and outcome per day), the three steps before Day 1, the API-key guide (the same text that opens the Day 1 notebook), Google Colab configuration, and a progress reset.
- For every one of the 39 day sections and the 14 LangChain-track sections, three views:
  - **Learn**: a short plain-language guide (the idea, a picture, three steps, the distinction to keep straight, the common mistake, what to notice when you run it), followed by the section's own explanations from the notebook with the checkpoint answers folded out.
  - **Notebook**: the complete section rendered cell by cell, explanations and code in running order.
  - **System view**: the section's architecture diagrams drawn from the Mermaid sources, with a text alternative.
- Sidebar search across titles, guides and explanations; per-section completion tracking stored in the browser; and one Colab link per day (next to the Learn tab and in the sidebar) that opens the complete day notebook. Sections are never opened or downloaded individually, because definitions carry forward within a day.

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

Do not edit `app/course-data.ts` or the copied files under `public/notebooks` by hand. Update the original notebooks in the parent course folders (and `content/lesson-guides.json` / `content/common-mistakes.json` for the beginner guides), then run `pnpm content` to refresh everything.
