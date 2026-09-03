from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, KeepTogether, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).parents[1]
OUT = ROOT / "output" / "pdf" / "agentic_ai_engineering_course_brochure.pdf"
OUT.parent.mkdir(parents=True, exist_ok=True)

FONT_DIR = Path("C:/Windows/Fonts")
pdfmetrics.registerFont(TTFont("CourseSans", str(FONT_DIR / "segoeui.ttf")))
pdfmetrics.registerFont(TTFont("CourseSans-Bold", str(FONT_DIR / "segoeuib.ttf")))

NAVY = colors.HexColor("#11243B")
NAVY_2 = colors.HexColor("#183B56")
TEAL = colors.HexColor("#00A6A6")
MINT = colors.HexColor("#DDF7F4")
GOLD = colors.HexColor("#F4B942")
INK = colors.HexColor("#16212E")
MUTED = colors.HexColor("#536273")
PALE = colors.HexColor("#F3F7FA")
WHITE = colors.white

PAGE_W, PAGE_H = A4
MARGIN_X = 17 * mm
MARGIN_TOP = 22 * mm
MARGIN_BOTTOM = 16 * mm

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="BodyX", fontName="CourseSans", fontSize=9.3, leading=13.2, textColor=INK, spaceAfter=5))
styles.add(ParagraphStyle(name="SmallX", fontName="CourseSans", fontSize=7.8, leading=10.6, textColor=MUTED))
styles.add(ParagraphStyle(name="H1X", fontName="CourseSans-Bold", fontSize=22, leading=26, textColor=NAVY, spaceAfter=9))
styles.add(ParagraphStyle(name="H2X", fontName="CourseSans-Bold", fontSize=14, leading=17, textColor=NAVY_2, spaceBefore=5, spaceAfter=7))
styles.add(ParagraphStyle(name="H3X", fontName="CourseSans-Bold", fontSize=10.5, leading=13, textColor=TEAL, spaceAfter=3))
styles.add(ParagraphStyle(name="CardTitle", fontName="CourseSans-Bold", fontSize=12, leading=15, textColor=NAVY, spaceAfter=4))
styles.add(ParagraphStyle(name="CardBody", fontName="CourseSans", fontSize=8.4, leading=11.5, textColor=INK))
styles.add(ParagraphStyle(name="WhiteBody", fontName="CourseSans", fontSize=10.5, leading=15, textColor=WHITE))
styles.add(ParagraphStyle(name="WhiteSmall", fontName="CourseSans", fontSize=8.5, leading=12, textColor=WHITE))
styles.add(ParagraphStyle(name="CoverTitle", fontName="CourseSans-Bold", fontSize=34, leading=38, textColor=WHITE))
styles.add(ParagraphStyle(name="CoverSub", fontName="CourseSans", fontSize=15, leading=21, textColor=MINT))
styles.add(ParagraphStyle(name="Credit", fontName="CourseSans-Bold", fontSize=16, leading=20, textColor=NAVY, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CenterSmall", fontName="CourseSans", fontSize=8.3, leading=11, textColor=MUTED, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="CenterWhite", fontName="CourseSans-Bold", fontSize=7.2, leading=9.2, textColor=WHITE, alignment=TA_CENTER))
styles.add(ParagraphStyle(name="DayLabel", fontName="CourseSans-Bold", fontSize=9.5, leading=12, textColor=WHITE, alignment=TA_CENTER))


def para(text, style="BodyX"):
    return Paragraph(text, styles[style])


def page_header(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, PAGE_H - 13 * mm, PAGE_W, 13 * mm, fill=1, stroke=0)
    canvas.setFont("CourseSans-Bold", 8.5)
    canvas.setFillColor(WHITE)
    canvas.drawString(MARGIN_X, PAGE_H - 8.5 * mm, "AGENTIC AI ENGINEERING")
    canvas.setFont("CourseSans", 7.5)
    canvas.drawRightString(PAGE_W - MARGIN_X, PAGE_H - 8.5 * mm, "FROM MODEL CALLS TO AI HARNESSES")
    canvas.setFillColor(TEAL)
    canvas.rect(0, PAGE_H - 14.5 * mm, PAGE_W, 1.5 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(colors.HexColor("#D9E2EA"))
    canvas.line(MARGIN_X, 12 * mm, PAGE_W - MARGIN_X, 12 * mm)
    canvas.setFillColor(MUTED)
    canvas.setFont("CourseSans", 7.5)
    canvas.drawString(MARGIN_X, 7.5 * mm, "Project-based course for final-year engineering students")
    canvas.drawRightString(PAGE_W - MARGIN_X, 7.5 * mm, f"{doc.page}")
    canvas.restoreState()


def cover(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    canvas.setFillColor(NAVY_2)
    canvas.circle(PAGE_W - 20 * mm, PAGE_H - 25 * mm, 55 * mm, fill=1, stroke=0)
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(3)
    canvas.line(18 * mm, PAGE_H - 122 * mm, 82 * mm, PAGE_H - 122 * mm)
    canvas.restoreState()


doc = BaseDocTemplate(
    str(OUT), pagesize=A4, leftMargin=MARGIN_X, rightMargin=MARGIN_X,
    topMargin=MARGIN_TOP, bottomMargin=MARGIN_BOTTOM,
    title="Agentic AI Engineering - Course Brochure",
    author="Agentic AI Engineering Course",
    subject="Five-day project-based syllabus and course overview",
)
cover_frame = Frame(18 * mm, 20 * mm, PAGE_W - 36 * mm, PAGE_H - 40 * mm, id="cover", showBoundary=0)
body_frame = Frame(MARGIN_X, MARGIN_BOTTOM, PAGE_W - 2 * MARGIN_X, PAGE_H - MARGIN_TOP - MARGIN_BOTTOM, id="body")
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[cover_frame], onPage=cover),
    PageTemplate(id="Body", frames=[body_frame], onPage=page_header),
])


def card(title, body, accent=TEAL):
    table = Table([[para(title, "CardTitle")], [para(body, "CardBody")]], colWidths=[82 * mm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), WHITE),
        ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#C9D6E0")),
        ("LINEBEFORE", (0, 0), (0, -1), 4, accent),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    return table


def day_block(day, title, project, flow, topics, outcome, accent):
    head = Table([[para(f"DAY {day}", "DayLabel"), para(title, "CardTitle")]], colWidths=[20 * mm, 142 * mm])
    head.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), accent),
        ("TEXTCOLOR", (0, 0), (0, 0), WHITE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LINEBELOW", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD7E1")),
    ]))
    details = Table([
        [para("PROJECT", "H3X"), para(project, "BodyX")],
        [para("BUILD PATH", "H3X"), para(flow, "BodyX")],
        [para("CORE TOPICS", "H3X"), para(topics, "BodyX")],
        [para("TAKEAWAY", "H3X"), para(outcome, "BodyX")],
    ], colWidths=[27 * mm, 135 * mm])
    details.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D6E0E8")),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return KeepTogether([head, details, Spacer(1, 7 * mm)])


