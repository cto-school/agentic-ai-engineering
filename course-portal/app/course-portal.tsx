'use client';

import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import { marked } from 'marked';
import { ArrowLeft, ArrowRight, BookOpen, Check, ChevronDown, ChevronRight, Circle, Code2, ExternalLink, FileJson, GitBranch, GraduationCap, KeyRound, Menu, Network, NotebookTabs, PanelLeftClose, Rocket, Search, Sparkles, Terminal } from 'lucide-react';
import { courseDays, setupGuide } from './course-data';
import { LessonWidget } from './llm-playground';
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
// Each track carries its own spine in course-data (label + last section of that layer).
const TITLE_PREFIX = /^(?:Day \d+(?:\.\d+| Project| Capstone)?|LangChain L\d+|LangGraph G\d+) — /;

marked.use({ gfm: true, breaks: false });

function renderMarkdown(source: string): string {
  const html = marked.parse(source, { async: false }) as string;
  // Notebook-relative links (../../diagrams/...) have no meaning inside the portal:
  // the same diagrams are drawn in the "System view" tab.
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
  return <div className="code-cell"><div className="code-cell-header"><span>Python · cell {index}</span><span>Run it in the notebook</span></div><pre><code>{source || '# This cell is intentionally empty'}</code></pre></div>;
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
    <div className="architecture-heading"><div className="grid size-10 place-items-center rounded-xl bg-[var(--ink)] text-white"><Network className="size-5" /></div><div><p className="eyebrow">{diagram.id} · Architecture</p><h3>{diagram.title}</h3></div></div>
    {svg && !failed && <div className="mermaid-canvas" dangerouslySetInnerHTML={{ __html: svg }} />}
    {!svg && !failed && <p className="architecture-loading">Drawing the diagram…</p>}
    {(failed || !svg) && <div className="architecture-flow">{diagram.edges.map((edge, index) => <div className="architecture-edge" key={`${edge.from}-${edge.to}-${index}`}><span>{labels.get(edge.from) || edge.from}</span><em>{edge.label ? edge.label : ''}<ChevronRight /></em><span>{labels.get(edge.to) || edge.to}</span></div>)}</div>}
    {diagram.textAlternative && <p className="architecture-note"><strong>In words:</strong> {diagram.textAlternative}</p>}
    <p className="architecture-note">Read each arrow as data or control passing from one part to another. Those hand-offs are where your code validates inputs, applies policy, and records what happened.</p>
  </section>;
}

function DayStory({ day, lessonOrder }: { day: CourseDay; lessonOrder: number }) {
  const finalSection = day.notebooks[day.projectLesson - 1]?.sectionCode ?? `${day.number}.${day.projectLesson}`;
  const unitWord = day.kind === 'day' ? 'today' : day.kind === 'track' ? 'in this track' : 'in this module';
  return <section className="day-story"><div><p className="eyebrow">{day.label} · what you {day.kind === 'module' ? 'end up with' : 'build'} {unitWord}</p><h2>{day.project}</h2><p>{day.projectBrief}</p><p className="project-signpost">The pieces come together in {day.kind === 'module' ? 'chapter' : 'section'} {finalSection}. You are not expected to understand the whole {day.kind === 'module' ? 'module' : 'project'} before then.</p></div><ol>{day.projectFlow.map((stage, index) => <li key={stage} className={lessonOrder >= Math.ceil(((index + 1) / day.projectFlow.length) * day.projectLesson) ? 'reached' : ''}><span>{index + 1}</span>{stage}</li>)}</ol></section>;
}

function CourseSpine({ day, lesson }: { day: CourseDay; lesson: Notebook }) {
  if (day.spine) {
    const layers = day.spine as [string, number][];
    const activeIndex = layers.findIndex(([, lastSection]) => lesson.order <= lastSection);
    return <div className="course-spine">{layers.map(([layer], index) => <div key={layer} className={index === activeIndex ? 'active' : ''}><span>{day.code}</span>{layer}{index < layers.length - 1 && <ChevronRight />}</div>)}</div>;
  }
  return <div className="course-spine">{COURSE_LAYERS.map((layer, index) => <div key={layer} className={index + 1 === day.number ? 'active' : ''}><span>{index + 1}</span>{layer}{index < COURSE_LAYERS.length - 1 && <ChevronRight />}</div>)}</div>;
}

