# Agentic AI Engineering Course Portal

An interactive reader for the five-day Agentic AI Engineering curriculum. It presents the theory embedded in every lesson notebook, tracks student progress in the browser, and provides direct notebook downloads and Google Colab launch links.

The sidebar and each day are independently collapsible. Every lesson has dedicated **Theory**, **Code**, and **Architecture** views generated from the canonical notebook and diagram sources.

## Run locally

```bash
pnpm install
pnpm dev
```

The portal copies and indexes the source notebooks during content generation:

```bash
pnpm content
```

`pnpm build` runs content generation automatically before creating the production build.

The build also runs an alignment check across the canonical five-day syllabus, every day README, all 45 notebook files, copied portal notebooks, required projects, and referenced architecture diagrams. This prevents the website and classroom material from silently drifting apart.

## Google Colab links

After this repository is published on GitHub, select **Set up Colab** in the portal and enter the public repository as `owner/repository` plus its branch name. The values are stored only in the current browser. Every notebook will then open directly in Google Colab.

## Content source

Do not edit `app/course-data.ts` or the copied files under `public/notebooks` by hand. Update the original notebooks in the parent course folders, then run `pnpm content` to refresh both.