story = []

# Cover
story += [Spacer(1, 37 * mm), para("AGENTIC AI<br/>ENGINEERING", "CoverTitle"), Spacer(1, 7 * mm),
          para("From first model calls to safe agents,<br/>multi-agent systems and reusable AI harnesses", "CoverSub"),
          Spacer(1, 21 * mm)]
badge = Table([[para("5 DAYS", "Credit"), para("5 PROJECTS", "Credit"), para("BEGINNER TO ADVANCED", "Credit")]], colWidths=[48 * mm] * 3)
badge.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), MINT), ("BOX", (0, 0), (-1, -1), 0, MINT),
                           ("INNERGRID", (0, 0), (-1, -1), 1, NAVY), ("TOPPADDING", (0, 0), (-1, -1), 9),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
story += [badge, Spacer(1, 17 * mm)]
credit = Table([[para("INCLUDED WITH THE COURSE", "CenterSmall")], [para("₹100 worth of AI API credits", "Credit")],
                [para("Individually limited classroom access for guided model exercises", "CenterSmall")]], colWidths=[146 * mm])
credit.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GOLD), ("BOX", (0, 0), (-1, -1), 1, WHITE),
                            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
story += [credit, Spacer(1, 19 * mm), para("Designed for final-year engineering students with Python fundamentals and no prior agentic AI experience.", "WhiteBody"),
          Spacer(1, 4 * mm), para("Project-based • Notebook-first • OpenRouter + open-source tooling • Mock fallbacks • No CrewAI or AutoGen", "WhiteSmall"),
          NextPageTemplate("Body"), PageBreak()]

# Overview
story += [para("Build the system, not just a demo", "H1X"),
          para("This course introduces agentic AI one layer at a time. Students first use a model, then inspect structured output, tools and state. Knowledge, memory, safety and observability are added only when the project exposes a real limitation. The course ends by consolidating these ideas into a reusable AI harness.", "BodyX"),
          Spacer(1, 3 * mm)]