function LessonGuide({ day, lesson, previousTitle }: { day: CourseDay; lesson: Notebook; previousTitle?: string }) {
  const guide = lesson.guide;
  const isModule = day.kind === 'module';
  return <div className="lesson-guide">
    {lesson.order === 1 && <DayStory day={day} lessonOrder={lesson.order} />}
    <section className="lesson-bridge"><p className="eyebrow">Where you are</p><p>{previousTitle ? <>This section builds on <strong>{shortTitle(previousTitle)}</strong>. If that idea is still fuzzy, revisit it first.</> : day.prerequisite}</p></section>
    {lesson.problem && <section className="lesson-problem"><p className="eyebrow">Why this section exists</p><p>{lesson.problem}</p></section>}
    <section><h2>The idea</h2><p>{guide.idea}</p></section>
    <section><h2>An analogy</h2><p>{guide.example}</p></section>
    <section><h2>How it works</h2><p className="section-hint">{isModule ? 'The mechanism behind the analogy, in plain words.' : 'The mechanism behind the analogy: what the graph, the model and your code actually do. The System view tab draws the same flow.'}</p>
      {guide.mechanism
        ? <ol className="guide-steps mechanism">{guide.mechanism.map((step, index) => <li key={step}><span>{index + 1}</span><p>{step}</p></li>)}</ol>
        : lesson.diagrams[0]?.textAlternative
          ? <p>{lesson.diagrams[0].textAlternative}</p>
          : <p>{guide.takeaway}</p>}
    </section>
    <section><h2>{isModule ? 'What you will do in the chapter' : 'What you will do in the notebook'}</h2><p className="section-hint">{isModule ? 'The chapter’s steps, in order.' : 'Open the Notebook tab, or the notebook in Colab, and run these in order.'}</p><ol className="guide-steps">{guide.steps.map((step, index) => <li key={step}><span>{index + 1}</span><p>{step}</p></li>)}</ol></section>
    <aside className="guide-takeaway"><p className="eyebrow">Keep this straight</p><p>{guide.takeaway}</p></aside>
    <aside className="guide-mistake"><p className="eyebrow">Common mistake</p><p>{guide.mistake}</p></aside>
    <section><h2>{isModule ? 'What to check as you go' : 'What to notice when you run it'}</h2><p>{guide.notebook}</p>{lesson.hasLiveObservation && <p className="live-note">This section holds the day&apos;s one <strong>live observation</strong>: with an API key, compare the real model&apos;s reply with the mock. Without a key, read the expected behaviour and move on.</p>}{lesson.isExercise && <p className="live-note">This is the day&apos;s <strong>hands-on exercise</strong>: try the stub, run the check, then read the commented reference solution. The rest of the day uses that solution.</p>}</section>
    {isModule
      ? <section className="section-reading"><h2>Read the chapter</h2><p className="section-hint">The full chapter: theory, step-by-step instructions and commands. Its diagrams are drawn in System view.</p>{lesson.segments.map((segment, index) => segment.type === 'widget' ? <LessonWidget key={`${lesson.id}-${index}`} id={segment.source} /> : <Markdown key={`${lesson.id}-${index}`} source={segment.source} />)}</section>
      : lesson.closing && <section className="section-reading"><h2>{/Checkpoint/.test(lesson.closing) ? 'Checkpoint and recap' : 'Recap'}</h2><p className="section-hint">{/Checkpoint/.test(lesson.closing) ? 'Try each question before opening its answer. The recap names the problem, the layer that solved it, and the evidence you saw.' : 'The problem this section solved, the layer it added, and the evidence you saw when you ran it. The full text and code live in the Notebook tab.'}</p><Markdown source={lesson.closing} /></section>}
  </div>;
}

