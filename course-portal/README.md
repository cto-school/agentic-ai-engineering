# Agentic AI Engineering Course Portal

An interactive reader for the five-day Agentic AI Engineering curriculum. Students use it alongside the classroom notebooks to read ahead, revise, or catch up.

## What students get

- **Getting started** page: how the course works, the four steps before Day 1, the complete `.env` and API-key guide (the same text as Day 1 Lesson 1), Google Colab configuration, and a progress reset.
- For every one of the 45 lessons, three views:
  - **Learn**: the beginner guide (idea, mental picture, steps, key distinction, common mistake), the lesson's *Before you begin* block, the full **Concept briefing** theory text from the notebook, and the **Checkpoint and recap** with answers folded under *Show answer*.
  - **Notebook**: the complete lesson notebook rendered cell by cell, markdown and code in reading order.
  - **System view**: the lesson's architecture diagrams drawn from the Mermaid sources, with a text alternative.
- Sidebar search across lesson titles, guides, and theory text; per-lesson completion tracking stored in the browser; notebook downloads; and one-click Colab links once the repository is configured.

## Run locally

```bash
pnpm install
pnpm dev
```

The portal copies and indexes the source notebooks during content generation:

```bash
pnpm content
```

`pnpm build` runs content generation automatically before creating the production build. The build also runs an alignment check across the canonical five-day syllabus, every day README, all 45 notebook files, copied portal notebooks, required projects, and referenced architecture diagrams, so the website and classroom material cannot silently drift apart.

## Google Colab links

After the repository is published on GitHub, open **Getting started** in the portal and enter the public repository as `owner/repository` plus its branch. The values are stored only in the current browser. Until a repository is configured, the Colab buttons lead back to the settings and students can download the notebooks instead.

## Content source

Do not edit `app/course-data.ts` or the copied files under `public/notebooks` by hand. Update the original notebooks in the parent course folders (and `content/lesson-guides.json` / `content/common-mistakes.json` for the beginner guides), then run `pnpm content` to refresh everything.
