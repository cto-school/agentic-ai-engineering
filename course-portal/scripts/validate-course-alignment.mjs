import fs from 'node:fs';
import path from 'node:path';

const portalRoot = path.resolve(import.meta.dirname, '..');
const courseRoot = path.resolve(portalRoot, '..');
const dayDirs = [
  'day_01_model_tools_agent',
  'day_02_knowledge_and_state',
  'day_03_memory_and_safety',
  'day_04_multi_agent_systems',
  'day_05_ai_harness',
];
const expectedProjects = [
  'Smart Research Assistant',
  'Engineering Knowledge Assistant',
  'Safe Personal Task Agent',
  'Engineering Design Review Team',
  'Website Maintenance Agent',
];
const syllabus = fs.readFileSync(path.join(courseRoot, 'syllabus', 'course_syllabus.md'), 'utf8');
const errors = [];
let notebookCount = 0;

expectedProjects.forEach((project) => {
  if (!syllabus.includes(project)) errors.push(`Syllabus is missing project: ${project}`);
});

dayDirs.forEach((dayDir, index) => {
  const dayRoot = path.join(courseRoot, dayDir);
  const readme = fs.readFileSync(path.join(dayRoot, 'README.md'), 'utf8');
  const actual = fs.readdirSync(path.join(dayRoot, 'notebooks')).filter((file) => file.endsWith('.ipynb')).sort();
  const masterFile = `day_${String(index + 1).padStart(2, '0')}_complete.ipynb`;
  const masterPath = path.join(dayRoot, masterFile);
  if (!fs.existsSync(masterPath)) errors.push(`${dayDir}: missing ${masterFile}`);
  const documented = [...readme.matchAll(/`([^`]+\.ipynb)`/g)].map((match) => path.basename(match[1])).filter((file) => file !== masterFile).sort();
  if (JSON.stringify(actual) !== JSON.stringify(documented)) errors.push(`${dayDir}: README notebook sequence differs from the folder`);
  const diagramSource = fs.readFileSync(path.join(courseRoot, 'diagrams', 'source', `day_${String(index + 1).padStart(2, '0')}.md`), 'utf8');
  const knownDiagrams = new Set([...diagramSource.matchAll(/^##\s+(D\d+)/gm)].map((match) => match[1]));
  actual.forEach((file) => {
    notebookCount += 1;
    const notebook = JSON.parse(fs.readFileSync(path.join(dayRoot, 'notebooks', file), 'utf8'));
    const markdown = notebook.cells.filter((cell) => cell.cell_type === 'markdown').map((cell) => cell.source.join('')).join('\n');
    const references = [...markdown.matchAll(/\b(D\d{2})\b/g)].map((match) => match[1]);
    references.forEach((id) => { if (!knownDiagrams.has(id)) errors.push(`${dayDir}/${file}: missing diagram ${id}`); });
    if (!markdown.trim()) errors.push(`${dayDir}/${file}: no student-facing explanation`);
    if (!fs.existsSync(path.join(portalRoot, 'public', 'notebooks', dayDir, file))) errors.push(`${dayDir}/${file}: missing portal notebook copy`);
  });
  if (fs.existsSync(masterPath)) {
    const master = JSON.parse(fs.readFileSync(masterPath, 'utf8'));
    const generatedFrom = master.metadata?.course?.generated_from || [];
    if (JSON.stringify(generatedFrom) !== JSON.stringify(actual)) errors.push(`${dayDir}: master notebook source list differs from modular notebooks`);
    const sectionStarts = master.cells.filter((cell) => cell.metadata?.tags?.includes('master-section-start')).length;
    if (sectionStarts !== actual.length) errors.push(`${dayDir}: master notebook has ${sectionStarts} sections for ${actual.length} lessons`);
    if (!fs.existsSync(path.join(portalRoot, 'public', 'notebooks', dayDir, masterFile))) errors.push(`${dayDir}: missing portal master notebook copy`);
  }
});

if (notebookCount !== 45) errors.push(`Expected 45 notebooks, found ${notebookCount}`);
if (errors.length) {
  console.error(errors.map((error) => `- ${error}`).join('\n'));
  process.exit(1);
}
console.log(`Alignment verified: 5 master notebooks, ${notebookCount} modular lessons, projects and diagram references.`);
