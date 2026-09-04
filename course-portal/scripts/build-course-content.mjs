import fs from 'node:fs';
import path from 'node:path';

const siteRoot = path.resolve(import.meta.dirname, '..');
const courseRoot = path.resolve(siteRoot, '..');
const outputRoot = path.join(siteRoot, 'public', 'notebooks');
const lessonGuides = JSON.parse(fs.readFileSync(path.join(siteRoot, 'content', 'lesson-guides.json'), 'utf8'));
const commonMistakes = JSON.parse(fs.readFileSync(path.join(siteRoot, 'content', 'common-mistakes.json'), 'utf8'));

const diagramMap = {
  '01_first_model_call.ipynb': ['D01'], '02_configuring_model_behavior.ipynb': ['D01'],
  '03_structured_outputs.ipynb': ['D02'], '04_tool_calling.ipynb': ['D03'],
  '05_exercise_manual_agent_loop.ipynb': ['D04'], '06_langgraph_agent.ipynb': ['D05'],
  '07_project_research_assistant.ipynb': ['D01', 'D03', 'D04'],
  '01_documents_and_chunks.ipynb': ['D06'], '02_keyword_search.ipynb': ['D06'],
  '03_embeddings_and_semantic_search.ipynb': ['D06'], '04_basic_rag.ipynb': ['D07'],
  '05_citations_and_abstention.ipynb': ['D07'], '06_retrieval_evaluation.ipynb': ['D07'],
  '07_retrieval_tool_and_state.ipynb': ['D07'], '08_project_knowledge_assistant.ipynb': ['D06', 'D07'],
  '09_exercise_rag_context.ipynb': ['D07'], '01_conversation_history.ipynb': ['D08'],
  '02_context_compaction.ipynb': ['D09'], '03_custom_persistent_memory.ipynb': ['D10'],
  '04_mem0_platform.ipynb': ['D10'], '05_small_plans.ipynb': ['D08'],
  '06_tools_with_side_effects.ipynb': ['D11'], '07_permissions_and_approval.ipynb': ['D11'],
  '08_observability_and_safety_evaluation.ipynb': ['D11'], '09_project_safe_task_agent.ipynb': ['D08', 'D10', 'D11'],
  '10_exercise_history_compaction.ipynb': ['D09'], '11_exercise_action_policy.ipynb': ['D11'],
  '01_seeded_artifact_and_golden_set.ipynb': ['D12'], '02_single_reviewer_baseline.ipynb': ['D12'],
  '03_deterministic_checks.ipynb': ['D12'], '04_parallel_specialist_reviewers.ipynb': ['D13'],
  '05_supervisor_synthesis.ipynb': ['D14'], '06_comparative_evaluation.ipynb': ['D15'],
  '07_project_engineering_review_team.ipynb': ['D13', 'D14', 'D15'], '08_exercise_supervisor_merge.ipynb': ['D14'],
  '01_what_is_a_harness.ipynb': ['D16'], '02_model_configuration_and_runtime.ipynb': ['D16'],
  '03_tool_registry.ipynb': ['D16'], '04_permissions_and_limits.ipynb': ['D16'],
  '05_events_logs_and_checkpoints.ipynb': ['D16'], '06_mcp_client.ipynb': ['D17'],
  '07_project_mini_harness.ipynb': ['D16', 'D18'], '08_exercise_tool_registry.ipynb': ['D16'],
  '09_project_website_maintenance_agent.ipynb': ['D18', 'D19']
};