journey = Table([[para(x, "CenterWhite") for x in ["MODEL", "TOOL", "AGENT", "KNOWLEDGE", "MEMORY", "SAFETY", "OBSERVABILITY", "MULTI-AGENT", "HARNESS"]]], colWidths=[18 * mm] * 9)
journey.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), NAVY), ("TEXTCOLOR", (0, 0), (-1, -1), WHITE),
                             ("INNERGRID", (0, 0), (-1, -1), 0.6, TEAL), ("BOX", (0, 0), (-1, -1), 0.8, NAVY),
                             ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8)]))
story += [journey, Spacer(1, 8 * mm), para("What makes the course different", "H2X")]
cards = Table([[card("Mechanism before framework", "Students build and inspect the loop before using LangGraph. The subject is agentic system design, not memorising a framework."),
                card("Project-based progression", "Five independent projects follow Build - Observe - Break - Improve. Six pivotal stub-and-test labs make students implement the central mechanisms.", GOLD)],
               [card("Safe and measurable", "Bounded steps, schema validation, permissions, approval, citations and golden-set evaluation are part of the core build."),
                card("Accessible classroom route", "OpenRouter provides consistent model access. Mock paths keep every core lesson runnable during outages or debugging.", GOLD)]],
              colWidths=[84 * mm, 84 * mm], hAlign="CENTER")
cards.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 3),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
story += [cards, Spacer(1, 7 * mm), para("By the end, students can", "H2X"),
          para("• Build a bounded tool-using agent and explain who executes each action.<br/>"
               "• Create a citation-producing RAG system and diagnose retrieval separately from generation.<br/>"
               "• Add context management, persistent memory, policy and human approval.<br/>"
               "• Compare single-agent and specialist multi-agent review systems using measurements.<br/>"
               "• Build a mini harness that operates a guarded Website Maintenance Agent with persistent state and approval.", "BodyX"), PageBreak()]

# Days 1-2
story += [para("Syllabus: Foundations and knowledge", "H1X"),
          day_block("1", "From model call to bounded agent", "Smart Research Assistant",
                    "Model call → configuration → structured output → tool request → manual loop → LangGraph",
                    "OpenRouter and mock routes; one direct OpenAI example; prompts and messages; Pydantic schemas; function calling; safe calculator; local search tool; tool-result messages; maximum-step termination.",
                    "Students build an application in which the model may request tools, while Python validates and executes every action.", TEAL),
          day_block("2", "Knowledge, retrieval and visible state", "Engineering Knowledge Assistant",
                    "Documents → chunks → keyword baseline → embeddings → retrieval → RAG → citations → evaluation",
                    "Heading-aware chunking; lexical and semantic search; Sentence Transformers; Chroma; grounded generation; citation validation; abstention; retrieval and answer golden sets; retrieval as a tool; state inspection.",
                    "Students build a small knowledge agent that answers from supplied engineering documents, cites evidence and abstains when evidence is insufficient.", GOLD),
          para("Daily learning pattern", "H2X"),
          para("Each project begins with the smallest working version. Students inspect the actual messages, chunks, state or events; reproduce a supplied failure; add one layer; and complete a bounded code modification with an objective success condition.", "BodyX"), PageBreak()]

# Days 3-4
story += [para("Syllabus: Memory, safety and collaboration", "H1X"),
          day_block("3", "Memory, planning and safe action", "Safe Personal Task Agent",
                    "History → compaction → persistent memory → plan → side effects → policy → approval → events",
                    "Conversation context and budgets; SQLite memory lifecycle; bounded plans; input, context, output, tool and execution guardrails; allow/approval/deny policy; injection defence; human-in-the-loop; safety cases and traces.",
                    "Students build an agent where a mock or live model proposes an action, but application policy and explicit human approval control execution.", TEAL),
          day_block("4", "Measured multi-agent systems", "Engineering Design Review Team",
                    "Seeded artifact → single reviewer → deterministic checks → specialists → supervisor → A/B",
                    "Structured engineering findings; correctness, security and maintainability roles; deterministic AST checks; sequential and parallel fan-out/fan-in; supervisor validation and deduplication; recall, false positives, model calls, tokens, latency and cost.",
                    "Students compare one general reviewer with bounded specialist reviewers and justify whether the added agents are worth the additional complexity.", GOLD),
          para("A deliberate design choice", "H2X"),
          para("The single-agent system is allowed to win. Multi-agent architecture is introduced as a measurable decomposition technique - not as a default, a swarm, or a substitute for deterministic engineering tools.", "BodyX"), PageBreak()]

