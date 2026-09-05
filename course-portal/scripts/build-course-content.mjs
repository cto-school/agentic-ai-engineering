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
  '13_multi_agent.ipynb': ['D29'], '14_streaming_observability_production.ipynb': ['D26', 'D30'],
  // LangGraph track
  '01_graphs_before_agents.ipynb': ['D31', 'D32'], '02_model_as_a_node.ipynb': ['D33'],
  '03_tools_and_the_agent_loop.ipynb': ['D34'], '04_structured_output_and_routing.ipynb': ['D35'],
  '05_short_term_memory_and_context.ipynb': ['D36'], '06_long_term_memory.ipynb': ['D37'],
  '07_knowledge_and_retrieval.ipynb': ['D38'], '08_approval_permissions_and_injection.ipynb': ['D39'],
  '09_reliability_and_limits.ipynb': ['D40'], '10_parallel_work.ipynb': ['D41'],
  '11_mcp_tools_from_servers.ipynb': ['D42'], '12_multi_agent_supervisor.ipynb': ['D43'],
  '13_streaming_tracing_and_evaluation.ipynb': ['D34', 'D44'], '14_scheduled_runs.ipynb': ['D45'], '15_the_full_system.ipynb': ['D44'],
  // Standalone modules (Markdown chapters)
  '01_what_ollama_is.md': ['D50'], '02_install_ollama.md': ['D50'], '03_choose_a_model_for_a_laptop.md': ['D51'],
  '04_pull_and_run_gemma.md': ['D50'], '05_talk_to_ollama_from_programs.md': ['D52'], '06_customise_and_troubleshoot.md': ['D52'],
  '01_what_n8n_is.md': ['D53', 'D54'], '02_open_an_n8n_cloud_account.md': ['D53'], '03_how_an_agent_node_works.md': ['D54'],
  '04_agent_1_chat_assistant_with_memory.md': ['D54'], '05_agent_2_research_agent_with_tools.md': ['D54'],
  '06_agent_3_ticket_triage_with_structured_output.md': ['D55'], '07_agent_4_supervisor_and_running_agents_well.md': ['D56'],
  '01_what_openclaw_is.md': ['D57', 'D59'], '02_open_an_aws_account_safely.md': ['D58'], '03_launch_an_ec2_ubuntu_machine.md': ['D58'],
  '04_ssh_in_and_harden_the_machine.md': ['D58'], '05_install_openclaw.md': ['D57'], '06_connect_a_telegram_bot.md': ['D59'],
  '07_gemini_model_and_daily_operation.md': ['D57'],
  '01_from_text_to_tokens.md': ['D60'], '02_inside_the_transformer.md': ['D61'], '03_predicting_the_next_token.md': ['D64'],
  '04_pretraining.md': ['D62'], '05_post_training.md': ['D62'], '06_inference_under_the_hood.md': ['D63'],
  '07_limits_and_what_it_means_for_agents.md': ['D62', 'D63'],
  '01_why_agents_need_a_memory_layer.md': ['D65', 'D69'], '02_open_an_account_and_store_first_memories.md': ['D65'],
  '03_how_add_and_search_work.md': ['D66', 'D67'], '04_wire_memory_into_an_agent.md': ['D68'],
  '05_shape_what_is_remembered.md': ['D66'], '06_run_mem0_yourself.md': ['D69'],
  '07_privacy_evaluation_and_operations.md': ['D67', 'D68']
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
    projectFlow: ['Call a model, then let it request tools', 'Add structured output, memory and knowledge', 'Guard it with middleware and human approval', 'Shape workflows, specialists and observability'],
    spine: [['Model', 1], ['Tools + agent', 4], ['Output + memory', 7], ['Knowledge + planning', 9], ['Guardrails + approval', 11], ['Graphs + specialists', 13], ['Production', 14]] },
  { dir: 'langgraph_track', masterFile: 'langgraph_complete.ipynb', diagramSource: 'langgraph.md', code: 'G', label: 'LangGraph', name: 'the LangGraph track',
    short: 'LangGraph', title: 'LangGraph Track', project: 'CampusAI', projectLesson: 15, color: '#c2652d',
    outcome: 'Learn LangGraph from scratch by growing one graph into a production-grade agent.',
    prerequisite: 'Fully self-contained: basic Python is enough. It starts with graphs that contain no model at all and introduces every agent concept from first principles.',
    projectBrief: 'You build CampusAI, a university helpdesk assistant, fourteen times with LangGraph. It starts as a three-node graph with no AI in it and gains a model node, tools and the agent loop, structured routing, short- and long-term memory, retrieval, permissions and human approval, retries and limits, parallel checks, tools served over MCP, a supervisor with specialists, streaming with tracing and evaluation, scheduled unattended runs, and finally one assembled system.',
    projectFlow: ['Learn state, nodes, edges and loops without a model', 'Add the model, tools, structured routing and memory', 'Ground it in knowledge, then permission, approve and harden it', 'Parallelise, connect MCP tools, delegate, stream, evaluate, schedule and assemble'],
    spine: [['Graph basics', 1], ['Model + tools', 3], ['Routing + memory', 6], ['Knowledge + safety', 8], ['Reliability + parallel', 10], ['MCP + specialists', 12], ['Observability + schedules', 14], ['The full system', 15]] },
];