// The map on the home page: which module answers which question, layer by layer.
const MODULE_MAP: { layer: string; question: string; units: string[] }[] = [
  { layer: 'Understand the model', question: 'What is a language model, and can I run one myself?', units: ['module_llm_foundation', 'module_ollama'] },
  { layer: 'Build the agent', question: 'How do tools, state, memory and approval fit around a model?', units: ['langgraph_track', 'langchain_track', 'module_n8n'] },
  { layer: 'Give it memory and a home', question: 'How does it remember people, and where does it live all day?', units: ['module_mem0', 'module_openclaw'] },
];
// Suggested orders through the modules. Each step is a unit id; titles come from the data.
const ROUTES: { title: string; units: string[]; why: string }[] = [
  { title: 'New to all of it', units: ['module_llm_foundation', 'module_ollama', 'langgraph_track'], why: 'See what a model does, run one on your laptop, then build agents on the runtime from first principles.' },
  { title: 'Agents without writing code', units: ['module_n8n', 'module_mem0'], why: 'Draw four agents on a canvas, then give them durable memory through a REST API.' },
  { title: 'Ship a personal assistant', units: ['module_openclaw', 'module_mem0', 'module_ollama'], why: 'Put an always-on assistant on a hardened server of your own, add memory, and compare local models.' },
  { title: 'LangGraph, then LangChain', units: ['langgraph_track', 'langchain_track'], why: 'Learn the runtime first, then the higher-level agent API built on top of it.' },
  { title: 'The guided classroom path', units: ['day_01_model_tools_agent', 'day_02_knowledge_and_state', 'day_03_memory_and_safety', 'day_04_multi_agent_systems', 'day_05_ai_harness'], why: 'Five notebooks, five projects, one exercise a day, from a model call to a reusable harness.' },
];

function unitById(id: string) {
  return courseDays.find((day) => day.id === id);
}

function unitFormat(day: CourseDay) {
  return day.kind === 'module' ? `${day.notebooks.length} chapters · guide` : `${day.notebooks.length} sections · Colab notebook`;
}

function UnitCard({ day, onOpenDay }: { day: CourseDay; onOpenDay: (day: CourseDay) => void }) {
  return <button type="button" className="day-card" onClick={() => onOpenDay(day)}><span className="day-number" style={{ background: day.color }}>{day.kind === 'day' ? day.number : day.code}</span><div><h3>{day.title}</h3><p className="day-card-project">{day.project}</p><p>{day.outcome}</p><small>{unitFormat(day)}</small></div></button>;
}

