'use client';

import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import { marked } from 'marked';
import { ArrowLeft, ArrowRight, BookOpen, Check, ChevronDown, ChevronRight, Circle, Code2, ExternalLink, FileJson, GitBranch, GraduationCap, KeyRound, Menu, Network, NotebookTabs, PanelLeftClose, Rocket, Search, Sparkles } from 'lucide-react';
import { courseDays, setupGuide } from './course-data';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

type CourseDay = (typeof courseDays)[number];
type Notebook = CourseDay['notebooks'][number];
type Diagram = CourseDay['diagrams'][number];
type ColabSettings = { repo: string; branch: string };

const STORAGE_PROGRESS = 'agentic-course-progress';
const STORAGE_COLAB = 'agentic-course-colab';
const DEFAULT_COLAB: ColabSettings = { repo: 'cto-school/agentic-ai-engineering', branch: 'main' };
const UNCONFIGURED_REPO = 'OWNER/REPOSITORY';
const COURSE_LAYERS = ['Model + tools', 'Knowledge', 'Memory + safety', 'Multi-agent', 'Harness'];
const TITLE_PREFIX = /^Day \d+(?:\.\d+| Project| Capstone)? — /;

marked.use({ gfm: true, breaks: false });

function renderMarkdown(source: string): string {
  const html = marked.parse(source, { async: false }) as string;
  // Notebook-relative links (../../diagrams/...) have no meaning inside the portal:
  // the same diagrams are rendered in the "System view" tab.
  return html.replace(/<a href="\.\.\/[^"]*">([^<]*)<\/a>/g, '<span class="doc-ref">$1 · see System view</span>');
}

function Markdown({ source, className = '' }: { source: string; className?: string }) {
  const html = useMemo(() => renderMarkdown(source), [source]);
  return <div className={`lesson-prose ${className}`} dangerouslySetInnerHTML={{ __html: html }} />;
}

function shortTitle(title: string) {
  return title.replace(TITLE_PREFIX, '');
}

function colabUrl(settings: ColabSettings, repoPath: string) {
  return `https://colab.research.google.com/github/${settings.repo}/blob/${settings.branch}/${repoPath}`;
}

function githubUrl(settings: ColabSettings, repoPath = '') {
  return `https://github.com/${settings.repo}${repoPath ? `/blob/${settings.branch}/${repoPath}` : ''}`;
}

function CodeCell({ source, index }: { source: string; index: number }) {
  return <div className="code-cell"><div className="code-cell-header"><span>Python · cell {index}</span><span>Run in the notebook</span></div><pre><code>{source || '# This cell is intentionally empty'}</code></pre></div>;
}

function NotebookWalkthrough({ notebook }: { notebook: Notebook }) {
  const items = [];
  let codeIndex = 0;
  for (const cell of notebook.cells) {
    if (cell.type === 'code') {
      codeIndex += 1;
      items.push(<CodeCell key={cell.id} source={cell.source} index={codeIndex} />);
    } else {
      items.push(<Markdown key={cell.id} source={cell.source} className="notebook-markdown" />);
    }
  }
  return <div className="notebook-walkthrough">{items}</div>;
}

function MermaidDiagram({ diagram }: { diagram: Diagram }) {
  const [rendered, setRendered] = useState<{ id: string; svg: string; failed: boolean } | null>(null);
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      try {
        const mermaid = (await import('mermaid')).default;
        mermaid.initialize({ startOnLoad: false, theme: 'neutral', fontFamily: 'inherit' });
        const elementId = `mermaid-${diagram.id}-${Math.random().toString(36).slice(2, 8)}`;
        const result = await mermaid.render(elementId, diagram.mermaid);
        if (!cancelled) setRendered({ id: diagram.id, svg: result.svg, failed: false });
      } catch {
        if (!cancelled) setRendered({ id: diagram.id, svg: '', failed: true });
      }
    })();
    return () => { cancelled = true; };
  }, [diagram.id, diagram.mermaid]);
  const current = rendered?.id === diagram.id ? rendered : null;
  const svg = current?.svg ?? '';
  const failed = current?.failed ?? false;
  const labels = new Map<string, string>(diagram.nodes.map((node) => [node.id, node.label]));
  return <section className="architecture-card">
    <div className="architecture-heading"><div className="grid size-10 place-items-center rounded-xl bg-[var(--ink)] text-white"><Network className="size-5" /></div><div><p className="eyebrow">{diagram.id} · Concept architecture</p><h3>{diagram.title}</h3></div></div>
    {svg && !failed && <div className="mermaid-canvas" dangerouslySetInnerHTML={{ __html: svg }} />}
    {!svg && !failed && <p className="architecture-loading">Drawing the diagram…</p>}
    {(failed || !svg) && <div className="architecture-flow">{diagram.edges.map((edge, index) => <div className="architecture-edge" key={`${edge.from}-${edge.to}-${index}`}><span>{labels.get(edge.from) || edge.from}</span><em>{edge.label ? edge.label : ''}<ChevronRight /></em><span>{labels.get(edge.to) || edge.to}</span></div>)}</div>}
    {diagram.textAlternative && <p className="architecture-note"><strong>In words:</strong> {diagram.textAlternative}</p>}
    <p className="architecture-note">Read each arrow as a transfer of data or control. These boundaries are where the application validates inputs, enforces policy, and records events.</p>
  </section>;
}

