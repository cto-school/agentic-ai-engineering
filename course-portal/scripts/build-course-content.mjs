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
  '03_embeddings_and_semantic_search.ipynb': ['D06'], '04_exercise_rag_context.ipynb': ['D07'],
  '05_citations_and_abstention.ipynb': ['D07'], '06_retrieval_evaluation.ipynb': ['D07'],
  '07_retrieval_tool_and_state.ipynb': ['D07'], '08_project_knowledge_assistant.ipynb': ['D06', 'D07'], '01_conversation_history.ipynb': ['D08'],
  '02_exercise_context_compaction.ipynb': ['D09'], '03_custom_persistent_memory.ipynb': ['D10'],
  '04_mem0_platform.ipynb': ['D10'], '05_small_plans.ipynb': ['D08'],
  '06_tools_with_side_effects.ipynb': ['D11'], '07_permissions_and_approval.ipynb': ['D11'],
  '08_observability_and_safety_evaluation.ipynb': ['D11'], '09_project_safe_task_agent.ipynb': ['D08', 'D10', 'D11'],
  '01_seeded_artifact_and_golden_set.ipynb': ['D12'], '02_single_reviewer_baseline.ipynb': ['D12'],
  '03_deterministic_checks.ipynb': ['D12'], '04_parallel_specialist_reviewers.ipynb': ['D13'],
  '05_exercise_supervisor_synthesis.ipynb': ['D14'], '06_comparative_evaluation.ipynb': ['D15'],
  '07_project_engineering_review_team.ipynb': ['D13', 'D14', 'D15'],
  '01_what_is_a_harness.ipynb': ['D16'], '02_model_configuration_and_runtime.ipynb': ['D16'],
  '03_exercise_tool_registry.ipynb': ['D16'], '04_permissions_and_limits.ipynb': ['D16'],
  '05_events_logs_and_checkpoints.ipynb': ['D16'], '06_mcp_client.ipynb': ['D17'],
  '07_project_mini_harness.ipynb': ['D16', 'D18'],
  '08_project_website_maintenance_agent.ipynb': ['D18', 'D19'],
  // LangChain track
  '01_plain_model_call.ipynb': ['D20'], '02_tool_calling_by_hand.ipynb': ['D21'],
  '03_first_agent.ipynb': ['D22'], '04_production_ready_tools.ipynb': ['D21'],
  '05_structured_output.ipynb': ['D23'], '06_conversation_memory.ipynb': ['D24'],
  '07_long_term_memory.ipynb': ['D24'], '08_knowledge_rag.ipynb': ['D25'],
  '09_research_and_planning.ipynb': ['D22'], '10_middleware_guardrails_permissions.ipynb': ['D26'],
  '11_human_in_the_loop.ipynb': ['D27'], '12_langgraph_workflow.ipynb': ['D28'],
  '13_multi_agent.ipynb': ['D29'], '14_streaming_observability_production.ipynb': ['D26', 'D30']
};

