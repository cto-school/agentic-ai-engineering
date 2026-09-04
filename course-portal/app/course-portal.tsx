'use client';

import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties } from 'react';
import { ArrowLeft, ArrowRight, BookOpen, Check, ChevronDown, ChevronRight, Circle, Code2, ExternalLink, FileJson, GitBranch, GraduationCap, Menu, Network, NotebookTabs, PanelLeftClose, Search, Sparkles } from 'lucide-react';
import { courseDays } from './course-data';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

type CourseDay = (typeof courseDays)[number];
type Notebook = CourseDay['notebooks'][number];
const STORAGE_PROGRESS = 'agentic-course-progress';
const GITHUB_REPO = 'cto-school/agentic-ai-engineering';
const GITHUB_URL = `https://github.com/${GITHUB_REPO}`;
const COURSE_LAYERS = ['Model + tools', 'Knowledge', 'Memory + safety', 'Multi-agent', 'Harness'];

function CodeCell({ cell, index }: { cell: Notebook['codeWalkthrough'][number]; index: number }) {
  return <section className="code-study-block"><div className="code-purpose"><span>{index}</span><div><h3>{cell.title}</h3><p>{cell.explanation}</p></div></div><div className="code-cell"><div className="code-cell-header"><span>Python cell {index}</span><span>Run in Colab</span></div><pre><code>{cell.source || '# This cell is intentionally empty'}</code></pre></div></section>;
}

function DayStory({ day, lessonOrder }: { day: CourseDay; lessonOrder: number }) {
  return <section className="day-story"><div><p className="eyebrow">Day {day.number} project storyline</p><h2>{day.project}</h2><p>{day.projectBrief}</p><p className="project-signpost">The complete pieces are first assembled in Lesson {day.number}.{day.projectLesson}. You are not expected to understand the whole project before reaching it.</p></div><ol>{day.projectFlow.map((stage, index) => <li key={stage} className={lessonOrder >= Math.ceil(((index + 1) / day.projectFlow.length) * day.projectLesson) ? 'reached' : ''}><span>{index + 1}</span>{stage}</li>)}</ol></section>;
}

function LessonGuide({ guide, day, lesson, previousTitle }: { guide: Notebook['guide']; day: CourseDay; lesson: Notebook; previousTitle?: string }) {
  const projectConnection = lesson.isProject
    ? `This is an integration point: you now combine the earlier building blocks into the ${day.project} and inspect the complete flow.`
    : lesson.isExercise
      ? `This exercise isolates one important mechanism from the ${day.project} so you can prove that you understand it without relying on the completed project code.`
      : `This lesson contributes one building block to the ${day.project}. Specifically, it establishes this rule: ${guide.takeaway}`;
  return <div className="lesson-guide">
    {lesson.order === 1 && <DayStory day={day} lessonOrder={lesson.order} />}
    <section className="lesson-bridge"><p className="eyebrow">Before this lesson</p><p>{previousTitle ? <>This section builds on <strong>{previousTitle}</strong>. If that idea is unclear, revisit it before running the new cells.</> : day.prerequisite}</p></section>
    <section><h2>Build a mental picture</h2><p>{guide.example}</p></section>
    <section><h2>What happens in the system</h2><ol className="guide-steps">{guide.steps.map((step, index) => <li key={step}><span>{index + 1}</span><p>{step}</p></li>)}</ol></section>
    <aside className="guide-takeaway"><p className="eyebrow">Keep this distinction clear</p><p>{guide.takeaway}</p></aside>
    <aside className="guide-mistake"><p className="eyebrow">Common beginner mistake</p><p>{guide.mistake}</p></aside>
    <section><h2>How this lesson advances the project</h2><p>{projectConnection}</p></section>
    <section><h2>What to notice in the notebook</h2><p>{guide.notebook}</p></section>
    <section><h2>Check your understanding</h2><ul className="guide-check"><li>Why does “{guide.steps[1]}” need to happen before “{guide.steps[2]}”?</li><li>What could go wrong if a developer made this mistake: {guide.mistake}</li></ul></section>
  </div>;
}

function ArchitectureDiagram({ diagram }: { diagram: Notebook['diagrams'][number] }) {
  const labels = new Map(diagram.nodes.map((node) => [node.id, node.label]));
  return <section className="architecture-card"><div className="architecture-heading"><div className="grid size-10 place-items-center rounded-xl bg-[var(--ink)] text-white"><Network className="size-5" /></div><div><p className="eyebrow">{diagram.id} · Concept architecture</p><h3>{diagram.title}</h3></div></div><div className="architecture-flow">{diagram.edges.map((edge, index) => <div className="architecture-edge" key={`${edge.from}-${edge.to}-${index}`}><span>{labels.get(edge.from) || edge.from}</span><ChevronRight /><span>{labels.get(edge.to) || edge.to}</span></div>)}</div><p className="architecture-note">Read each arrow as a transfer of data or control. These boundaries are where the application can validate inputs, enforce policy, and record events.</p></section>;
}