const days = [
  { dir: 'day_01_model_tools_agent', short: 'Foundations', title: 'Model, Tools & Agent', project: 'Smart Research Assistant', projectLesson: 7, prerequisite: 'No previous agentic-AI knowledge is required. Basic Python functions, lists, and dictionaries are enough.', projectBrief: 'You will progressively build an assistant that accepts a focused question, asks a model what to do next, uses approved research tools, records the evidence, and stops with an inspectable answer.', projectFlow: ['Make one model call', 'Turn model output into validated data', 'Let the model request tools', 'Control the complete loop in Python'], color: '#ef8354' },
  { dir: 'day_02_knowledge_and_state', short: 'Knowledge', title: 'Knowledge, RAG & State', project: 'Engineering Knowledge Assistant', projectLesson: 8, prerequisite: 'Uses the model-call and tool-loop ideas from Day 1. Retrieval itself is introduced from first principles.', projectBrief: 'You will build an assistant that searches supplied engineering documents, assembles relevant evidence, answers with citations, and clearly abstains when the collection cannot support an answer.', projectFlow: ['Prepare labelled document chunks', 'Compare keyword and semantic retrieval', 'Assemble bounded RAG context', 'Answer with evidence or abstain'], color: '#41b3a3' },
  { dir: 'day_03_memory_and_safety', short: 'Safety', title: 'Memory, Guardrails & Safety', project: 'Safe Personal Task Agent', projectLesson: 9, prerequisite: 'Uses the visible state and tool execution boundaries developed on Days 1 and 2.', projectBrief: 'You will build a task agent that can retain selected preferences, form a small plan, propose real actions, wait for approval, and leave a trace showing exactly why an action ran or was blocked.', projectFlow: ['Manage conversation context', 'Store only useful long-term memory', 'Separate plans from execution', 'Apply guardrails, approval, and evaluation'], color: '#7a6ff0' },
  { dir: 'day_04_multi_agent_systems', short: 'Coordination', title: 'Multi-Agent Systems', project: 'Engineering Design Review Team', projectLesson: 7, prerequisite: 'Assumes you can build and evaluate one bounded agent. The day begins by measuring that simpler baseline.', projectBrief: 'You will compare one reviewer with a coordinated review team: deterministic checks and focused specialists produce findings that a supervisor merges into an evidence-backed engineering report.', projectFlow: ['Define a measurable review task', 'Establish a single-agent baseline', 'Add genuinely distinct specialists', 'Merge and evaluate quality, cost, and latency'], color: '#de9e36' },
  { dir: 'day_05_ai_harness', short: 'Runtime', title: 'Harness & Automation', project: 'Mini Harness + Website Maintenance Agent', projectLesson: 9, prerequisite: 'Consolidates the model, tool, knowledge, memory, safety, and coordination boundaries built during Days 1–4.', projectBrief: 'You will first package the repeated controls into a reusable mini harness, then use that harness in a website-maintenance workflow that checks updates, proposes a change, applies policy, pauses for approval, and records the run.', projectFlow: ['Separate configuration from runtime', 'Govern tools and resource limits', 'Add events, checkpoints, and MCP', 'Run an end-to-end automated maintenance cycle'], color: '#3085c3' },
];