const days = [
  { dir: 'day_01_model_tools_agent', short: 'Foundations', title: 'Model, Tools & Agent', project: 'Smart Research Assistant', projectLesson: 7, color: '#ef8354',
    outcome: 'Build a tool-using agent whose every step you can point to.',
    prerequisite: 'No agentic-AI background is needed. Basic Python (functions, lists, dictionaries) is enough.',
    projectBrief: 'You send one message to a model, then add the pieces that turn replies into a dependable assistant: a validated output contract, a safe calculator tool, and a loop you control. The project is a research assistant that shows its evidence.',
    projectFlow: ['Make one model call and read the reply', 'Turn replies into validated data', 'Let the model request a tool you run', 'Write the bounded loop and ship the assistant'] },
  { dir: 'day_02_knowledge_and_state', short: 'Knowledge', title: 'Knowledge, RAG & State', project: 'Engineering Knowledge Assistant', projectLesson: 8, color: '#41b3a3',
    outcome: 'Build an assistant that answers from evidence or says it cannot.',
    prerequisite: 'Uses the chat() helper and tool loop from Day 1. Retrieval itself is introduced from scratch.',
    projectBrief: 'You give the assistant documents it has never seen: split them into chunks, find the right ones by keyword and by meaning, assemble evidence within a budget, answer with citations, and measure retrieval separately from answers.',
    projectFlow: ['Chunk documents with their source labels', 'Compare keyword and semantic retrieval', 'Assemble evidence and answer with citations', 'Measure retrieval and answers separately'] },
  { dir: 'day_03_memory_and_safety', short: 'Safety', title: 'Memory, Guardrails & Safety', project: 'Safe Personal Task Agent', projectLesson: 9, color: '#7a6ff0',
    outcome: 'Build an agent that can act, but only within rules you wrote.',
    prerequisite: 'Uses the tools and loop from Day 1. Memory, planning, and policy are built from scratch.',
    projectBrief: 'You manage a growing conversation, keep only the memories worth keeping, let the model propose plans and actions, and put deterministic policy and human approval between a proposal and any real side effect.',
    projectFlow: ['Bound the conversation with compaction', 'Keep selected memories with a lifecycle', 'Separate plans and proposals from execution', 'Enforce policy, approval, and a safety suite'] },
  { dir: 'day_04_multi_agent_systems', short: 'Coordination', title: 'Multi-Agent Systems', project: 'Engineering Design Review Team', projectLesson: 7, color: '#de9e36',
    outcome: 'Decide with numbers whether more agents are worth it.',
    prerequisite: 'Assumes you can build and evaluate one bounded agent. The day starts by measuring that simpler baseline.',
    projectBrief: 'You compare one reviewer with a team: deterministic checks, focused specialists running in parallel, and a supervisor that merges findings. Two scenarios show when the team is worth its cost and when it is not.',
    projectFlow: ['Define a review task you can score', 'Measure the single-reviewer baseline', 'Add checks and parallel specialists', 'Merge, compare, and decide with evidence'] },
  { dir: 'day_05_ai_harness', short: 'Runtime', title: 'Harness & Automation', project: 'Mini Harness + Website Maintenance Agent', projectLesson: 8, color: '#3085c3',
    outcome: 'Build a reusable runtime and run a real workflow on it.',
    prerequisite: 'Consolidates the model, tool, knowledge, memory, safety, and coordination boundaries from Days 1 to 4.',
    projectBrief: 'You package the controls every project repeated into one reusable runtime: configuration, a tool registry, policy and limits, events and checkpoints, and an MCP connection. Then that harness runs a website-maintenance agent end to end.',
    projectFlow: ['Separate configuration from the runtime', 'Register, govern, and limit tools', 'Record events, resume from checkpoints, connect MCP', 'Run the maintenance agent through the harness'] },
];

// Tracks sit beside the five days: one self-contained notebook each, split into sections the same way.
const tracks = [
  { dir: 'langchain_track', masterFile: 'langchain_complete.ipynb', diagramSource: 'langchain.md', code: 'L', label: 'LangChain', name: 'the LangChain track',
    short: 'LangChain', title: 'LangChain Track', project: 'OpsPilot', projectLesson: 14, color: '#1c9c8a',
    outcome: 'Grow one LangChain agent from a model call to a production-shaped system.',
    prerequisite: 'Separate from the five days. Knowing what a model call and a tool are (Day 1) helps; every LangChain and LangGraph idea is introduced from scratch.',
    projectBrief: 'You build OpsPilot, an operations assistant, fourteen times with LangChain 1.x and LangGraph. Each version solves a problem the previous one visibly had: tools, structured output, memory, retrieval, planning, middleware, human approval, explicit workflows, specialists, streaming and tracing.',
    projectFlow: ['Call a model, then let it request tools', 'Add structured output, memory and knowledge', 'Guard it with middleware and human approval', 'Shape workflows, specialists and observability'] },
];

