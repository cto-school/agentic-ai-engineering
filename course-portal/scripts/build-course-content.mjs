import fs from 'node:fs';
import path from 'node:path';

const siteRoot = path.resolve(import.meta.dirname, '..');
const courseRoot = path.resolve(siteRoot, '..');
const outputRoot = path.join(siteRoot, 'public', 'notebooks');

const days = [
  { dir: 'day_01_model_tools_agent', short: 'Foundations', title: 'Model, Tools & Agent', project: 'Smart Research Assistant', color: '#ef8354' },
  { dir: 'day_02_knowledge_and_state', short: 'Knowledge', title: 'Knowledge, RAG & State', project: 'Engineering Knowledge Assistant', color: '#41b3a3' },
  { dir: 'day_03_memory_and_safety', short: 'Safety', title: 'Memory, Guardrails & Safety', project: 'Safe Personal Task Agent', color: '#7a6ff0' },
  { dir: 'day_04_multi_agent_systems', short: 'Coordination', title: 'Multi-Agent Systems', project: 'Engineering Design Review Team', color: '#de9e36' },
  { dir: 'day_05_ai_harness', short: 'Runtime', title: 'Harness & Automation', project: 'Mini Harness + Website Maintenance Agent', color: '#3085c3' },
];

function plainTitle(source, fallback) {
  const match = source.match(/^#\s+(.+)$/m);
  return match ? match[1].replace(/[*`]/g, '').trim() : fallback;
}

function description(markdown) {
  const paragraphs = markdown
    .split(/\n\s*\n/)
    .map((part) => part.replace(/^#+\s+.*$/gm, '').replace(/[*`>#-]/g, '').replace(/\s+/g, ' ').trim())
    .filter((part) => part.length > 40 && !part.startsWith('Architecture reference'));
  return (paragraphs[0] || 'Interactive course notebook').slice(0, 180);
}

function diagramCatalog(dayNumber) {
  const file = path.join(courseRoot, 'diagrams', 'source', `day_${String(dayNumber).padStart(2, '0')}.md`);
  const source = fs.readFileSync(file, 'utf8');
  const entries = [];
  const pattern = /^##\s+(D\d+)\s+—\s+(.+?)\s*$[\s\S]*?```mermaid\s*\n([\s\S]*?)```/gm;
  for (const match of source.matchAll(pattern)) {
    const mermaid = match[3].trim();
    const labels = new Map();
    for (const node of mermaid.matchAll(/([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\{|\()+(?:\"?)([^\]})\"]+)(?:\"?)(?:\]|\}|\))+/g)) labels.set(node[1], node[2]);
    const edges = [];
    for (const line of mermaid.split('\n')) {
      const parts = line.trim().split(/-->(?:\|[^|]*\|)?/);
      if (parts.length < 2) continue;
      const ids = parts.map((part) => part.match(/([A-Za-z][A-Za-z0-9_]*)/)?.[1]).filter(Boolean);
      for (let index = 0; index < ids.length - 1; index += 1) edges.push({ from: ids[index], to: ids[index + 1] });
    }
    entries.push({ id: match[1], title: match[2].trim(), mermaid, nodes: [...labels].map(([id, label]) => ({ id, label })), edges });
  }
  return entries;
}

fs.mkdirSync(outputRoot, { recursive: true });

const data = days.map((day, dayIndex) => {
  const diagrams = diagramCatalog(dayIndex + 1);
  const notebooksDir = path.join(courseRoot, day.dir, 'notebooks');
  const destination = path.join(outputRoot, day.dir);
  fs.mkdirSync(destination, { recursive: true });
  const notebooks = fs.readdirSync(notebooksDir).filter((name) => name.endsWith('.ipynb')).sort();
  return {
    id: day.dir,
    number: dayIndex + 1,
    short: day.short,
    title: day.title,
    project: day.project,
    color: day.color,
    diagrams,
    notebooks: notebooks.map((file, notebookIndex) => {
      const sourcePath = path.join(notebooksDir, file);
      const notebook = JSON.parse(fs.readFileSync(sourcePath, 'utf8'));
      fs.copyFileSync(sourcePath, path.join(destination, file));
      const markdownCells = notebook.cells.filter((cell) => cell.cell_type === 'markdown');
      const readable = markdownCells.map((cell) => cell.source.join('')).join('\n\n---\n\n');
      const theory = markdownCells
        .filter((cell) => cell.metadata?.tags?.includes('embedded-course-theory'))
        .map((cell) => cell.source.join(''))
        .join('\n\n');
      const codeCells = notebook.cells.filter((cell) => cell.cell_type === 'code').length;
      const referencedDiagramIds = [...readable.matchAll(/\b(D\d{2})\b/g)].map((match) => match[1]);
      const lessonDiagrams = diagrams.filter((diagram) => referencedDiagramIds.includes(diagram.id));
      return {
        id: `${dayIndex + 1}-${notebookIndex + 1}`,
        order: notebookIndex + 1,
        file,
        path: `${day.dir}/notebooks/${file}`,
        publicPath: `/notebooks/${day.dir}/${file}`,
        title: plainTitle(readable, file.replace('.ipynb', '').replaceAll('_', ' ')),
        description: description(readable),
        theory: theory || readable,
        reading: readable,
        cells: notebook.cells
          .filter((cell) => cell.cell_type === 'markdown' || cell.cell_type === 'code')
          .map((cell, cellIndex) => ({
            id: cellIndex + 1,
            type: cell.cell_type,
            source: cell.source.join(''),
          })),
        diagrams: lessonDiagrams.length ? lessonDiagrams : diagrams.slice(0, 1),
        codeCells,
        isExercise: file.includes('_exercise_'),
        isProject: file.includes('_project_'),
        hasLiveObservation: markdownCells.some((cell) => cell.metadata?.tags?.includes('required-live-observation')),
      };
    }),
  };
});

const out = `export const courseDays = ${JSON.stringify(data, null, 2)} as const;\n`;
fs.writeFileSync(path.join(siteRoot, 'app', 'course-data.ts'), out);
console.log(`Prepared ${data.reduce((sum, day) => sum + day.notebooks.length, 0)} notebooks.`);