// Standalone modules: Markdown chapters under modules/<dir>/chapters, no notebook, no Colab link.
// Chapters may embed a portal simulation with an HTML comment: <!-- widget:tokenizer -->.
const modules = [
  { dir: 'modules/ollama', id: 'module_ollama', diagramSource: 'ollama.md', code: 'O', label: 'Ollama', name: 'the Ollama module',
    short: 'Ollama', title: 'Ollama', project: 'Gemma 3 on your laptop', projectLesson: 6, color: '#7f93e6',
    outcome: 'Run a small open model locally on an ordinary laptop, from the terminal and from programs.',
    prerequisite: 'Independent of the days and tracks. You need a laptop with 8 GB of RAM or more and a terminal; no GPU and no Python.',
    projectBrief: 'You install Ollama, choose the Gemma 3 size that fits your machine, pull it, talk to it in the terminal, reach it from programs through the same request shape the course uses for hosted models, and customise it with a Modelfile.',
    projectFlow: ['Understand weights, quantisation and the server', 'Install Ollama and pick a size', 'Pull Gemma 3 and use the terminal chat', 'Use it from programs and customise it'],
    spine: [['Concepts', 1], ['Install', 2], ['Choose', 3], ['Run', 4], ['Programs', 5], ['Customise', 6]] },
  { dir: 'modules/n8n', id: 'module_n8n', diagramSource: 'n8n.md', code: 'N', label: 'n8n', name: 'the n8n module',
    short: 'n8n', title: 'n8n', project: 'Four agents on a visual canvas', projectLesson: 7, color: '#ee7a9c',
    outcome: 'Build agents by drawing them: model, memory, tools, structured output and a supervisor as boxes.',
    prerequisite: 'Independent of the days and tracks; everything runs in the browser on n8n Cloud. Day 1 makes the concepts familiar but is not required.',
    projectBrief: 'You open an n8n Cloud account, store a Gemini key once, learn how the AI Agent node runs the tool loop, and build four agents: a chat assistant with memory, a research agent with tools, a ticket triage with structured output and routing, and a supervisor that delegates to specialist workflows.',
    projectFlow: ['Open the account and learn the editor', 'Understand the AI Agent node', 'Build chat, tools and structured output', 'Build a supervisor and operate it'],
    spine: [['Concepts', 1], ['Account', 2], ['Agent node', 3], ['Chat + memory', 4], ['Tools', 5], ['Structured output', 6], ['Supervisor + ops', 7]] },
  { dir: 'modules/openclaw', id: 'module_openclaw', diagramSource: 'openclaw.md', code: 'C', label: 'OpenClaw', name: 'the OpenClaw module',
    short: 'OpenClaw', title: 'OpenClaw on AWS', project: 'Your own assistant on a hardened server', projectLesson: 7, color: '#e8a13f',
    outcome: 'Deploy an always-on personal assistant on an EC2 machine you built and hardened, reachable through Telegram.',
    prerequisite: 'Independent of the days and tracks. You need a card and phone for AWS, a Google account for a Gemini key, a Telegram account and a terminal with ssh.',
    projectBrief: 'You open an AWS account without living as the root user, launch an Ubuntu EC2 machine, log in over SSH and remove root and password access, then install OpenClaw, keep its gateway running as a service, connect a Telegram bot with pairing, wire up a Gemini API key, and lock down what the assistant may do.',
    projectFlow: ['Open AWS safely and launch the machine', 'Log in and harden SSH', 'Install OpenClaw and its service', 'Connect Telegram, set the model, operate it'],
    spine: [['Concepts', 1], ['AWS account', 2], ['EC2', 3], ['SSH hardening', 4], ['Install', 5], ['Telegram', 6], ['Gemini + ops', 7]] },
  { dir: 'modules/llm_foundation', id: 'module_llm_foundation', diagramSource: 'llm_foundation.md', code: 'F', label: 'LLM Foundation', name: 'the LLM Foundation module',
    short: 'Foundation', title: 'LLM Foundation', project: 'A working mental model of an LLM', projectLesson: 7, color: '#a98bf0',
    outcome: 'Explain how a language model is built, trained and run, and what that means for the agents you build.',
    prerequisite: 'Independent of the days and tracks and needs no code. Read it when a term such as token, context window, temperature or tool call feels like a black box.',
    projectBrief: 'You follow text into tokens and vectors, through the Transformer, out as a probability over the next token, and back around; then pretraining, post-training and inference, and finally the limits every agent builder works around. Two chapters carry an in-browser simulation: a tokenizer you train yourself and a next-token predictor with a temperature slider.',
    projectFlow: ['Tokens, vectors and the Transformer', 'Choosing the next token', 'Pretraining and post-training', 'Inference, limits and what it means for agents'],
    spine: [['Tokens', 1], ['Transformer', 2], ['Sampling', 3], ['Pretraining', 4], ['Post-training', 5], ['Inference', 6], ['Limits', 7]] },
  { dir: 'modules/mem0', id: 'module_mem0', diagramSource: 'mem0.md', code: 'M', label: 'Mem0', name: 'the Mem0 module',
    short: 'Mem0', title: 'Mem0', project: 'A memory layer for your agents', projectLesson: 7, color: '#5fc9b8',
    outcome: 'Give any agent durable, per-user memory with Mem0, and evaluate and operate it responsibly.',
    prerequisite: 'Independent of the days and tracks. Day 3 makes the ideas familiar but is not required; you need Python or curl, a free Mem0 account, and for the local chapter Ollama or Docker.',
    projectBrief: 'You learn what a memory layer does and what it leaves to you, store and search your first memories on the Mem0 Platform, open the box on add and search, wire memory into an agent loop in plain Python, LangGraph and n8n, shape what is remembered, run Mem0 on your laptop with Ollama or as a self-hosted server, and finish with a recall-and-isolation evaluation and an operations checklist.',
    projectFlow: ['Understand the memory layer and store first memories', 'See how add and search work inside', 'Wire memory into an agent and shape what is kept', 'Run it yourself, then evaluate and operate it'],
    spine: [['Concepts', 1], ['Account', 2], ['Add + search', 3], ['Agent', 4], ['Shaping', 5], ['Self-host', 6], ['Operate', 7]] },
];