function DayStory({ day, lessonOrder }: { day: CourseDay; lessonOrder: number }) {
  return <section className="day-story"><div><p className="eyebrow">Day {day.number} project storyline</p><h2>{day.project}</h2><p>{day.projectBrief}</p><p className="project-signpost">The complete pieces are first assembled in Lesson {day.number}.{day.projectLesson}. You are not expected to understand the whole project before reaching it.</p></div><ol>{day.projectFlow.map((stage, index) => <li key={stage} className={lessonOrder >= Math.ceil(((index + 1) / day.projectFlow.length) * day.projectLesson) ? 'reached' : ''}><span>{index + 1}</span>{stage}</li>)}</ol></section>;
}

function LessonGuide({ day, lesson, previousTitle }: { day: CourseDay; lesson: Notebook; previousTitle?: string }) {
  const guide = lesson.guide;
  const projectConnection = lesson.isProject
    ? `This is an integration point: you now combine the earlier building blocks into the ${day.project} and inspect the complete flow.`
    : lesson.isExercise
      ? `This exercise isolates one important mechanism from the ${day.project} so you can prove that you understand it without relying on the completed project code. A commented reference solution follows the check in the notebook.`
      : `This lesson contributes one building block to the ${day.project}. Specifically, it establishes this rule: ${guide.takeaway}`;
  return <div className="lesson-guide">
    {lesson.order === 1 && <DayStory day={day} lessonOrder={lesson.order} />}
    <section className="lesson-bridge"><p className="eyebrow">Before this lesson</p><p>{previousTitle ? <>This section builds on <strong>{shortTitle(previousTitle)}</strong>. If that idea is unclear, revisit it before running the new cells.</> : day.prerequisite}</p></section>
    <section><h2>The idea in one paragraph</h2><p>{guide.idea}</p></section>
    <section><h2>Build a mental picture</h2><p>{guide.example}</p></section>
    <section><h2>What happens in the system</h2><ol className="guide-steps">{guide.steps.map((step, index) => <li key={step}><span>{index + 1}</span><p>{step}</p></li>)}</ol></section>
    <aside className="guide-takeaway"><p className="eyebrow">Keep this distinction clear</p><p>{guide.takeaway}</p></aside>
    <aside className="guide-mistake"><p className="eyebrow">Common beginner mistake</p><p>{guide.mistake}</p></aside>
    {lesson.before && <section><h2>Before you begin</h2><Markdown source={lesson.before} /></section>}
    {lesson.theory && <section className="concept-briefing"><h2>Concept briefing</h2><p className="section-hint">This is the same theory text that sits inside the notebook, so you can read it here before or after running the cells.</p><Markdown source={lesson.theory} /></section>}
    <section><h2>How this lesson advances the project</h2><p>{projectConnection}</p></section>
    <section><h2>What to notice in the notebook</h2><p>{guide.notebook}</p></section>
    {lesson.closing && <section><h2>Checkpoint and recap</h2><p className="section-hint">Try to answer before opening each answer.</p><Markdown source={lesson.closing} /></section>}
  </div>;
}