function plainTitle(source, fallback) {
  const match = source.match(/^#\s+(.+)$/m);
  return match ? match[1].replace(/[*`]/g, '').trim() : fallback;
}

function diagramCatalog(dayNumber) {
  const file = path.join(courseRoot, 'diagrams', 'source', `day_${String(dayNumber).padStart(2, '0')}.md`);
  const source = fs.readFileSync(file, 'utf8');
  const entries = [];
  const pattern = /^##\s+(D\d+)\s+—\s+(.+?)\s*$[\s\S]*?```mermaid\s*\n([\s\S]*?)```/gm;
  for (const match of source.matchAll(pattern)) {
    const mermaid = match[3].trim();
    const tail = source.slice(match.index + match[0].length).split(/^##\s/m)[0];
    const textAlternative = tail.match(/Text alternative:\s*(.+)/)?.[1]?.trim() || '';
    const labels = new Map();
    for (const node of mermaid.matchAll(/([A-Za-z][A-Za-z0-9_]*)\s*(?:\[|\{|\()+"?([^\]})"]+)"?(?:\]|\}|\))+/g)) labels.set(node[1], node[2]);
    for (const participant of mermaid.matchAll(/^\s*participant\s+([A-Za-z][A-Za-z0-9_]*)\s+as\s+(.+)$/gm)) labels.set(participant[1], participant[2].trim());
    const edges = [];
    for (const line of mermaid.split('\n')) {
      const sequence = line.match(/^\s*([A-Za-z][A-Za-z0-9_]*)\s*-+>>\s*([A-Za-z][A-Za-z0-9_]*)\s*:\s*(.*)$/);
      if (sequence) { edges.push({ from: sequence[1], to: sequence[2], label: sequence[3].trim() }); continue; }
      if (!line.includes('-->')) continue;
      // Split a chain such as  A --> B -->|"yes"| C  into labelled hops.
      const hops = line.trim().split(/-->/);
      for (let index = 0; index < hops.length - 1; index += 1) {
        const from = hops[index].match(/([A-Za-z][A-Za-z0-9_]*)/)?.[1];
        const right = hops[index + 1];
        const label = right.match(/^\s*\|\s*"?([^"|]*)"?\s*\|/)?.[1]?.trim() || '';
        const to = right.replace(/^\s*\|[^|]*\|/, '').match(/([A-Za-z][A-Za-z0-9_]*)/)?.[1];
        if (from && to) edges.push({ from, to, label });
      }
    }
    if (!labels.size || !edges.length) throw new Error(`Diagram ${match[1]} has no renderable nodes or edges`);
    entries.push({ id: match[1], title: match[2].trim(), mermaid, textAlternative, nodes: [...labels].map(([id, label]) => ({ id, label })), edges });
  }
  return entries;
}

fs.mkdirSync(outputRoot, { recursive: true });

let setupGuide = '';

const data = days.map((day, dayIndex) => {
  const diagrams = diagramCatalog(dayIndex + 1);
  const notebooksDir = path.join(courseRoot, day.dir, 'notebooks');
  const destination = path.join(outputRoot, day.dir);
  fs.mkdirSync(destination, { recursive: true });
  const masterFile = `day_${String(dayIndex + 1).padStart(2, '0')}_complete.ipynb`;
  fs.copyFileSync(path.join(courseRoot, day.dir, masterFile), path.join(destination, masterFile));
  const notebooks = fs.readdirSync(notebooksDir).filter((name) => name.endsWith('.ipynb')).sort();
  return {
    id: day.dir,
    number: dayIndex + 1,
    short: day.short,
    title: day.title,
    project: day.project,
    projectLesson: day.projectLesson,
    prerequisite: day.prerequisite,
    projectBrief: day.projectBrief,
    projectFlow: day.projectFlow,
    color: day.color,
    masterFile,
    masterPath: `${day.dir}/${masterFile}`,
    masterPublicPath: `/notebooks/${day.dir}/${masterFile}`,
    diagrams,
    notebooks: notebooks.map((file, notebookIndex) => {
      const sourcePath = path.join(notebooksDir, file);
      const notebook = JSON.parse(fs.readFileSync(sourcePath, 'utf8'));
      fs.copyFileSync(sourcePath, path.join(destination, file));
      const cells = notebook.cells
        .filter((cell) => cell.cell_type === 'markdown' || cell.cell_type === 'code')
        .map((cell, cellIndex) => ({ id: cellIndex + 1, type: cell.cell_type, source: cell.source.join(''), tags: cell.metadata?.tags || [] }));
      const markdownCells = cells.filter((cell) => cell.type === 'markdown');
      const readable = markdownCells.map((cell) => cell.source).join('\n\n');
      const theory = markdownCells
        .filter((cell) => cell.tags.includes('embedded-course-theory'))
        .map((cell) => cell.source.replace(/^##\s+Concept briefing\s*/i, ''))
        .join('\n\n')
        .trim();
      const closingCell = [...markdownCells].reverse().find((cell) => /###\s+(Checkpoint|Recap)|^##\s+Explain/m.test(cell.source));
      const closing = closingCell ? closingCell.source.trim() : '';
      const beforeCell = markdownCells.find((cell) => /^##\s+Before you begin/m.test(cell.source));
      const before = beforeCell ? beforeCell.source.replace(/^##\s+Before you begin\s*/m, '').trim() : '';
      const setupCell = markdownCells.find((cell) => /^##\s+Your API key/m.test(cell.source));
      if (setupCell && !setupGuide) setupGuide = setupCell.source.trim();
      const codeCells = cells.filter((cell) => cell.type === 'code').length;
      const guide = lessonGuides[file];
      const mistake = commonMistakes[file];
      if (!guide || !mistake) throw new Error(`Missing beginner guide for ${day.dir}/${file}`);
      const referencedDiagramIds = diagramMap[file] || [];
      const lessonDiagrams = diagrams.filter((diagram) => referencedDiagramIds.includes(diagram.id));
      if (lessonDiagrams.length !== referencedDiagramIds.length) throw new Error(`Missing mapped diagram for ${day.dir}/${file}`);
      return {
        id: `${dayIndex + 1}-${notebookIndex + 1}`,
        order: notebookIndex + 1,
        file,
        path: `${day.dir}/notebooks/${file}`,
        publicPath: `/notebooks/${day.dir}/${file}`,
        title: plainTitle(readable, file.replace('.ipynb', '').replaceAll('_', ' ')),
        description: guide.idea,
        guide: { ...guide, mistake },
        before,
        theory,
        closing,
        cells: cells.map(({ id, type, source }) => ({ id, type, source })),
        diagrams: lessonDiagrams,
        codeCells,
        isExercise: file.includes('_exercise_'),
        isProject: file.includes('_project_'),
        hasLiveObservation: markdownCells.some((cell) => cell.tags.includes('required-live-observation')),
      };
    }),
  };
});

if (!setupGuide) throw new Error('Day 1 Lesson 1 no longer contains the "Your API key" section');

const out = `// Generated by scripts/build-course-content.mjs. Do not edit by hand; run \`pnpm content\`.\n`
  + `export const courseDays = ${JSON.stringify(data, null, 2)};\n\n`
  + `export const setupGuide = ${JSON.stringify(setupGuide)};\n`;
fs.writeFileSync(path.join(siteRoot, 'app', 'course-data.ts'), out);
console.log(`Prepared ${data.reduce((sum, day) => sum + day.notebooks.length, 0)} notebooks.`);