export function CoursePortal() {
  const [dayId, setDayId] = useState<string>(courseDays[0].id);
  const [notebookId, setNotebookId] = useState<string>(courseDays[0].notebooks[0].id);
  const [query, setQuery] = useState('');
  const [completed, setCompleted] = useState<string[]>([]);
  const [expandedDays, setExpandedDays] = useState<string[]>([courseDays[0].id]);

  useEffect(() => {
    let savedProgress: string[] = [];
    try { savedProgress = JSON.parse(localStorage.getItem(STORAGE_PROGRESS) || '[]'); } catch { savedProgress = []; }
    setCompleted(savedProgress);
  }, []);

  const activeDay = courseDays.find((day) => day.id === dayId) || courseDays[0];
  const activeNotebook = activeDay.notebooks.find((item) => item.id === notebookId) || activeDay.notebooks[0];
  const allNotebooks = useMemo(() => courseDays.flatMap((day) => day.notebooks.map((notebook) => ({ day, notebook }))), []);
  const matches = useMemo(() => { const term = query.toLowerCase().trim(); return term ? new Set(allNotebooks.filter(({ notebook }) => `${notebook.title} ${notebook.description} ${Object.values(notebook.guide).flat().join(' ')}`.toLowerCase().includes(term)).map(({ notebook }) => notebook.id)) : null; }, [query, allNotebooks]);
  const progress = Math.round((completed.length / allNotebooks.length) * 100);
  const dayColabUrl = `https://colab.research.google.com/github/${GITHUB_REPO}/blob/main/${activeDay.masterPath}`;
  const lessonColabUrl = `https://colab.research.google.com/github/${GITHUB_REPO}/blob/main/${activeNotebook.path}`;
  const activeIndex = allNotebooks.findIndex(({ notebook }) => notebook.id === activeNotebook.id);
  const previousLesson = activeIndex > 0 ? allNotebooks[activeIndex - 1] : null;
  const nextLesson = activeIndex < allNotebooks.length - 1 ? allNotebooks[activeIndex + 1] : null;
  const previousInDay = activeNotebook.order > 1 ? activeDay.notebooks[activeNotebook.order - 2] : null;

  function selectNotebook(day: CourseDay, notebook: Notebook) { setDayId(day.id); setNotebookId(notebook.id); if (!expandedDays.includes(day.id)) setExpandedDays((items) => [...items, day.id]); }
  function toggleDay(id: string) { setExpandedDays((items) => items.includes(id) ? items.filter((item) => item !== id) : [...items, id]); }
  function toggleComplete() { const next = completed.includes(activeNotebook.id) ? completed.filter((id) => id !== activeNotebook.id) : [...completed, activeNotebook.id]; setCompleted(next); localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(next)); }

  return <SidebarProvider style={{ '--sidebar-width': '23rem', '--sidebar-width-icon': '4.5rem' } as CSSProperties}>
    <Sidebar className="border-r border-white/10 bg-[var(--ink)] text-white" collapsible="icon">
      <SidebarHeader className="border-b border-white/10 p-4">
        <div className="flex items-center gap-3"><div className="grid size-10 shrink-0 place-items-center rounded-xl bg-[var(--signal)] text-[var(--ink)]"><GraduationCap /></div><div className="min-w-0 group-data-[collapsible=icon]:hidden"><p className="text-[11px] font-bold uppercase tracking-[.18em] text-white/55">Course portal</p><p className="truncate font-semibold">Agentic AI Engineering</p></div><SidebarTrigger className="ml-auto text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:hidden"><PanelLeftClose /></SidebarTrigger></div>
        <div className="relative mt-3 group-data-[collapsible=icon]:hidden"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-white/40" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search lessons" className="h-10 border-white/10 bg-white/7 pl-9 text-white placeholder:text-white/40" /></div>
      </SidebarHeader>
      <SidebarContent><SidebarGroup><SidebarGroupLabel className="px-3 text-[11px] uppercase tracking-[.16em] text-white/40 group-data-[collapsible=icon]:hidden">Five-day path</SidebarGroupLabel><SidebarGroupContent className="space-y-1 px-2">
        {courseDays.map((day) => { const open = expandedDays.includes(day.id) || Boolean(query && day.notebooks.some((notebook) => matches?.has(notebook.id))); const dayColab = `https://colab.research.google.com/github/${GITHUB_REPO}/blob/main/${day.masterPath}`; return <Collapsible key={day.id} open={open} onOpenChange={() => toggleDay(day.id)}><CollapsibleTrigger className={`day-button w-full ${day.id === activeDay.id ? 'active' : ''}`}><span className="day-number" style={{ background: day.color }}>{day.number}</span><span className="min-w-0 flex-1 text-left group-data-[collapsible=icon]:hidden"><span className="block truncate text-sm font-semibold">{day.title}</span><span className="block truncate text-xs text-white/45">{day.notebooks.length} sections · one notebook</span></span>{open ? <ChevronDown className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" /> : <ChevronRight className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" />}</CollapsibleTrigger><CollapsibleContent className="ml-5 border-l border-white/12 pl-3 group-data-[collapsible=icon]:hidden"><a className="day-colab-link" href={dayColab} target="_blank" rel="noreferrer"><NotebookTabs />Open complete Day {day.number} notebook<ExternalLink /></a>{day.notebooks.filter((notebook) => !matches || matches.has(notebook.id)).map((notebook) => <button key={notebook.id} onClick={() => selectNotebook(day, notebook)} className={`subchapter-button ${notebook.id === activeNotebook.id ? 'active' : ''}`}><span className="font-mono text-[11px] opacity-50">{day.number}.{notebook.order}</span><span className="line-clamp-2">{notebook.title.replace(/^Day \d+\.\d+ — /, '')}</span>{completed.includes(notebook.id) && <Check className="ml-auto size-3.5 shrink-0 text-[var(--signal)]" />}</button>)}</CollapsibleContent></Collapsible>; })}
      </SidebarGroupContent></SidebarGroup></SidebarContent>
      <SidebarFooter className="border-t border-white/10 p-4"><div className="group-data-[collapsible=icon]:hidden"><div className="mb-2 flex justify-between text-xs"><span className="text-white/55">Course progress</span><span>{completed.length}/{allNotebooks.length}</span></div><Progress value={progress} className="[&_[data-slot=progress-indicator]]:bg-[var(--signal)] [&_[data-slot=progress-track]]:bg-white/12" /></div><SidebarTrigger className="mx-auto hidden text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:flex"><Menu /></SidebarTrigger></SidebarFooter>
    </Sidebar>

    <SidebarInset className="min-w-0 bg-[var(--paper)]">
      <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-[var(--line)] bg-[color:var(--paper)]/92 px-4 backdrop-blur-xl sm:px-7"><SidebarTrigger><Menu /></SidebarTrigger><div className="min-w-0"><p className="truncate text-sm font-semibold">Day {activeDay.number} · {activeDay.title}</p><p className="truncate text-xs text-[var(--muted-ink)]">Lesson {activeDay.number}.{activeNotebook.order}</p></div><div className="ml-auto flex items-center gap-2"><a className="secondary-link hidden sm:inline-flex" href={GITHUB_URL} target="_blank" rel="noreferrer"><GitBranch />GitHub</a><a className="primary-link" href={lessonColabUrl} target="_blank" rel="noreferrer"><ExternalLink />Open this lesson</a></div></header>

      <article className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-9 sm:py-10"><div className="mb-7 border-b border-[var(--line)] pb-7"><div className="mb-4 flex flex-wrap items-center gap-2"><Badge style={{ backgroundColor: activeDay.color, color: '#10212b' }}>Day {activeDay.number}</Badge>{activeNotebook.isExercise && <Badge variant="outline">Hands-on exercise</Badge>}{activeNotebook.isProject && <Badge variant="outline">Integrated project</Badge>}<div className="top-lesson-nav"><Button variant="outline" size="sm" disabled={!previousLesson} onClick={() => previousLesson && selectNotebook(previousLesson.day, previousLesson.notebook)} aria-label="Previous lesson"><ArrowLeft />Previous</Button><span>{activeIndex + 1} of {allNotebooks.length}</span><Button variant="outline" size="sm" disabled={!nextLesson} onClick={() => nextLesson && selectNotebook(nextLesson.day, nextLesson.notebook)} aria-label="Next lesson">Next<ArrowRight /></Button></div></div><h1 className="max-w-4xl text-3xl font-bold tracking-[-.035em] text-[var(--ink)] sm:text-4xl">{activeNotebook.title}</h1><p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted-ink)]">{activeNotebook.description}</p><div className="mt-5 flex flex-wrap items-center gap-2 text-sm text-[var(--muted-ink)]"><span className="meta-pill"><BookOpen />Theory included</span><span className="meta-pill"><Code2 />{activeNotebook.codeCells} runnable cells</span><span className="meta-pill"><Network />{activeNotebook.diagrams.length} architecture view</span>{activeNotebook.hasLiveObservation && <span className="meta-pill"><Sparkles />Live observation</span>}</div></div>
        <Tabs defaultValue="lesson" key={activeNotebook.id}><div className="lesson-toolbar"><TabsList className="lesson-tabs"><TabsTrigger value="lesson"><BookOpen />Learn</TabsTrigger><TabsTrigger value="code"><Code2 />Study the code</TabsTrigger><TabsTrigger value="architecture"><Network />System view</TabsTrigger></TabsList><div className="lesson-actions"><a className="secondary-link" href={activeDay.masterPublicPath} target="_blank" rel="noreferrer"><FileJson />Download full day</a><a className="primary-link" href={dayColabUrl} target="_blank" rel="noreferrer"><NotebookTabs />Open full day</a></div></div><TabsContent value="lesson" className="mt-8"><LessonGuide guide={activeNotebook.guide} day={activeDay} lesson={activeNotebook} previousTitle={previousInDay?.title} /></TabsContent><TabsContent value="code" className="mt-8"><div className="mb-6"><h2 className="text-2xl font-bold">Read the code as a sequence</h2><p className="mt-2 max-w-3xl text-[var(--muted-ink)]">Each block explains why the next cell exists. Read the purpose first, inspect the code, then run the independent lesson notebook to experiment without losing your place in the full-day notebook.</p><a className="secondary-link mt-4" href={lessonColabUrl} target="_blank" rel="noreferrer"><NotebookTabs />Open this lesson notebook</a></div><div className="space-y-7">{activeNotebook.codeWalkthrough.map((cell, index) => <CodeCell key={index} cell={cell} index={index + 1} />)}{!activeNotebook.codeCells && <p className="rounded-xl border border-dashed p-6 text-[var(--muted-ink)]">This lesson is conceptual and has no executable cells.</p>}</div></TabsContent><TabsContent value="architecture" className="mt-8"><div className="mb-7"><h2 className="text-2xl font-bold">Where this lesson fits</h2><p className="mt-2 max-w-3xl text-[var(--muted-ink)]">This is the architecture used by this lesson—not a generic diagram for the day. Locate today’s layer in the course spine, then follow the data and control flow below.</p><div className="course-spine">{COURSE_LAYERS.map((layer, index) => <div key={layer} className={index + 1 === activeDay.number ? 'active' : ''}><span>{index + 1}</span>{layer}{index < COURSE_LAYERS.length - 1 && <ChevronRight />}</div>)}</div></div><div className="space-y-6">{activeNotebook.diagrams.map((diagram) => <ArchitectureDiagram key={diagram.id} diagram={diagram} />)}</div></TabsContent></Tabs>
        <footer className="mt-12 rounded-2xl border border-[var(--line)] bg-white p-5 shadow-sm"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="font-semibold">Practise this lesson</p><p className="mt-1 text-sm text-[var(--muted-ink)]">Run the independent notebook, change one input, observe the result, and explain what changed.</p></div><div className="flex flex-wrap gap-2"><a className="secondary-link" href={activeNotebook.publicPath} target="_blank" rel="noreferrer"><FileJson />Download lesson</a><a className="primary-link" href={lessonColabUrl} target="_blank" rel="noreferrer"><NotebookTabs />Run lesson in Colab</a><Button variant={completed.includes(activeNotebook.id) ? 'secondary' : 'outline'} onClick={toggleComplete}>{completed.includes(activeNotebook.id) ? <Check /> : <Circle />}{completed.includes(activeNotebook.id) ? 'Completed' : 'Mark complete'}</Button></div></div></footer>
        <nav className="lesson-pagination" aria-label="Lesson navigation"><div>{previousLesson && <button onClick={() => selectNotebook(previousLesson.day, previousLesson.notebook)}><ArrowLeft /><span><small>Previous lesson</small>{previousLesson.notebook.title.replace(/^Day \d+\.\d+ — /, '')}</span></button>}</div><div>{nextLesson && <button className="text-right" onClick={() => selectNotebook(nextLesson.day, nextLesson.notebook)}><span><small>Next lesson</small>{nextLesson.notebook.title.replace(/^Day \d+\.\d+ — /, '')}</span><ArrowRight /></button>}</div></nav>
      </article>
    </SidebarInset>
  </SidebarProvider>;
}