function GettingStarted({ settings, onSettings, onOpenDay, onResetProgress }: { settings: ColabSettings; onSettings: (next: ColabSettings) => void; onOpenDay: (day: CourseDay) => void; onResetProgress: () => void }) {
  // The parent remounts this form (key = saved settings) whenever the saved values change.
  const [repo, setRepo] = useState(settings.repo);
  const [branch, setBranch] = useState(settings.branch);
  const configured = settings.repo !== UNCONFIGURED_REPO;
  const standalone = courseDays.filter((day) => day.section === 'standalone');
  const days = courseDays.filter((day) => day.kind === 'day');
  return <div className="lesson-guide getting-started">
    <section className="start-hero"><p className="eyebrow">Start here</p><h2>How this site works</h2>
      <ul className="start-list">
        <li><strong>Every module stands alone.</strong> Pick the one that answers your question and start there. Nothing assumes you have read another module, and cross-references say where to look when it helps.</li>
        <li><strong>Two formats.</strong> <em>Notebook modules</em> (LangGraph, LangChain, the five days) are one Google Colab notebook each, run from top to bottom; this site shows every section with its explanations, code and diagrams. <em>Guide modules</em> (Ollama, n8n, OpenClaw, LLM Foundation, Mem0) are read here and followed on your own machine or in a browser.</li>
        <li><strong>You learn by doing.</strong> Every notebook cell does one thing and prints what happened; every guide chapter ends with something you can check.</li>
        <li><strong>No key needed to learn.</strong> Notebooks run on a built-in mock model without an API key; with your key, the same cells talk to the real model. Guide modules say up front what accounts they need.</li>
        <li><strong>Your progress stays in this browser.</strong> Mark a section complete at the bottom of its page; the sidebar keeps count.</li>
      </ul>
    </section>
    <section className="course-map"><h2>How it all connects</h2><p className="section-hint">Three layers, each answering a question. Click a module to open its first section.</p>
      <div className="module-map">{MODULE_MAP.map((row, index) => <div key={row.layer} className="map-row"><div className="map-label"><span>{index + 1}</span><strong>{row.layer}</strong><em>{row.question}</em></div><div className="map-cards">{row.units.map(unitById).filter((day): day is CourseDay => Boolean(day)).map((day) => <button type="button" key={day.id} className="map-card" onClick={() => onOpenDay(day)}><span className="day-number" style={{ background: day.color }}>{day.code}</span><span><strong>{day.title}</strong><small>{day.outcome}</small></span></button>)}</div></div>)}
        <div className="map-row map-row-days"><div className="map-label"><span>+</span><strong>Practise end to end</strong><em>The five-day path builds five projects that use every layer above.</em></div><div className="map-cards">{days.map((day) => <button type="button" key={day.id} className="map-card" onClick={() => onOpenDay(day)}><span className="day-number" style={{ background: day.color }}>{day.number}</span><span><strong>{day.title}</strong><small>{day.project}</small></span></button>)}</div></div>
      </div>
    </section>
    <section className="course-map"><h2>Choose a route</h2><p className="section-hint">Suggested orders, depending on what you want. Click a step to open it.</p>
      <div className="route-list">{ROUTES.map((route) => <div key={route.title} className="route"><strong>{route.title}</strong><div className="route-steps">{route.units.map(unitById).filter((day): day is CourseDay => Boolean(day)).map((day, index) => <span key={day.id} className="route-step">{index > 0 && <ChevronRight />}<button type="button" onClick={() => onOpenDay(day)} style={{ borderColor: day.color }}>{day.title}</button></span>)}</div><p>{route.why}</p></div>)}</div>
    </section>
    <section className="course-map"><h2>Standalone modules</h2><p className="section-hint">In the order of the sidebar: the LangGraph runtime first, the guides, and LangChain last.</p>
      <div className="day-cards">{standalone.map((day) => <UnitCard key={day.id} day={day} onOpenDay={onOpenDay} />)}</div>
    </section>
    <section className="course-map"><h2>The five-day path</h2><p className="section-hint">A guided course: each day is one notebook and one project, and each day stands on the previous one.</p>
      <div className="day-cards">{days.map((day) => <UnitCard key={day.id} day={day} onOpenDay={onOpenDay} />)}</div>
    </section>
    <section><h2>Before a notebook module</h2>
      <ol className="guide-steps">
        <li><span>1</span><p><strong>Open the module&apos;s notebook in Google Colab</strong> from the sidebar. Nothing needs installing.</p></li>
        <li><span>2</span><p><strong>Add your OpenRouter key</strong> as a Colab secret named <code>OPENROUTER_API_KEY</code> (key icon in Colab&apos;s left sidebar), or paste it when the setup cell asks. Press Enter instead to stay in mock mode.</p></li>
        <li><span>3</span><p><strong>Keep this site open next to the notebook.</strong> <em>Learn</em> gives the idea and the section&apos;s explanations, <em>Notebook</em> shows every cell, and <em>System view</em> draws the architecture.</p></li>
      </ol>
    </section>
    <section className="setup-guide"><h2>Your API key</h2><p className="section-hint">The same text opens every notebook module.</p><Markdown source={setupGuide.replace(/^##\s+Your API key.*\s*/m, '')} /></section>
    <section className="colab-settings"><h2>Google Colab links</h2>
      <p>Colab opens notebooks straight from a public GitHub repository. The course repository is set already; change it only if your instructor gives you a fork or a branch. The value is stored in this browser only.</p>
      <form className="colab-form" onSubmit={(event) => { event.preventDefault(); onSettings({ repo: repo.trim() || DEFAULT_COLAB.repo, branch: branch.trim() || 'main' }); }}>
        <div className="colab-field"><label htmlFor="colab-repo">Repository <span>owner/repository</span></label><Input id="colab-repo" value={repo} onChange={(event) => setRepo(event.target.value)} placeholder="owner/repository" /></div>
        <div className="colab-field"><label htmlFor="colab-branch">Branch</label><Input id="colab-branch" value={branch} onChange={(event) => setBranch(event.target.value)} placeholder="main" /></div>
        <Button type="submit"><Check />Save</Button>
      </form>
      <p className={`colab-status ${configured ? 'ok' : ''}`}>{configured ? <>Colab links open <code>{settings.repo}</code> on branch <code>{settings.branch}</code>.</> : 'Colab links are not configured yet: download the notebooks instead, or ask your instructor for the repository name.'}</p>
    </section>
    <section><h2>Ready?</h2><div className="start-actions"><Button onClick={() => onOpenDay(courseDays[0])}><Rocket />Start with {courseDays[0].title}</Button><Button variant="outline" onClick={onResetProgress}>Reset my progress</Button></div></section>
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
  const searchIndex = useMemo(() => new Map(allNotebooks.map(({ notebook }) => [notebook.id, `${notebook.title} ${Object.values(notebook.guide).flat().join(' ')} ${notebook.reading}`.toLowerCase()])), [allNotebooks]);
  const matches = useMemo(() => {
    const term = query.toLowerCase().trim();
    if (!term) return null;
    return new Set(allNotebooks.filter(({ notebook }) => searchIndex.get(notebook.id)?.includes(term)).map(({ notebook }) => notebook.id));
  }, [query, allNotebooks, searchIndex]);
  const progress = Math.round((completed.length / allNotebooks.length) * 100);
  const colabReady = colab.repo !== UNCONFIGURED_REPO;
  const dayColabUrl = colabUrl(colab, activeDay.masterPath);
  const isModule = activeDay.kind === 'module';
  // Previous and next stay inside the current unit: a module's chapters never spill into the next one.
  const unitIndex = activeDay.notebooks.findIndex((item) => item.id === activeNotebook.id);
  const previousLesson = unitIndex > 0 ? { day: activeDay, notebook: activeDay.notebooks[unitIndex - 1] } : null;
  const nextLesson = unitIndex < activeDay.notebooks.length - 1 ? { day: activeDay, notebook: activeDay.notebooks[unitIndex + 1] } : null;
  const previousInDay = previousLesson?.notebook ?? null;

  function selectNotebook(day: CourseDay, notebook: Notebook) { setView('lesson'); setDayId(day.id); setNotebookId(notebook.id); if (!expandedDays.includes(day.id)) setExpandedDays((items) => [...items, day.id]); if (typeof window !== 'undefined') window.scrollTo({ top: 0 }); }
  function toggleDay(id: string) { setExpandedDays((items) => items.includes(id) ? items.filter((item) => item !== id) : [...items, id]); }
  function toggleComplete() { const next = completed.includes(activeNotebook.id) ? completed.filter((id) => id !== activeNotebook.id) : [...completed, activeNotebook.id]; setCompleted(next); localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(next)); }
  function saveColab(next: ColabSettings) { setColab(next); try { localStorage.setItem(STORAGE_COLAB, JSON.stringify(next)); } catch { /* ignore */ } }
  function resetProgress() { setCompleted([]); try { localStorage.removeItem(STORAGE_PROGRESS); } catch { /* ignore */ } }

  const colabLink = (href: string, label: string, primary = true) => colabReady
    ? <a className={primary ? 'primary-link' : 'secondary-link'} href={href} target="_blank" rel="noreferrer"><NotebookTabs />{label}</a>
    : <button type="button" className={primary ? 'primary-link' : 'secondary-link'} onClick={() => setView('start')} title="Configure the repository in Getting started first"><NotebookTabs />{label}</button>;

  // One collapsible sidebar entry per day or track: the master notebook link, then its sections.
  const renderUnit = (day: CourseDay) => {
    const open = expandedDays.includes(day.id) || Boolean(query && day.notebooks.some((notebook) => matches?.has(notebook.id)));
    const dayColab = colabUrl(colab, day.masterPath);
    return <Collapsible key={day.id} open={open} onOpenChange={() => toggleDay(day.id)}><CollapsibleTrigger className={`day-button w-full ${view === 'lesson' && day.id === activeDay.id ? 'active' : ''}`}><span className="day-number" style={{ background: day.color }}>{day.code}</span><span className="min-w-0 flex-1 text-left group-data-[collapsible=icon]:hidden"><span className="block truncate text-sm font-semibold">{day.title}</span><span className="block truncate text-xs text-white/45">{day.notebooks.length} {day.kind === 'module' ? 'chapters' : 'sections'} · {day.project}</span></span>{open ? <ChevronDown className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" /> : <ChevronRight className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" />}</CollapsibleTrigger><CollapsibleContent className="ml-5 border-l border-white/12 pl-3 group-data-[collapsible=icon]:hidden">{day.masterPath ? (colabReady ? <a className="day-colab-link" href={dayColab} target="_blank" rel="noreferrer"><NotebookTabs />Open {day.name} notebook in Colab<ExternalLink /></a> : <a className="day-colab-link" href={day.masterPublicPath} target="_blank" rel="noreferrer"><FileJson />Download {day.name} notebook<ExternalLink /></a>) : null}{day.notebooks.filter((notebook) => !matches || matches.has(notebook.id)).map((notebook) => <button key={notebook.id} onClick={() => selectNotebook(day, notebook)} className={`subchapter-button ${view === 'lesson' && notebook.id === activeNotebook.id ? 'active' : ''}`}><span className="font-mono text-[11px] opacity-50">{notebook.sectionCode}</span><span className="line-clamp-2">{shortTitle(notebook.title)}</span>{completed.includes(notebook.id) && <Check className="ml-auto size-3.5 shrink-0 text-[var(--signal)]" />}</button>)}</CollapsibleContent></Collapsible>;
  };

  return <SidebarProvider style={{ '--sidebar-width': '23rem', '--sidebar-width-icon': '4.5rem' } as CSSProperties}>
    <Sidebar className="border-r border-white/10 bg-[var(--ink)] text-white" collapsible="icon">
      <SidebarHeader className="border-b border-white/10 p-4">
        <div className="flex items-center gap-3"><div className="grid size-10 shrink-0 place-items-center rounded-xl bg-[var(--signal)] text-[var(--ink)]"><GraduationCap /></div><div className="min-w-0 group-data-[collapsible=icon]:hidden"><p className="text-[11px] font-bold uppercase tracking-[.18em] text-white/55">Course portal</p><p className="truncate font-semibold">Agentic AI Engineering</p></div><SidebarTrigger className="ml-auto text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:hidden"><PanelLeftClose /></SidebarTrigger></div>
        <div className="relative mt-3 group-data-[collapsible=icon]:hidden"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-white/40" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search sections and explanations" className="h-10 border-white/10 bg-white/7 pl-9 text-white placeholder:text-white/40" /></div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup><SidebarGroupContent className="px-2"><button type="button" onClick={() => setView('start')} className={`day-button w-full ${view === 'start' ? 'active' : ''}`}><span className="day-number" style={{ background: 'var(--signal)' }}><Rocket className="size-4" /></span><span className="min-w-0 flex-1 text-left group-data-[collapsible=icon]:hidden"><span className="block truncate text-sm font-semibold">Getting started</span><span className="block truncate text-xs text-white/45">Module map, routes, API key, Colab</span></span></button></SidebarGroupContent></SidebarGroup>
        <SidebarGroup><SidebarGroupLabel className="px-3 text-[11px] uppercase tracking-[.16em] text-white/40 group-data-[collapsible=icon]:hidden">Standalone modules</SidebarGroupLabel><SidebarGroupContent className="space-y-1 px-2">
        {courseDays.filter((day) => day.section === 'standalone').map(renderUnit)}
      </SidebarGroupContent></SidebarGroup>
        <SidebarGroup><SidebarGroupLabel className="px-3 text-[11px] uppercase tracking-[.16em] text-white/40 group-data-[collapsible=icon]:hidden">Five-day path</SidebarGroupLabel><SidebarGroupContent className="space-y-1 px-2">
        {courseDays.filter((day) => day.kind === 'day').map(renderUnit)}
      </SidebarGroupContent></SidebarGroup></SidebarContent>
      <SidebarFooter className="border-t border-white/10 p-4"><div className="group-data-[collapsible=icon]:hidden"><div className="mb-2 flex justify-between text-xs"><span className="text-white/55">Sections completed</span><span>{completed.length}/{allNotebooks.length}</span></div><Progress value={progress} className="[&_[data-slot=progress-indicator]]:bg-[var(--signal)] [&_[data-slot=progress-track]]:bg-white/12" /><button type="button" onClick={() => setView('start')} className="mt-3 flex w-full items-center gap-2 text-left text-[11px] text-white/45 hover:text-white"><KeyRound className="size-3.5" />{colabReady ? `Colab: ${colab.repo}` : 'Colab not configured'}</button></div><SidebarTrigger className="mx-auto hidden text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:flex"><Menu /></SidebarTrigger></SidebarFooter>
    </Sidebar>

    <SidebarInset className="min-w-0 bg-[var(--paper)]">
      {view === 'start' ? <>
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-[var(--line)] bg-[color:var(--paper)]/92 px-4 backdrop-blur-xl sm:px-7"><SidebarTrigger><Menu /></SidebarTrigger><div className="min-w-0"><p className="truncate text-sm font-semibold">Getting started</p><p className="truncate text-xs text-[var(--muted-ink)]">Module map, routes, API key, Colab</p></div><div className="ml-auto flex items-center gap-2">{colabReady && <a className="secondary-link hidden sm:inline-flex" href={githubUrl(colab)} target="_blank" rel="noreferrer"><GitBranch />GitHub</a>}<Button onClick={() => selectNotebook(courseDays[0], courseDays[0].notebooks[0])}><Rocket />Start with {courseDays[0].title}</Button></div></header>
        <article className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-9 sm:py-10"><div className="mb-7 border-b border-[var(--line)] pb-7"><Badge style={{ backgroundColor: 'var(--signal)', color: '#10212b' }}>Welcome</Badge><h1 className="mt-4 max-w-4xl text-3xl font-bold tracking-[-.035em] text-[var(--ink)] sm:text-4xl">Agentic AI Engineering</h1><p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted-ink)]">Self-contained modules on building AI agents: the LangGraph runtime from first principles, a model on your own laptop, agents drawn in n8n, an assistant on a server you harden yourself, how a language model works inside, a memory layer, LangChain, and a five-day guided path with five projects. Read here; run in Colab or on your machine.</p></div><GettingStarted key={`${colab.repo}@${colab.branch}`} settings={colab} onSettings={saveColab} onOpenDay={(day) => selectNotebook(day, day.notebooks[0])} onResetProgress={resetProgress} /></article>
      </> : <>
        <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-[var(--line)] bg-[color:var(--paper)]/92 px-4 backdrop-blur-xl sm:px-7"><SidebarTrigger><Menu /></SidebarTrigger><div className="min-w-0"><p className="truncate text-sm font-semibold">{activeDay.label} · {activeDay.title}</p><p className="truncate text-xs text-[var(--muted-ink)]">{isModule ? 'Chapter' : 'Section'} {activeNotebook.sectionCode} of {activeDay.notebooks.length}</p></div><div className="ml-auto flex items-center gap-2">{colabReady && <a className="secondary-link hidden sm:inline-flex" href={githubUrl(colab)} target="_blank" rel="noreferrer"><GitBranch />GitHub</a>}</div></header>

        <article className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-9 sm:py-10"><div className="mb-7 border-b border-[var(--line)] pb-7"><div className="mb-4 flex flex-wrap items-center gap-2"><Badge style={{ backgroundColor: activeDay.color, color: '#10212b' }}>{activeDay.label}</Badge>{activeNotebook.isExercise && <Badge variant="outline">Hands-on exercise</Badge>}{activeNotebook.isProject && <Badge variant="outline">Project</Badge>}<div className="top-lesson-nav"><Button variant="outline" size="sm" disabled={!previousLesson} onClick={() => previousLesson && selectNotebook(previousLesson.day, previousLesson.notebook)} aria-label="Previous section"><ArrowLeft />Previous</Button><span>{unitIndex + 1} of {activeDay.notebooks.length}</span><Button variant="outline" size="sm" disabled={!nextLesson} onClick={() => nextLesson && selectNotebook(nextLesson.day, nextLesson.notebook)} aria-label="Next section">Next<ArrowRight /></Button></div></div><h1 className="max-w-4xl text-3xl font-bold tracking-[-.035em] text-[var(--ink)] sm:text-4xl">{shortTitle(activeNotebook.title)}</h1><p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted-ink)]">{activeNotebook.description}</p><div className="mt-5 flex flex-wrap items-center gap-2 text-sm text-[var(--muted-ink)]">{isModule ? <><span className="meta-pill"><BookOpen />Theory and instructions</span><span className="meta-pill"><Terminal />{activeNotebook.commandBlocks} command block{activeNotebook.commandBlocks === 1 ? '' : 's'}</span></> : <><span className="meta-pill"><BookOpen />Explanations included</span><span className="meta-pill"><Code2 />{activeNotebook.codeCells} code cells</span></>}<span className="meta-pill"><Network />{activeNotebook.diagrams.length} diagram{activeNotebook.diagrams.length === 1 ? '' : 's'}</span>{activeNotebook.hasLiveObservation && <span className="meta-pill"><Sparkles />Live observation</span>}</div></div>
          <Tabs defaultValue="lesson" key={activeNotebook.id}><div className="lesson-toolbar"><TabsList className="lesson-tabs"><TabsTrigger value="lesson"><BookOpen />Learn</TabsTrigger>{!isModule && <TabsTrigger value="code"><Code2 />Notebook</TabsTrigger>}<TabsTrigger value="architecture"><Network />System view</TabsTrigger></TabsList>{!isModule && <div className="lesson-actions">{colabLink(dayColabUrl, `Open ${activeDay.name} notebook in Colab`)}</div>}</div>
            <TabsContent value="lesson" className="mt-8"><LessonGuide day={activeDay} lesson={activeNotebook} previousTitle={previousInDay?.title} /></TabsContent>
            {!isModule && <TabsContent value="code" className="mt-8"><div className="mb-6"><h2 className="text-2xl font-bold">The notebook, cell by cell</h2><p className="mt-2 max-w-3xl text-[var(--muted-ink)]">Every explanation and every code cell of this section, in the order you run them. Definitions from earlier sections carry forward, so run the {activeDay.kind === 'day' ? 'day' : 'track'} notebook from the top rather than this section alone.</p></div><NotebookWalkthrough notebook={activeNotebook} />{!activeNotebook.codeCells && <p className="rounded-xl border border-dashed p-6 text-[var(--muted-ink)]">This section is conceptual and has no code cells.</p>}</TabsContent>}
            <TabsContent value="architecture" className="mt-8"><div className="mb-7"><h2 className="text-2xl font-bold">Where this {isModule ? 'chapter' : 'section'} fits</h2><p className="mt-2 max-w-3xl text-[var(--muted-ink)]">Find {activeDay.kind === 'day' ? "today's layer in the course spine" : isModule ? "this chapter's place in the module" : "this section's layer in the track spine"}, then follow the data and control flow for this {isModule ? 'chapter' : 'section'}.</p><CourseSpine day={activeDay} lesson={activeNotebook} /></div><div className="space-y-6">{activeNotebook.diagrams.map((diagram) => <MermaidDiagram key={diagram.id} diagram={diagram} />)}</div></TabsContent>
          </Tabs>
          <footer className="mt-12 rounded-2xl border border-[var(--line)] bg-white p-5 shadow-sm"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="font-semibold">Make it yours</p><p className="mt-1 text-sm text-[var(--muted-ink)]">{isModule ? 'Change one thing from the chapter (a model tag, a setting, a tool description), try it, and explain what changed and why.' : 'Change one input in the notebook, run the cell again, and explain what changed and why.'}</p></div><div className="flex flex-wrap gap-2"><Button variant={completed.includes(activeNotebook.id) ? 'secondary' : 'outline'} onClick={toggleComplete}>{completed.includes(activeNotebook.id) ? <Check /> : <Circle />}{completed.includes(activeNotebook.id) ? 'Completed' : 'Mark complete'}</Button></div></div></footer>
          <nav className="lesson-pagination" aria-label="Section navigation"><div>{previousLesson && <button onClick={() => selectNotebook(previousLesson.day, previousLesson.notebook)}><ArrowLeft /><span><small>Previous section</small>{shortTitle(previousLesson.notebook.title)}</span></button>}</div><div>{nextLesson && <button className="text-right" onClick={() => selectNotebook(nextLesson.day, nextLesson.notebook)}><span><small>Next section</small>{shortTitle(nextLesson.notebook.title)}</span><ArrowRight /></button>}</div></nav>
          {!nextLesson && <section className="unit-end"><div><p className="eyebrow">End of {activeDay.name}</p><p>That was the last {isModule ? 'chapter' : 'section'}. Modules stand alone, so pick the next one from the map.</p></div><Button variant="outline" onClick={() => setView('start')}><Rocket />Back to the module map</Button></section>}
        </article>
      </>}
    </SidebarInset>
  </SidebarProvider>;
}