function GettingStarted({ settings, onSettings, onOpenLesson, onResetProgress }: { settings: ColabSettings; onSettings: (next: ColabSettings) => void; onOpenLesson: () => void; onResetProgress: () => void }) {
  // The parent remounts this form (key = saved settings) whenever the saved values change.
  const [repo, setRepo] = useState(settings.repo);
  const [branch, setBranch] = useState(settings.branch);
  const configured = settings.repo !== UNCONFIGURED_REPO;
  return <div className="lesson-guide getting-started">
    <section className="start-hero"><p className="eyebrow">Start here</p><h2>How this course works</h2>
      <ul className="start-list">
        <li><strong>Five days, five projects.</strong> Each day has one master notebook that you run top to bottom, and the same content split into short lessons for reference. This portal mirrors every lesson.</li>
        <li><strong>Learn by running.</strong> Lessons are step-by-step: a short explanation, then a small code cell that prints what happened. Read the output, then the comments, then move on.</li>
        <li><strong>Try it, then see the answer.</strong> Each lesson has at most one <em>Try it yourself</em> prompt, always followed by a fully commented worked solution. Every day ends with one hands-on exercise that also carries a reference solution.</li>
        <li><strong>No key needed to learn.</strong> Without an API key every cell runs in deterministic <em>mock</em> mode and spends nothing. Live model calls are used only where the model&apos;s behaviour is the lesson, and they fall back to mock automatically.</li>
        <li><strong>Checkpoints have answers.</strong> Each lesson ends with two questions; the answers are folded under <em>Show answer</em>.</li>
      </ul>
    </section>
    <section><h2>Four steps before Day 1</h2>
      <ol className="guide-steps">
        <li><span>1</span><p><strong>Install Python and the course packages</strong> following <code>setup/installation_guide.md</code> in the repository{configured && <> (<a href={githubUrl(settings, 'setup/installation_guide.md')} target="_blank" rel="noreferrer">open on GitHub</a>)</>}. Python 3.10 or newer is enough.</p></li>
        <li><span>2</span><p><strong>Create your <code>.env</code> file</strong> with the issued OpenRouter key, exactly as described below. Skip this step entirely if you want to stay in mock mode.</p></li>
        <li><span>3</span><p><strong>Open the Day 1 master notebook</strong> locally with Jupyter, or in Google Colab using the links in this portal once the repository is configured.</p></li>
        <li><span>4</span><p><strong>Use this portal alongside the notebook.</strong> <em>Learn</em> explains the idea and the theory, <em>Notebook</em> shows every cell with its explanation, and <em>System view</em> draws the architecture.</p></li>
      </ol>
    </section>
    <section className="setup-guide"><h2>Your API key and the .env file</h2><p className="section-hint">This is the same guide that appears in Day 1 Lesson 1.</p><Markdown source={setupGuide.replace(/^##\s+Setting up your \.env file\s*/m, '')} /></section>
    <section className="colab-settings"><h2>Google Colab links</h2>
      <p>Colab opens notebooks straight from a public GitHub repository. Enter the course repository once; the value is stored only in this browser and every <em>Open in Colab</em> link in the portal will use it.</p>
      <form className="colab-form" onSubmit={(event) => { event.preventDefault(); onSettings({ repo: repo.trim() || DEFAULT_COLAB.repo, branch: branch.trim() || 'main' }); }}>
        <div className="colab-field"><label htmlFor="colab-repo">Repository <span>owner/repository</span></label><Input id="colab-repo" value={repo} onChange={(event) => setRepo(event.target.value)} placeholder="owner/repository" /></div>
        <div className="colab-field"><label htmlFor="colab-branch">Branch</label><Input id="colab-branch" value={branch} onChange={(event) => setBranch(event.target.value)} placeholder="main" /></div>
        <Button type="submit"><Check />Save</Button>
      </form>
      <p className={`colab-status ${configured ? 'ok' : ''}`}>{configured ? <>Colab links point to <code>{settings.repo}</code> on branch <code>{settings.branch}</code>.</> : 'Colab links are not configured yet: download the notebooks instead, or ask your instructor for the repository name.'}</p>
    </section>
    <section><h2>Ready?</h2><div className="start-actions"><Button onClick={onOpenLesson}><Rocket />Go to Day 1, Lesson 1</Button><Button variant="outline" onClick={onResetProgress}>Reset my progress</Button></div></section>
  </div>;
}

export function CoursePortal() {
  const [view, setView] = useState<'start' | 'lesson'>('start');
  const [dayId, setDayId] = useState<string>(courseDays[0].id);
  const [notebookId, setNotebookId] = useState<string>(courseDays[0].notebooks[0].id);
  const [query, setQuery] = useState('');
  const [completed, setCompleted] = useState<string[]>([]);
  const [expandedDays, setExpandedDays] = useState<string[]>([courseDays[0].id]);
  const [colab, setColab] = useState<ColabSettings>(DEFAULT_COLAB);

  // Progress and Colab settings live in localStorage, which only exists after hydration.
  // Reading them during render would make the server and client markup disagree.
  useEffect(() => {
    let savedProgress: string[] = [];
    try { savedProgress = JSON.parse(localStorage.getItem(STORAGE_PROGRESS) || '[]'); } catch { savedProgress = []; }
    // oxlint-disable-next-line react/react-compiler
    setCompleted(savedProgress);
    try {
      const saved = JSON.parse(localStorage.getItem(STORAGE_COLAB) || 'null');
      // oxlint-disable-next-line react/react-compiler
      if (saved?.repo) setColab({ repo: String(saved.repo), branch: String(saved.branch || 'main') });
    } catch { /* keep defaults */ }
  }, []);

  const activeDay = courseDays.find((day) => day.id === dayId) || courseDays[0];
  const activeNotebook = activeDay.notebooks.find((item) => item.id === notebookId) || activeDay.notebooks[0];
  const allNotebooks = useMemo(() => courseDays.flatMap((day) => day.notebooks.map((notebook) => ({ day, notebook }))), []);
  const searchIndex = useMemo(() => new Map(allNotebooks.map(({ notebook }) => [notebook.id, `${notebook.title} ${Object.values(notebook.guide).flat().join(' ')} ${notebook.cells.filter((cell) => cell.type === 'markdown').map((cell) => cell.source).join(' ')}`.toLowerCase()])), [allNotebooks]);
  const matches = useMemo(() => {
    const term = query.toLowerCase().trim();
    if (!term) return null;
    return new Set(allNotebooks.filter(({ notebook }) => searchIndex.get(notebook.id)?.includes(term)).map(({ notebook }) => notebook.id));
  }, [query, allNotebooks, searchIndex]);
  const progress = Math.round((completed.length / allNotebooks.length) * 100);
  const colabReady = colab.repo !== UNCONFIGURED_REPO;
  const dayColabUrl = colabUrl(colab, activeDay.masterPath);
  const lessonColabUrl = colabUrl(colab, activeNotebook.path);
  const activeIndex = allNotebooks.findIndex(({ notebook }) => notebook.id === activeNotebook.id);
  const previousLesson = activeIndex > 0 ? allNotebooks[activeIndex - 1] : null;
  const nextLesson = activeIndex < allNotebooks.length - 1 ? allNotebooks[activeIndex + 1] : null;
  const previousInDay = activeNotebook.order > 1 ? activeDay.notebooks[activeNotebook.order - 2] : null;

  function selectNotebook(day: CourseDay, notebook: Notebook) { setView('lesson'); setDayId(day.id); setNotebookId(notebook.id); if (!expandedDays.includes(day.id)) setExpandedDays((items) => [...items, day.id]); if (typeof window !== 'undefined') window.scrollTo({ top: 0 }); }
  function toggleDay(id: string) { setExpandedDays((items) => items.includes(id) ? items.filter((item) => item !== id) : [...items, id]); }
  function toggleComplete() { const next = completed.includes(activeNotebook.id) ? completed.filter((id) => id !== activeNotebook.id) : [...completed, activeNotebook.id]; setCompleted(next); localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(next)); }
  function saveColab(next: ColabSettings) { setColab(next); try { localStorage.setItem(STORAGE_COLAB, JSON.stringify(next)); } catch { /* ignore */ } }
  function resetProgress() { setCompleted([]); try { localStorage.removeItem(STORAGE_PROGRESS); } catch { /* ignore */ } }

  const colabLink = (href: string, label: string, primary = true) => colabReady
    ? <a className={primary ? 'primary-link' : 'secondary-link'} href={href} target="_blank" rel="noreferrer"><NotebookTabs />{label}</a>
    : <button type="button" className={primary ? 'primary-link' : 'secondary-link'} onClick={() => setView('start')} title="Configure the repository in Getting started first"><NotebookTabs />{label}</button>;

  return <SidebarProvider style={{ '--sidebar-width': '23rem', '--sidebar-width-icon': '4.5rem' } as CSSProperties}>
    <Sidebar className="border-r border-white/10 bg-[var(--ink)] text-white" collapsible="icon">
      <SidebarHeader className="border-b border-white/10 p-4">
        <div className="flex items-center gap-3"><div className="grid size-10 shrink-0 place-items-center rounded-xl bg-[var(--signal)] text-[var(--ink)]"><GraduationCap /></div><div className="min-w-0 group-data-[collapsible=icon]:hidden"><p className="text-[11px] font-bold uppercase tracking-[.18em] text-white/55">Course portal</p><p className="truncate font-semibold">Agentic AI Engineering</p></div><SidebarTrigger className="ml-auto text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:hidden"><PanelLeftClose /></SidebarTrigger></div>
        <div className="relative mt-3 group-data-[collapsible=icon]:hidden"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-white/40" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search lessons and theory" className="h-10 border-white/10 bg-white/7 pl-9 text-white placeholder:text-white/40" /></div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup><SidebarGroupContent className="px-2"><button type="button" onClick={() => setView('start')} className={`day-button w-full ${view === 'start' ? 'active' : ''}`}><span className="day-number" style={{ background: 'var(--signal)' }}><Rocket className="size-4" /></span><span className="min-w-0 flex-1 text-left group-data-[collapsible=icon]:hidden"><span className="block truncate text-sm font-semibold">Getting started</span><span className="block truncate text-xs text-white/45">Setup, .env file, Colab, how to study</span></span></button></SidebarGroupContent></SidebarGroup>
        <SidebarGroup><SidebarGroupLabel className="px-3 text-[11px] uppercase tracking-[.16em] text-white/40 group-data-[collapsible=icon]:hidden">Five-day path</SidebarGroupLabel><SidebarGroupContent className="space-y-1 px-2">
        {courseDays.map((day) => { const open = expandedDays.includes(day.id) || Boolean(query && day.notebooks.some((notebook) => matches?.has(notebook.id))); const dayColab = colabUrl(colab, day.masterPath); return <Collapsible key={day.id} open={open} onOpenChange={() => toggleDay(day.id)}><CollapsibleTrigger className={`day-button w-full ${view === 'lesson' && day.id === activeDay.id ? 'active' : ''}`}><span className="day-number" style={{ background: day.color }}>{day.number}</span><span className="min-w-0 flex-1 text-left group-data-[collapsible=icon]:hidden"><span className="block truncate text-sm font-semibold">{day.title}</span><span className="block truncate text-xs text-white/45">{day.notebooks.length} lessons · {day.project}</span></span>{open ? <ChevronDown className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" /> : <ChevronRight className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" />}</CollapsibleTrigger><CollapsibleContent className="ml-5 border-l border-white/12 pl-3 group-data-[collapsible=icon]:hidden">{colabReady ? <a className="day-colab-link" href={dayColab} target="_blank" rel="noreferrer"><NotebookTabs />Open complete Day {day.number} notebook in Colab<ExternalLink /></a> : <a className="day-colab-link" href={day.masterPublicPath} target="_blank" rel="noreferrer"><FileJson />Download complete Day {day.number} notebook<ExternalLink /></a>}{day.notebooks.filter((notebook) => !matches || matches.has(notebook.id)).map((notebook) => <button key={notebook.id} onClick={() => selectNotebook(day, notebook)} className={`subchapter-button ${view === 'lesson' && notebook.id === activeNotebook.id ? 'active' : ''}`}><span className="font-mono text-[11px] opacity-50">{day.number}.{notebook.order}</span><span className="line-clamp-2">{shortTitle(notebook.title)}</span>{completed.includes(notebook.id) && <Check className="ml-auto size-3.5 shrink-0 text-[var(--signal)]" />}</button>)}</CollapsibleContent></Collapsible>; })}
      </SidebarGroupContent></SidebarGroup></SidebarContent>
      <SidebarFooter className="border-t border-white/10 p-4"><div className="group-data-[collapsible=icon]:hidden"><div className="mb-2 flex justify-between text-xs"><span className="text-white/55">Course progress</span><span>{completed.length}/{allNotebooks.length}</span></div><Progress value={progress} className="[&_[data-slot=progress-indicator]]:bg-[var(--signal)] [&_[data-slot=progress-track]]:bg-white/12" /><button type="button" onClick={() => setView('start')} className="mt-3 flex w-full items-center gap-2 text-left text-[11px] text-white/45 hover:text-white"><KeyRound className="size-3.5" />{colabReady ? `Colab: ${colab.repo}` : 'Colab not configured'}</button></div><SidebarTrigger className="mx-auto hidden text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:flex"><Menu /></SidebarTrigger></SidebarFooter>
    </Sidebar>

    <SidebarInset className="min-w-0 bg-[var(--paper)]">
      {view === 'start' ? <>
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-[var(--line)] bg-[color:var(--paper)]/92 px-4 backdrop-blur-xl sm:px-7"><SidebarTrigger><Menu /></SidebarTrigger><div className="min-w-0"><p className="truncate text-sm font-semibold">Getting started</p><p className="truncate text-xs text-[var(--muted-ink)]">Setup, API key, Colab and how to study</p></div><div className="ml-auto flex items-center gap-2">{colabReady && <a className="secondary-link hidden sm:inline-flex" href={githubUrl(colab)} target="_blank" rel="noreferrer"><GitBranch />GitHub</a>}<Button onClick={() => selectNotebook(courseDays[0], courseDays[0].notebooks[0])}><Rocket />Start Day 1</Button></div></header>
        <article className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-9 sm:py-10"><div className="mb-7 border-b border-[var(--line)] pb-7"><Badge style={{ backgroundColor: 'var(--signal)', color: '#10212b' }}>Welcome</Badge><h1 className="mt-4 max-w-4xl text-3xl font-bold tracking-[-.035em] text-[var(--ink)] sm:text-4xl">Agentic AI Engineering</h1><p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted-ink)]">A five-day, project-based course: from a single model call to a reusable AI harness. Everything here mirrors the classroom notebooks, so you can read ahead, revise, or catch up.</p></div><GettingStarted key={`${colab.repo}@${colab.branch}`} settings={colab} onSettings={saveColab} onOpenLesson={() => selectNotebook(courseDays[0], courseDays[0].notebooks[0])} onResetProgress={resetProgress} /></article>
      </> : <>
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-[var(--line)] bg-[color:var(--paper)]/92 px-4 backdrop-blur-xl sm:px-7"><SidebarTrigger><Menu /></SidebarTrigger><div className="min-w-0"><p className="truncate text-sm font-semibold">Day {activeDay.number} · {activeDay.title}</p><p className="truncate text-xs text-[var(--muted-ink)]">Lesson {activeDay.number}.{activeNotebook.order}</p></div><div className="ml-auto flex items-center gap-2">{colabReady && <a className="secondary-link hidden sm:inline-flex" href={githubUrl(colab)} target="_blank" rel="noreferrer"><GitBranch />GitHub</a>}{colabLink(lessonColabUrl, 'Open this lesson in Colab')}</div></header>

        <article className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-9 sm:py-10"><div className="mb-7 border-b border-[var(--line)] pb-7"><div className="mb-4 flex flex-wrap items-center gap-2"><Badge style={{ backgroundColor: activeDay.color, color: '#10212b' }}>Day {activeDay.number}</Badge>{activeNotebook.isExercise && <Badge variant="outline">Hands-on exercise</Badge>}{activeNotebook.isProject && <Badge variant="outline">Integrated project</Badge>}<div className="top-lesson-nav"><Button variant="outline" size="sm" disabled={!previousLesson} onClick={() => previousLesson && selectNotebook(previousLesson.day, previousLesson.notebook)} aria-label="Previous lesson"><ArrowLeft />Previous</Button><span>{activeIndex + 1} of {allNotebooks.length}</span><Button variant="outline" size="sm" disabled={!nextLesson} onClick={() => nextLesson && selectNotebook(nextLesson.day, nextLesson.notebook)} aria-label="Next lesson">Next<ArrowRight /></Button></div></div><h1 className="max-w-4xl text-3xl font-bold tracking-[-.035em] text-[var(--ink)] sm:text-4xl">{shortTitle(activeNotebook.title)}</h1><p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted-ink)]">{activeNotebook.description}</p><div className="mt-5 flex flex-wrap items-center gap-2 text-sm text-[var(--muted-ink)]">{activeNotebook.theory && <span className="meta-pill"><BookOpen />Theory included</span>}<span className="meta-pill"><Code2 />{activeNotebook.codeCells} runnable cells</span><span className="meta-pill"><Network />{activeNotebook.diagrams.length} architecture view{activeNotebook.diagrams.length === 1 ? '' : 's'}</span>{activeNotebook.hasLiveObservation && <span className="meta-pill"><Sparkles />Live observation</span>}</div></div>
          <Tabs defaultValue="lesson" key={activeNotebook.id}><div className="lesson-toolbar"><TabsList className="lesson-tabs"><TabsTrigger value="lesson"><BookOpen />Learn</TabsTrigger><TabsTrigger value="code"><Code2 />Notebook</TabsTrigger><TabsTrigger value="architecture"><Network />System view</TabsTrigger></TabsList><div className="lesson-actions"><a className="secondary-link" href={activeDay.masterPublicPath} target="_blank" rel="noreferrer"><FileJson />Download full day</a>{colabLink(dayColabUrl, 'Open full day')}</div></div>
            <TabsContent value="lesson" className="mt-8"><LessonGuide day={activeDay} lesson={activeNotebook} previousTitle={previousInDay?.title} /></TabsContent>
            <TabsContent value="code" className="mt-8"><div className="mb-6"><h2 className="text-2xl font-bold">The notebook, cell by cell</h2><p className="mt-2 max-w-3xl text-[var(--muted-ink)]">This is the complete lesson notebook in reading order: every explanation, every code cell, and every checkpoint. Read a step, then run the matching cell in your own copy and compare the printed output with what the text predicts.</p><div className="mt-4 flex flex-wrap gap-2">{colabLink(lessonColabUrl, 'Open this lesson notebook', false)}<a className="secondary-link" href={activeNotebook.publicPath} target="_blank" rel="noreferrer"><FileJson />Download lesson</a></div></div><NotebookWalkthrough notebook={activeNotebook} />{!activeNotebook.codeCells && <p className="rounded-xl border border-dashed p-6 text-[var(--muted-ink)]">This lesson is conceptual and has no executable cells.</p>}</TabsContent>
            <TabsContent value="architecture" className="mt-8"><div className="mb-7"><h2 className="text-2xl font-bold">Where this lesson fits</h2><p className="mt-2 max-w-3xl text-[var(--muted-ink)]">This is the architecture used by this lesson, not a generic diagram for the day. Locate today&apos;s layer in the course spine, then follow the data and control flow below.</p><div className="course-spine">{COURSE_LAYERS.map((layer, index) => <div key={layer} className={index + 1 === activeDay.number ? 'active' : ''}><span>{index + 1}</span>{layer}{index < COURSE_LAYERS.length - 1 && <ChevronRight />}</div>)}</div></div><div className="space-y-6">{activeNotebook.diagrams.map((diagram) => <MermaidDiagram key={diagram.id} diagram={diagram} />)}</div></TabsContent>
          </Tabs>
          <footer className="mt-12 rounded-2xl border border-[var(--line)] bg-white p-5 shadow-sm"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="font-semibold">Practise this lesson</p><p className="mt-1 text-sm text-[var(--muted-ink)]">Run the notebook, change one input, observe the result, and explain what changed.</p></div><div className="flex flex-wrap gap-2"><a className="secondary-link" href={activeNotebook.publicPath} target="_blank" rel="noreferrer"><FileJson />Download lesson</a>{colabLink(lessonColabUrl, 'Run lesson in Colab')}<Button variant={completed.includes(activeNotebook.id) ? 'secondary' : 'outline'} onClick={toggleComplete}>{completed.includes(activeNotebook.id) ? <Check /> : <Circle />}{completed.includes(activeNotebook.id) ? 'Completed' : 'Mark complete'}</Button></div></div></footer>
          <nav className="lesson-pagination" aria-label="Lesson navigation"><div>{previousLesson && <button onClick={() => selectNotebook(previousLesson.day, previousLesson.notebook)}><ArrowLeft /><span><small>Previous lesson</small>{shortTitle(previousLesson.notebook.title)}</span></button>}</div><div>{nextLesson && <button className="text-right" onClick={() => selectNotebook(nextLesson.day, nextLesson.notebook)}><span><small>Next lesson</small>{shortTitle(nextLesson.notebook.title)}</span><ArrowRight /></button>}</div></nav>
        </article>
      </>}
    </SidebarInset>
  </SidebarProvider>;
}