// The page header shows only the first sentence of the idea; the Learn tab shows the whole paragraph.
function firstSentence(text) {
  const match = text.match(/^(.+?[.!?])(?:\s|$)/);
  return match ? match[1] : text;
}

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
  ...modules.map((module) => ({ ...module, kind: 'module', number: 0 })),
];

// A module chapter is one Markdown file. Widget markers become segments the portal renders as simulations.
function moduleUnit(module) {
  const diagrams = diagramCatalog(module.diagramSource);
  const chaptersDir = path.join(courseRoot, module.dir, 'chapters');
  const files = fs.readdirSync(chaptersDir).filter((name) => name.endsWith('.md')).sort();
  const widgetMarker = /<!--\s*widget:([a-z0-9-]+)\s*-->/g;
  return {
    id: module.id, kind: 'module', number: 0, code: module.code, label: module.label, name: module.name, spine: module.spine || null,
    short: module.short, title: module.title, project: module.project, projectLesson: module.projectLesson,
    prerequisite: module.prerequisite, projectBrief: module.projectBrief, projectFlow: module.projectFlow, color: module.color, outcome: module.outcome,
    masterFile: '', masterPath: '', masterPublicPath: '',
    diagrams,
    notebooks: files.map((file, index) => {
      const source = fs.readFileSync(path.join(chaptersDir, file), 'utf8').replace(/\r\n/g, '\n');
      const body = source.replace(/^#\s+.+\n/m, '').trim();
      const segments = [];
      let last = 0;
      for (const match of body.matchAll(widgetMarker)) {
        const before = body.slice(last, match.index).trim();
        if (before) segments.push({ type: 'markdown', source: before });
        segments.push({ type: 'widget', source: match[1] });
        last = match.index + match[0].length;
      }
      const tail = body.slice(last).trim();
      if (tail) segments.push({ type: 'markdown', source: tail });
      const reading = segments.filter((segment) => segment.type === 'markdown').map((segment) => segment.source).join('\n\n');
      const guide = lessonGuides[file];
      const mistake = commonMistakes[file];
      if (!guide || !mistake) throw new Error(`Missing beginner guide for ${module.dir}/${file}`);
      const referencedDiagramIds = diagramMap[file] || [];
      const lessonDiagrams = diagrams.filter((diagram) => referencedDiagramIds.includes(diagram.id));
      if (lessonDiagrams.length !== referencedDiagramIds.length) throw new Error(`Missing mapped diagram for ${module.dir}/${file}`);
      return {
        id: `${module.code}-${index + 1}`,
        order: index + 1,
        sectionCode: `${module.code}${index + 1}`,
        file,
        path: `${module.dir}/chapters/${file}`,
        publicPath: '',
        title: plainTitle(source, file.replace('.md', '').replaceAll('_', ' ')),
        description: firstSentence(guide.idea),
        guide: { ...guide, mechanism: guide.mechanism || null, mistake },
        reading,
        closing: '',
        problem: '',
        segments,
        cells: [],
        diagrams: lessonDiagrams,
        codeCells: 0,
        commandBlocks: (body.match(/^```[a-z0-9]+\s*$/gm) || []).length,
        isExercise: false,
        isProject: false,
        hasLiveObservation: false,
      };
    }),
  };
}

const data = units.map((day, dayIndex) => {
  if (day.kind === 'module') return moduleUnit(day);
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
    spine: day.spine || null,
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
      // The section's closing cell (Recap, or Checkpoint + Recap on the days) and the problem line that opens its recap.
      const closingCell = [...markdownCells].reverse().find((cell) => /^###\s+(Checkpoint|Recap)/m.test(cell.source));
      const closing = closingCell ? closingCell.source.trim() : '';
      const problem = closing.match(/\*\*(?:Problem seen|Limitation seen|The problem we started with):\*\*\s*(.+)/)?.[1]?.trim() || '';
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
        description: firstSentence(guide.idea),
        guide: { ...guide, mechanism: guide.mechanism || null, mistake },
        reading,
        closing,
        problem,
        segments: [{ type: 'markdown', source: reading }],
        cells: cells.map(({ id, type, source }) => ({ id, type, source })),
        diagrams: lessonDiagrams,
        codeCells,
        commandBlocks: 0,
        isExercise: file.includes('_exercise_'),
        isProject: file.includes('_project_'),
        hasLiveObservation: markdownCells.some((cell) => cell.tags.includes('required-live-observation')),
      };
    }),
  };
});

if (!setupGuide) throw new Error('Day 1 Lesson 1 no longer contains the "Your API key" section');

// Display order for the portal: one standalone group (LangGraph first, LangChain last, the Markdown
// modules between), then the five-day path. Lesson ids do not depend on this order.
const standaloneOrder = ['langgraph_track', 'module_ollama', 'module_n8n', 'module_openclaw', 'module_llm_foundation', 'module_mem0', 'langchain_track'];
const orderedData = [
  ...standaloneOrder.map((id) => {
    const unit = data.find((candidate) => candidate.id === id);
    if (!unit) throw new Error(`Unknown unit in standaloneOrder: ${id}`);
    return { ...unit, section: 'standalone' };
  }),
  ...data.filter((unit) => unit.kind === 'day').map((unit) => ({ ...unit, section: 'five-day' })),
];
if (orderedData.length !== data.length) throw new Error('standaloneOrder does not list every non-day unit');

const out = `// Generated by scripts/build-course-content.mjs. Do not edit by hand; run \`pnpm content\`.\n`
  + `export const courseDays = ${JSON.stringify(orderedData, null, 2)};\n\n`
  + `export const setupGuide = ${JSON.stringify(setupGuide)};\n`;
fs.writeFileSync(path.join(siteRoot, 'app', 'course-data.ts'), out);
const moduleChapters = data.filter((unit) => unit.kind === 'module').reduce((sum, unit) => sum + unit.notebooks.length, 0);
console.log(`Prepared ${data.reduce((sum, day) => sum + day.notebooks.length, 0) - moduleChapters} notebooks across ${days.length} days and ${tracks.length} track(s), plus ${moduleChapters} chapters across ${modules.length} module(s).`);