function plainTitle(source, fallback) {
  const match = source.match(/^#\s+(.+)$/m);
  return match ? match[1].replace(/[*`]/g, '').trim() : fallback;
}

function diagramCatalog(sourceFile) {
  const file = path.join(courseRoot, 'diagrams', 'source', sourceFile);
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
fs.mkdirSync(path.join(siteRoot, 'public', 'diagrams'), { recursive: true });
fs.cpSync(path.join(courseRoot, 'diagrams', 'rendered'), path.join(siteRoot, 'public', 'diagrams'), { recursive: true });

// The notebooks embed diagrams as base64 images; the portal serves the same PNGs as files.
function relocateImages(markdown) {
  return markdown.replace(/<img src="data:image\/png;base64,[^"]+" width="(\d+)" alt="(D\d+): ([^"]*)">/g,
    (match, width, id, alt) => `<img src="/diagrams/${id}.png" width="${width}" alt="${id}: ${alt}">`);
}

let setupGuide = '';

const units = [
  ...days.map((day, index) => ({ ...day, kind: 'day', number: index + 1, code: String(index + 1), label: `Day ${index + 1}`, name: `Day ${index + 1}`,
    masterFile: `day_${String(index + 1).padStart(2, '0')}_complete.ipynb`, diagramSource: `day_${String(index + 1).padStart(2, '0')}.md` })),
  ...tracks.map((track) => ({ ...track, kind: 'track', number: 0 })),
];

const data = units.map((day, dayIndex) => {
  const diagrams = diagramCatalog(day.diagramSource);
  const notebooksDir = path.join(courseRoot, day.dir, 'notebooks');
  const destination = path.join(outputRoot, day.dir);
  fs.mkdirSync(destination, { recursive: true });
  const masterFile = day.masterFile;
  fs.copyFileSync(path.join(courseRoot, day.dir, masterFile), path.join(destination, masterFile));
  const notebooks = fs.readdirSync(notebooksDir).filter((name) => name.endsWith('.ipynb')).sort();
  return {
    id: day.dir,
    kind: day.kind,
    number: day.number,
    code: day.code,
    label: day.label,
    name: day.name,
    short: day.short,
    title: day.title,
    project: day.project,
    projectLesson: day.projectLesson,
    prerequisite: day.prerequisite,
    projectBrief: day.projectBrief,
    projectFlow: day.projectFlow,
    color: day.color,
    outcome: day.outcome,
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
        .map((cell, cellIndex) => ({ id: cellIndex + 1, type: cell.cell_type, source: cell.cell_type === 'markdown' ? relocateImages(cell.source.join('')) : cell.source.join(''), tags: cell.metadata?.tags || [] }));
      const markdownCells = cells.filter((cell) => cell.type === 'markdown');
      const readable = markdownCells.map((cell) => cell.source).join('\n\n');
      // The section's own explanations without the code: every markdown cell, minus the H1 the page already shows.
      const reading = markdownCells.map((cell) => cell.source).join('\n\n').replace(/^#\s+.+\r?\n/m, '').trim();
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
        id: `${day.kind === 'day' ? dayIndex + 1 : day.code}-${notebookIndex + 1}`,
        order: notebookIndex + 1,
        sectionCode: day.kind === 'day' ? `${day.number}.${notebookIndex + 1}` : `${day.code}${notebookIndex + 1}`,
        file,
        path: `${day.dir}/notebooks/${file}`,
        publicPath: `/notebooks/${day.dir}/${file}`,
        title: plainTitle(readable, file.replace('.ipynb', '').replaceAll('_', ' ')),
        description: guide.idea,
        guide: { ...guide, mistake },
        reading,
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
console.log(`Prepared ${data.reduce((sum, day) => sum + day.notebooks.length, 0)} notebooks across ${days.length} days and ${tracks.length} track(s).`);
