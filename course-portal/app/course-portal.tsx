'use client';

import { useEffect, useMemo, useState } from 'react';
import type { CSSProperties, ReactNode } from 'react';
import { BookOpen, Check, ChevronDown, ChevronRight, Circle, Code2, ExternalLink, FileJson, GitBranch, GraduationCap, Menu, Network, NotebookTabs, PanelLeftClose, Search, Settings2, Sparkles } from 'lucide-react';
import { courseDays } from './course-data';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Sidebar, SidebarContent, SidebarFooter, SidebarGroup, SidebarGroupContent, SidebarGroupLabel, SidebarHeader, SidebarInset, SidebarProvider, SidebarTrigger } from '@/components/ui/sidebar';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from '@/components/ui/collapsible';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';

type CourseDay = (typeof courseDays)[number];
type Notebook = CourseDay['notebooks'][number];
const STORAGE_REPO = 'agentic-course-github-repo';
const STORAGE_BRANCH = 'agentic-course-github-branch';
const STORAGE_PROGRESS = 'agentic-course-progress';

function inline(text: string) {
  return text.split(/(`[^`]+`|\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))/g).map((part, index) => {
    if (part.startsWith('`') && part.endsWith('`')) return <code key={index}>{part.slice(1, -1)}</code>;
    if (part.startsWith('**') && part.endsWith('**')) return <strong key={index}>{part.slice(2, -2)}</strong>;
    const link = part.match(/^\[([^\]]+)\]\(([^)]+)\)$/);
    if (link) return <span key={index} className="text-[var(--teal)] underline decoration-dotted">{link[1]}</span>;
    return part;
  });
}

function MarkdownReader({ source }: { source: string }) {
  const blocks: ReactNode[] = [];
  let code: string[] = [], paragraph: string[] = [], list: string[] = [];
  let inCode = false;
  const flushParagraph = () => { if (paragraph.length) blocks.push(<p key={`p-${blocks.length}`}>{inline(paragraph.join(' '))}</p>); paragraph = []; };
  const flushList = () => { if (list.length) blocks.push(<ul key={`l-${blocks.length}`}>{list.map((item, i) => <li key={i}>{inline(item)}</li>)}</ul>); list = []; };
  for (const line of source.split('\n')) {
    if (line.startsWith('```')) { flushParagraph(); flushList(); if (inCode) { blocks.push(<pre key={`c-${blocks.length}`}><code>{code.join('\n')}</code></pre>); code = []; } inCode = !inCode; continue; }
    if (inCode) { code.push(line); continue; }
    if (/^#{1,4}\s/.test(line)) { flushParagraph(); flushList(); const level = line.match(/^#+/)?.[0].length || 2; const value = line.replace(/^#+\s*/, ''); if (level === 1) continue; blocks.push(level === 2 ? <h2 key={`h-${blocks.length}`}>{inline(value)}</h2> : <h3 key={`h-${blocks.length}`}>{inline(value)}</h3>); }
    else if (/^[-*]\s+/.test(line)) { flushParagraph(); list.push(line.replace(/^[-*]\s+/, '')); }
    else if (/^\d+\.\s+/.test(line)) { flushParagraph(); list.push(line.replace(/^\d+\.\s+/, '')); }
    else if (line.trim() === '---') { flushParagraph(); flushList(); blocks.push(<hr key={`r-${blocks.length}`} />); }
    else if (!line.trim()) { flushParagraph(); flushList(); }
    else if (!line.startsWith('Architecture reference:')) paragraph.push(line.replace(/^>\s?/, ''));
  }
  flushParagraph(); flushList();
  return <div className="lesson-prose">{blocks}</div>;
}

function CodeCell({ source, index }: { source: string; index: number }) {
  return <section className="code-cell"><div className="code-cell-header"><span>Python cell {index}</span><span>Run in Colab</span></div><pre><code>{source || '# This cell is intentionally empty'}</code></pre></section>;
}

function ArchitectureDiagram({ diagram }: { diagram: Notebook['diagrams'][number] }) {
  const labels = new Map(diagram.nodes.map((node) => [node.id, node.label]));
  return <section className="architecture-card"><div className="architecture-heading"><div className="grid size-10 place-items-center rounded-xl bg-[var(--ink)] text-white"><Network className="size-5" /></div><div><p className="eyebrow">{diagram.id}</p><h3>{diagram.title}</h3></div></div><div className="architecture-flow">{diagram.edges.map((edge, index) => <div className="architecture-edge" key={`${edge.from}-${edge.to}-${index}`}><span>{labels.get(edge.from) || edge.from}</span><ChevronRight /><span>{labels.get(edge.to) || edge.to}</span></div>)}</div></section>;
}

function normaliseRepo(value: string) { return value.trim().replace(/^https?:\/\/github\.com\//, '').replace(/\.git$/, '').replace(/^\/+|\/+$/g, ''); }

export function CoursePortal() {
  const [dayId, setDayId] = useState<string>(courseDays[0].id);
  const [notebookId, setNotebookId] = useState<string>(courseDays[0].notebooks[0].id);
  const [query, setQuery] = useState('');
  const [repo, setRepo] = useState('');
  const [repoDraft, setRepoDraft] = useState('');
  const [branch, setBranch] = useState('main');
  const [branchDraft, setBranchDraft] = useState('main');
  const [completed, setCompleted] = useState<string[]>([]);
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [expandedDays, setExpandedDays] = useState<string[]>([courseDays[0].id]);

  useEffect(() => {
    const savedRepo = localStorage.getItem(STORAGE_REPO) || '';
    const savedBranch = localStorage.getItem(STORAGE_BRANCH) || 'main';
    let savedProgress: string[] = [];
    try { savedProgress = JSON.parse(localStorage.getItem(STORAGE_PROGRESS) || '[]'); } catch { savedProgress = []; }
    setRepo(savedRepo); setRepoDraft(savedRepo); setBranch(savedBranch); setBranchDraft(savedBranch); setCompleted(savedProgress);
  }, []);

  const activeDay = courseDays.find((day) => day.id === dayId) || courseDays[0];
  const activeNotebook = activeDay.notebooks.find((item) => item.id === notebookId) || activeDay.notebooks[0];
  const allNotebooks = useMemo(() => courseDays.flatMap((day) => day.notebooks.map((notebook) => ({ day, notebook }))), []);
  const matches = useMemo(() => { const term = query.toLowerCase().trim(); return term ? new Set(allNotebooks.filter(({ notebook }) => `${notebook.title} ${notebook.description} ${notebook.theory}`.toLowerCase().includes(term)).map(({ notebook }) => notebook.id)) : null; }, [query, allNotebooks]);
  const progress = Math.round((completed.length / allNotebooks.length) * 100);
  const colabUrl = repo ? `https://colab.research.google.com/github/${normaliseRepo(repo)}/blob/${branch}/${activeNotebook.path}` : '';

  function selectNotebook(day: CourseDay, notebook: Notebook) { setDayId(day.id); setNotebookId(notebook.id); if (!expandedDays.includes(day.id)) setExpandedDays((items) => [...items, day.id]); }
  function toggleDay(id: string) { setExpandedDays((items) => items.includes(id) ? items.filter((item) => item !== id) : [...items, id]); }
  function toggleComplete() { const next = completed.includes(activeNotebook.id) ? completed.filter((id) => id !== activeNotebook.id) : [...completed, activeNotebook.id]; setCompleted(next); localStorage.setItem(STORAGE_PROGRESS, JSON.stringify(next)); }
  function saveRepo() { const clean = normaliseRepo(repoDraft); setRepo(clean); setRepoDraft(clean); setBranch(branchDraft || 'main'); localStorage.setItem(STORAGE_REPO, clean); localStorage.setItem(STORAGE_BRANCH, branchDraft || 'main'); setSettingsOpen(false); }

  return <SidebarProvider style={{ '--sidebar-width': '23rem', '--sidebar-width-icon': '4.5rem' } as CSSProperties}>
    <Sidebar className="border-r border-white/10 bg-[var(--ink)] text-white" collapsible="icon">
      <SidebarHeader className="border-b border-white/10 p-4">
        <div className="flex items-center gap-3"><div className="grid size-10 shrink-0 place-items-center rounded-xl bg-[var(--signal)] text-[var(--ink)]"><GraduationCap /></div><div className="min-w-0 group-data-[collapsible=icon]:hidden"><p className="text-[11px] font-bold uppercase tracking-[.18em] text-white/55">Course portal</p><p className="truncate font-semibold">Agentic AI Engineering</p></div><SidebarTrigger className="ml-auto text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:hidden"><PanelLeftClose /></SidebarTrigger></div>
        <div className="relative mt-3 group-data-[collapsible=icon]:hidden"><Search className="absolute left-3 top-1/2 size-4 -translate-y-1/2 text-white/40" /><Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search lessons" className="h-10 border-white/10 bg-white/7 pl-9 text-white placeholder:text-white/40" /></div>
      </SidebarHeader>
      <SidebarContent><SidebarGroup><SidebarGroupLabel className="px-3 text-[11px] uppercase tracking-[.16em] text-white/40 group-data-[collapsible=icon]:hidden">Five-day path</SidebarGroupLabel><SidebarGroupContent className="space-y-1 px-2">
        {courseDays.map((day) => { const open = expandedDays.includes(day.id) || Boolean(query && day.notebooks.some((notebook) => matches?.has(notebook.id))); return <Collapsible key={day.id} open={open} onOpenChange={() => toggleDay(day.id)}><CollapsibleTrigger className={`day-button w-full ${day.id === activeDay.id ? 'active' : ''}`}><span className="day-number" style={{ background: day.color }}>{day.number}</span><span className="min-w-0 flex-1 text-left group-data-[collapsible=icon]:hidden"><span className="block truncate text-sm font-semibold">{day.title}</span><span className="block truncate text-xs text-white/45">{day.notebooks.length} lessons · {day.short}</span></span>{open ? <ChevronDown className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" /> : <ChevronRight className="size-4 opacity-50 group-data-[collapsible=icon]:hidden" />}</CollapsibleTrigger><CollapsibleContent className="ml-5 border-l border-white/12 pl-3 group-data-[collapsible=icon]:hidden">{day.notebooks.filter((notebook) => !matches || matches.has(notebook.id)).map((notebook) => <button key={notebook.id} onClick={() => selectNotebook(day, notebook)} className={`subchapter-button ${notebook.id === activeNotebook.id ? 'active' : ''}`}><span className="font-mono text-[11px] opacity-50">{day.number}.{notebook.order}</span><span className="line-clamp-2">{notebook.title.replace(/^Day \d+\.\d+ — /, '')}</span>{completed.includes(notebook.id) && <Check className="ml-auto size-3.5 shrink-0 text-[var(--signal)]" />}</button>)}</CollapsibleContent></Collapsible>; })}
      </SidebarGroupContent></SidebarGroup></SidebarContent>
      <SidebarFooter className="border-t border-white/10 p-4"><div className="group-data-[collapsible=icon]:hidden"><div className="mb-2 flex justify-between text-xs"><span className="text-white/55">Course progress</span><span>{completed.length}/{allNotebooks.length}</span></div><Progress value={progress} className="[&_[data-slot=progress-indicator]]:bg-[var(--signal)] [&_[data-slot=progress-track]]:bg-white/12" /></div><SidebarTrigger className="mx-auto hidden text-white hover:bg-white/10 hover:text-white group-data-[collapsible=icon]:flex"><Menu /></SidebarTrigger></SidebarFooter>
    </Sidebar>

    <SidebarInset className="min-w-0 bg-[var(--paper)]">
      <header className="sticky top-0 z-20 flex h-16 items-center gap-3 border-b border-[var(--line)] bg-[color:var(--paper)]/92 px-4 backdrop-blur-xl sm:px-7"><SidebarTrigger><Menu /></SidebarTrigger><div className="min-w-0"><p className="text-xs font-semibold uppercase tracking-[.14em] text-[var(--muted-ink)]">Day {activeDay.number} · {activeDay.project}</p><p className="truncate font-semibold">{activeNotebook.title}</p></div><div className="ml-auto flex items-center gap-2"><Dialog open={settingsOpen} onOpenChange={setSettingsOpen}><DialogTrigger render={<Button variant="outline" size="sm" />}><Settings2 /><span className="hidden sm:inline">Colab setup</span></DialogTrigger><DialogContent className="sm:max-w-md"><DialogHeader><DialogTitle>Connect the GitHub repository</DialogTitle><DialogDescription>Enter the public repository once to activate every Colab link. This stays in your browser.</DialogDescription></DialogHeader><label className="grid gap-2 text-sm font-medium">GitHub repository<Input value={repoDraft} onChange={(event) => setRepoDraft(event.target.value)} placeholder="organisation/repository" /></label><label className="grid gap-2 text-sm font-medium">Branch<Input value={branchDraft} onChange={(event) => setBranchDraft(event.target.value)} placeholder="main" /></label><DialogFooter><Button onClick={saveRepo}>Save Colab setup</Button></DialogFooter></DialogContent></Dialog>{colabUrl ? <a className="primary-link" href={colabUrl} target="_blank" rel="noreferrer"><ExternalLink />Open in Colab</a> : <Button onClick={() => setSettingsOpen(true)}><ExternalLink />Open in Colab</Button>}</div></header>

      <article className="mx-auto w-full max-w-5xl px-5 py-8 sm:px-9 sm:py-10"><div className="mb-7 border-b border-[var(--line)] pb-7"><div className="mb-4 flex flex-wrap gap-2"><Badge style={{ backgroundColor: activeDay.color, color: '#10212b' }}>Day {activeDay.number}</Badge>{activeNotebook.isExercise && <Badge variant="outline">Hands-on exercise</Badge>}{activeNotebook.isProject && <Badge variant="outline">Integrated project</Badge>}</div><h1 className="max-w-4xl text-3xl font-bold tracking-[-.035em] text-[var(--ink)] sm:text-4xl">{activeNotebook.title}</h1><p className="mt-3 max-w-3xl text-base leading-7 text-[var(--muted-ink)]">{activeNotebook.description}</p><div className="mt-5 flex flex-wrap items-center gap-2 text-sm text-[var(--muted-ink)]"><span className="meta-pill"><BookOpen />Theory included</span><span className="meta-pill"><Code2 />{activeNotebook.codeCells} runnable cells</span><span className="meta-pill"><Network />{activeNotebook.diagrams.length} architecture view</span>{activeNotebook.hasLiveObservation && <span className="meta-pill"><Sparkles />Live observation</span>}</div></div>
        <Tabs defaultValue="lesson" key={activeNotebook.id}><TabsList className="lesson-tabs"><TabsTrigger value="lesson"><BookOpen />Theory</TabsTrigger><TabsTrigger value="code"><Code2 />Code</TabsTrigger><TabsTrigger value="architecture"><Network />Architecture</TabsTrigger></TabsList><TabsContent value="lesson" className="mt-8"><MarkdownReader source={activeNotebook.reading} /></TabsContent><TabsContent value="code" className="mt-8"><div className="mb-6"><h2 className="text-2xl font-bold">Notebook code</h2><p className="mt-2 text-[var(--muted-ink)]">Read the cells here, then run and modify them in Colab.</p></div><div className="space-y-5">{activeNotebook.cells.filter((cell) => cell.type === 'code').map((cell, index) => <CodeCell key={cell.id} source={cell.source} index={index + 1} />)}{!activeNotebook.codeCells && <p className="rounded-xl border border-dashed p-6 text-[var(--muted-ink)]">This lesson is conceptual and has no executable cells.</p>}</div></TabsContent><TabsContent value="architecture" className="mt-8"><div className="mb-6"><h2 className="text-2xl font-bold">How the system fits together</h2><p className="mt-2 text-[var(--muted-ink)]">Each row is a real connection in the architecture. Follow the arrows to trace information and control flow.</p></div><div className="space-y-6">{activeNotebook.diagrams.map((diagram) => <ArchitectureDiagram key={diagram.id} diagram={diagram} />)}</div></TabsContent></Tabs>
        <footer className="mt-12 rounded-2xl border border-[var(--line)] bg-white p-5 shadow-sm"><div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center"><div><p className="font-semibold">Continue in the notebook</p><p className="mt-1 text-sm text-[var(--muted-ink)]">Run the code, complete the exercise, then mark this lesson complete.</p></div><div className="flex flex-wrap gap-2"><a className="secondary-link" href={activeNotebook.publicPath} target="_blank" rel="noreferrer"><FileJson />Open notebook file</a>{colabUrl ? <a className="primary-link" href={colabUrl} target="_blank" rel="noreferrer"><NotebookTabs />Open in Colab</a> : <Button onClick={() => setSettingsOpen(true)}><GitBranch />Configure GitHub</Button>}<Button variant={completed.includes(activeNotebook.id) ? 'secondary' : 'outline'} onClick={toggleComplete}>{completed.includes(activeNotebook.id) ? <Check /> : <Circle />}{completed.includes(activeNotebook.id) ? 'Completed' : 'Mark complete'}</Button></div></div></footer>
      </article>
    </SidebarInset>
  </SidebarProvider>;
}