# Day 5 and projects
story += [para("Syllabus: The AI harness capstone", "H1X"),
          day_block("5", "Reusable harness and operational automation", "Mini AI Harness + Website Maintenance Agent",
                    "Runtime → registry → guardrails → MCP → scheduled check → approval → verified website update",
                    "Mock/OpenRouter providers; registry and policy; events and checkpoints; MCP; cached or public update source; durable processed-item state; indirect-injection challenge; bounded live observation; persistent local website change; optional LLM judge.",
                    "Students use their harness for a recurring real-file workflow while keeping model proposals, guardrails, approval, verification and scheduling as separate responsibilities.", TEAL),
          para("Five independent portfolio projects", "H2X")]
projects = [
    ("01", "Smart Research Assistant", "A bounded model-and-tool loop"),
    ("02", "Engineering Knowledge Assistant", "RAG with citations and abstention"),
    ("03", "Safe Personal Task Agent", "Memory, policy and human approval"),
    ("04", "Engineering Design Review Team", "Measured single vs multi-agent review"),
    ("05", "Mini AI Harness + Website Agent", "Guarded recurring workflow with persistent effect"),
]
proj_table = Table([[para(n, "H3X"), para(name, "CardTitle"), para(result, "CardBody")] for n, name, result in projects], colWidths=[15 * mm, 72 * mm, 75 * mm])
proj_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), PALE), ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D4DEE7")),
                                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 7),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 7), ("TOPPADDING", (0, 0), (-1, -1), 7),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 7)]))
story += [proj_table, Spacer(1, 8 * mm), para("No framework zoo", "H2X"),
          para("CrewAI and AutoGen are deliberately excluded. LangGraph is used after the manual loop is understood. LangSmith, Mem0 and MCP are shown as product or protocol exposures around transparent local mechanisms, not as definitions of the concepts themselves.", "BodyX"), PageBreak()]

# Practical information
story += [para("Practical information", "H1X")]
info = Table([
    [card("Who should attend", "Final-year engineering students, recent graduates and early-career developers who can read and modify basic Python but are new to agentic AI."),
     card("Prerequisites", "Basic Python functions, lists, dictionaries and classes; package installation; notebooks; the basic idea of an HTTP API. Git is helpful but not required.", GOLD)],
    [card("Delivery format", "Five classroom days with theory embedded beside notebook code, deliberate failures, six pivotal exercise notebooks and one independently runnable project per day."),
     card("Student environment", "Students work on their own computers. OpenRouter is the primary live route; Ollama is optional; deterministic fallbacks support low-spec systems and service outages.", GOLD)],
], colWidths=[84 * mm, 84 * mm])
info.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 2),
                          ("RIGHTPADDING", (0, 0), (-1, -1), 2), ("TOPPADDING", (0, 0), (-1, -1), 3),
                          ("BOTTOMPADDING", (0, 0), (-1, -1), 3)]))
story += [info, Spacer(1, 8 * mm)]
api = Table([[para("₹100 WORTH OF AI API CREDITS INCLUDED", "Credit")],
             [para("Each learner receives individually limited classroom API access for the guided AI exercises. Credits are intended for this curriculum and are complemented by mock fallbacks for debugging and outages.", "CenterSmall")]], colWidths=[168 * mm])
api.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), GOLD), ("BOX", (0, 0), (-1, -1), 1.2, NAVY),
                         ("TOPPADDING", (0, 0), (-1, -1), 9), ("BOTTOMPADDING", (0, 0), (-1, -1), 9)]))
story += [api, Spacer(1, 7 * mm), para("Core technology exposure", "H2X"),
          para("Python • Jupyter • OpenRouter • GPT-OSS • Pydantic • LangGraph • Chroma • Sentence Transformers • SQLite • Mem0 • LangSmith • MCP", "BodyX"),
          para("Optional and comparative: Ollama, direct OpenAI API, Langfuse, FastAPI and Docker.", "SmallX"),
          Spacer(1, 6 * mm), para("What is intentionally outside the core", "H2X"),
          para("Agent swarms, CrewAI/AutoGen surveys, browser agents, model training, advanced Graph RAG, Kubernetes, remote production MCP authentication and enterprise deployment. These topics are deferred so students can understand the engineering foundations first.", "BodyX"),
          Spacer(1, 8 * mm)]
closing = Table([[para("LEARN THE LAYERS. BUILD THE SYSTEMS. ENGINEER THE HARNESS.", "Credit")]], colWidths=[168 * mm])
closing.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), MINT), ("BOX", (0, 0), (-1, -1), 1, TEAL),
                             ("TOPPADDING", (0, 0), (-1, -1), 10), ("BOTTOMPADDING", (0, 0), (-1, -1), 10)]))
story += [closing]

doc.build(story)
print(OUT)
