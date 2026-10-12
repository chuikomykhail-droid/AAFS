<!-- CC-EXPORT:README -->
# AI work logs

This folder holds every log of the work on AAFS (raion-level air-raid alert forecasting, see the
[project README](../README.md) and [PLAN.md](../PLAN.md)) from 9 to 12 October 2026, together with an analysis of how
that work was organised.

We used three tools:
- **claude.ai** — discussing the idea, the plan, reviewing the agents' reports;
- **Antigravity** — parallel agents on different models;
- **Claude Code** — the main implementation.

Decisions on what to do, what to accept and what to redo were ours. The agents explored the data, wrote code and
reviews; we checked their conclusions on the data and against each other.

**Contents:**
[Guide](#guide) ·
[How the work was organised](#how-the-work-was-organised) ·
[Key moments](#key-moments) ·
[Analysis of caught errors](#analysis-of-caught-errors) ·
[Index of mentions](#index-of-mentions)

The reflection is in [REFLECTION.txt](REFLECTION.txt).

---

## Guide

### If you are short on time

1. [Workflow diagram](#diagram) and [timeline](#timeline) — the whole picture in a minute.
2. [Three stage-1 agents and how their reports were checked](#1-three-agents-on-one-task-agreement-is-not-verification) —
   why agreement between agents proves nothing.
3. [Our question that found a leak](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-8d9ffcec)
   (Claude Code, 11.10 02:32). The tests did not catch it.
4. [The project review by two lines of agents](#5-review-by-two-independent-lines-of-agents) and
   [the question that led to fixing hyperparameter tuning](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-b33039de).
5. [Analysis of the 32 caught errors](#analysis-of-caught-errors).

### Folder structure

```
ai_logs/
├── README.md                    ← this file
├── REFLECTION.txt               ← reflection (~100 words, plain text)
├── export_claude_code.py        ← export script for Claude Code and claude.ai (secret redaction, table below)
├── claude_ai/                   ← 1. planning chat (claude.ai, browser)
│   ├── chat_planning.md
│   └── raw/chat_planning.jsonl
├── antigravity/                 ← 2. Antigravity (exported by the agents themselves)
│   ├── main_dialogue.md         ←    main chat: launching agents, stages 1b–2, reviews
│   ├── raw/                     ←    its raw JSONL (compact and _full)
│   ├── stage1_agents/           ←    stage-1 agents, each with a README, dialogue log and raw/
│   │   ├── claude_opus/
│   │   ├── gemini_flash/
│   │   └── gemini_pro/
│   └── review_agents/           ←    7 review agents (gemini-3.1-pro): stage*.md and raw/
└── claude_code/                 ← 3. Claude Code
    ├── <date>_<topic>_<id>.md   ←    three sessions; the longest is split by day
    ├── review_agents/           ←    8 review agents from the critical-analysis session
    └── raw/claude_code_raw.zip  ←    source JSONL of all sessions and agents (41.5 MB → zip)
```

Auxiliary Claude Code sessions are not included, among them the session in which this export was prepared.

### Contents of the logs

<!-- AUTO:table -->
**claude.ai — planning chat**

| File | Period (Kyiv) | Messages | First user message |
|---|---|---|---|
| [claude_ai/chat_planning.md](claude_ai/chat_planning.md) | 2026-10-09 23:20 → 2026-10-12 22:47 | 54 | Мне нужно сделать тестовое задание: Congratulations! Your Stage 1 application demonstrated the crit… |

**Antigravity — main chat**

| File | Period (Kyiv) | Messages | First user message |
|---|---|---|---|
| [antigravity/main_dialogue.md](antigravity/main_dialogue.md) | 2026-10-10 10:57 → 2026-10-12 22:02 | 101 | синхронизируй проэкт с репозиторием https://github.com/chuikomykhail-droid/AAFS |

**Antigravity — stage-1 agents**

| File | Period (Kyiv) | Messages | First user message |
|---|---|---|---|
| [antigravity/stage1_agents/claude_opus/main_dialogue.md](antigravity/stage1_agents/claude_opus/main_dialogue.md) | 2026-10-10 17:02 → 2026-10-12 23:23 | 29 | Ты один из трех параллельных агентов и будешь работать с веткой claude-opus. Твоя задача:прочитать … |
| [antigravity/stage1_agents/gemini_flash/chat.md](antigravity/stage1_agents/gemini_flash/chat.md) | 2026-10-10 11:50 → 2026-10-12 23:10 | 9 | Ты один из трех параллельных агентов и будешь работать с веткой gemini-flash. Твоя задача: прочитат… |
| [antigravity/stage1_agents/gemini_pro/chat.md](antigravity/stage1_agents/gemini_pro/chat.md) | 2026-10-10 11:51 → 2026-10-12 23:17 | 8 | Ты один из трех параллельных агентов и будешь работать с веткой gemini-pro. Твоя задача: прочитать … |

**Antigravity — review agents (gemini-3.1-pro)**

| File | Period (Kyiv) | Messages | First user message |
|---|---|---|---|
| [antigravity/review_agents/stage0-1b.md](antigravity/review_agents/stage0-1b.md) | 2026-10-11 21:08 → 2026-10-11 21:13 | 6 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |
| [antigravity/review_agents/stage2.md](antigravity/review_agents/stage2.md) | 2026-10-11 21:08 → 2026-10-11 21:17 | 4 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |
| [antigravity/review_agents/stage3.md](antigravity/review_agents/stage3.md) | 2026-10-11 21:07 → 2026-10-11 21:12 | 5 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |
| [antigravity/review_agents/stage4-6.md](antigravity/review_agents/stage4-6.md) | 2026-10-11 21:09 → 2026-10-11 21:24 | 5 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |
| [antigravity/review_agents/stage5-leakage.md](antigravity/review_agents/stage5-leakage.md) | 2026-10-11 21:07 → 2026-10-11 21:22 | 13 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |
| [antigravity/review_agents/stage7.md](antigravity/review_agents/stage7.md) | 2026-10-11 21:06 → 2026-10-11 21:20 | 16 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |
| [antigravity/review_agents/stage8.md](antigravity/review_agents/stage8.md) | 2026-10-11 21:06 → 2026-10-11 21:17 | 16 | The following is a not actually sent by the user. It is provided by the system as important informa… *(task given to the agent)* |

**Claude Code — sessions and review agents**

| File | Period (Kyiv) | Messages | First user message |
|---|---|---|---|
| [2026-10-11_stage2-plan-decisions_2d7ee671.md](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md)<br>[2026-10-12_stage2-plan-decisions_2d7ee671.md](claude_code/2026-10-12_stage2-plan-decisions_2d7ee671.md) | 2026-10-11 01:31 → 2026-10-12 18:12 | 124 | Проанализируй файлы @PLAN.md и @DECISIONS.md , в них описана общая идея проекта над которым я работ… |
| [2026-10-11_critical-analysis_57049ae5.md](claude_code/2026-10-11_critical-analysis_57049ae5.md) | 2026-10-11 08:46 → 2026-10-12 14:32 | 51 | Проведи глубокий критический анализ проекта согласно файлам @PLAN.md и @DECISIONS.md Сейчас проект … |
| ↳ [review-stage-5-and-leakage_a2210cb8.md](claude_code/review_agents/review-stage-5-and-leakage_a2210cb8.md) | 2026-10-11 20:19 → 2026-10-12 08:53 | 1 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| ↳ [review-stage-2_a3bb0394.md](claude_code/review_agents/review-stage-2_a3bb0394.md) | 2026-10-11 20:19 → 2026-10-12 08:50 | 1 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| ↳ [synthesize-claude-and-gemini-reviews_a3fd7a77.md](claude_code/review_agents/synthesize-claude-and-gemini-reviews_a3fd7a77.md) | 2026-10-12 08:53 → 2026-10-12 09:21 | 1 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; есть Bash (Git Bash) и PowerShell). Се… |
| ↳ [review-stages-4-and-6_a62651ca.md](claude_code/review_agents/review-stages-4-and-6_a62651ca.md) | 2026-10-11 20:19 → 2026-10-12 08:46 | 2 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| ↳ [review-stage-3_a893a512.md](claude_code/review_agents/review-stage-3_a893a512.md) | 2026-10-11 20:19 → 2026-10-12 08:51 | 4 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| ↳ [review-stage-7-report_a897305d.md](claude_code/review_agents/review-stage-7-report_a897305d.md) | 2026-10-11 20:19 → 2026-10-12 08:45 | 2 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| ↳ [review-stage-8-api-check_aa72d8eb.md](claude_code/review_agents/review-stage-8-api-check_aa72d8eb.md) | 2026-10-11 20:19 → 2026-10-12 08:46 | 1 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| ↳ [review-stages-0-1b_ab787b28.md](claude_code/review_agents/review-stages-0-1b_ab787b28.md) | 2026-10-11 20:19 → 2026-10-12 08:43 | 1 | Рабочая папка проекта: d:\Flash\golova\KSE_AI\AAFS (Windows; доступны Bash (Git Bash) и PowerShell)… |
| [2026-10-12_yellow-red-alerts_0efe39d2.md](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md) | 2026-10-12 18:13 → 2026-10-12 21:45 | 54 | В этом проекте я разрабатываю систему анализа архива воздушных тревог, подробнее можешь прочитать в… |

Messages = user messages + text replies of the assistant; tool calls are not counted. For agents, the "user" is whoever launched them: the main agent or the first prompt. The logs are in Russian.
<!-- /AUTO:table -->

### How to read

- **Claude Code** (`claude_code/`). Each file header gives the session id, period and number of messages. All
  times are Kyiv time. Tool calls are collapsed into "🔧 Tool: what it does" blocks; arguments are cut to 2000
  characters, results to 3000. System inserts and thinking blocks are omitted but kept in the source JSONL. Where
  an agent is launched there is a link to its log, and the agent's log links back. The logs themselves are in
  Russian, as the work was.
- **Antigravity** (`antigravity/`). Exported by the agents themselves, so the format is their own and headings are
  in Ukrainian. `raw/` has a compact and a full (`_full`) JSONL for every chat.
- **claude.ai** (`claude_ai/`). Exported from the browser as JSON and Markdown.
- **Secrets.** The alerts.in.ua token and the author's email are replaced with `[REDACTED_TOKEN]` /
  `[REDACTED_EMAIL]` in Markdown and raw files. A `grep` over the whole folder, including the zip contents, finds
  nothing. How it is done — [export_claude_code.py](export_claude_code.py).

---

## How the work was organised

### Diagram

```
claude.ai (planning chat) ── idea, architecture, PLAN.md; reviewing reports; plan changes (stage 8, D23)
   │
   ├─► Antigravity: 3 agents on different models, stage 1, independently
   │      └─► three reports reviewed in claude.ai → updated plan, working rules for agents
   ├─► Antigravity, main chat: finishing stage 1 (1b) and stage 2
   ├─► Claude Code "stage 2 review": review → refactoring → stages 3–6 → 7–8
   ├─► review of the whole project: 7 agents in Antigravity and 7 in Claude Code (+ a summarising one)
   │      └─► confirmed findings fixed in Claude Code
   └─► Claude Code "yellow and red alerts": D23, final discussion, README
```

| Tool | Role | Models |
|---|---|---|
| claude.ai | Discussing the task and architecture, `PLAN.md`; reviewing agents' reports; plan changes (stage 8, D23); writing prompts for agents | Claude Opus |
| Antigravity | Stage 1 by three agents independently; finishing stage 1 and stage 2; review (7 agents); second opinion on review findings | Gemini Flash, Gemini Pro, Claude Opus 4.6; gemini-3.1-pro |
| Claude Code | Stage 2 review and implementation of stages 2–8 and D23; critical analysis of the project (8 agents); README | Claude Opus |

The principle: the plan and contested questions were discussed in a separate chat with no code in it.
Implementation was done by agents. Every stage's report was checked by someone else: the planning chat, an agent on
another model, or a separate review session.

### Timeline

| Time (Kyiv) | Where | What | Log |
|---|---|---|---|
| 9.10 23:20 – 10.10 00:29 | claude.ai | Task breakdown, leakage-free backtest, data sources, first `PLAN.md` | [chat_planning.md](claude_ai/chat_planning.md) |
| 10.10 10:57 – 17:19 | Antigravity | Setting up parallel work; three agents on stage 1 (Gemini from 11:50, Claude Opus 17:02–17:19) | [main_dialogue.md](antigravity/main_dialogue.md), [stage1_agents/](antigravity/stage1_agents/) |
| 10.10 20:33 – 22:50 | claude.ai | Review of the three reports; manual check of the channel; new plan with stage 1b | [chat_planning.md](claude_ai/chat_planning.md) |
| 10.10 23:01 – 11.10 01:08 | Antigravity | Gemini Flash's work taken as the base; stage 1b finished, stage 2 done | [main_dialogue.md](antigravity/main_dialogue.md) |
| 11.10 00:03 | claude.ai | Review of the stage-1 completion report | [chat_planning.md](claude_ai/chat_planning.md) |
| 11.10 01:31 – 11:42 | Claude Code | Stage 2 review, refactoring, stages 3–6 | [stage2-plan-decisions, 11.10](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md) |
| 11.10 08:46, 15:08 | Claude Code | Critical analysis: at stage 6 and after the project was complete | [critical-analysis](claude_code/2026-10-11_critical-analysis_57049ae5.md) |
| 11.10 11:27 – 11:42 | claude.ai → Claude Code | alerts.in.ua token received: stage 8 added to the plan; stages 7–8 | [chat_planning.md](claude_ai/chat_planning.md), [stage2-plan-decisions](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-07b1cfda) |
| 11.10 13:39 | Antigravity | Independent review of the stage 3 implementation | [main_dialogue.md](antigravity/main_dialogue.md) |
| 11.10 20:19 – 12.10 09:21 | Claude Code | 7 review agents by stage and 1 summarising agent; paused overnight by the usage limit | [review_agents/](claude_code/review_agents/) |
| 11.10 21:05 – 21:24 | Antigravity | 7 review agents on gemini-3.1-pro | [review_agents/](antigravity/review_agents/) |
| 12.10 12:33 – 14:30 | Antigravity, Claude Code | Cross-checking review findings; fixes in a separate branch | [main_dialogue.md](antigravity/main_dialogue.md), [critical-analysis](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-b33039de) |
| 12.10 14:37 – 18:08 | Claude Code | README in English; API data downloaded again | [stage2-plan-decisions, 12.10](claude_code/2026-10-12_stage2-plan-decisions_2d7ee671.md#m-84054240) |
| 12.10 18:07 – 21:45 | claude.ai → Claude Code | Two alert levels (D23); final discussion and README | [yellow-red-alerts](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md) |

---

## Key moments

### 1. Three agents on one task: agreement is not verification

**10.10, Antigravity and claude.ai.** We gave stage 1 (exploring the data structure) to three agents on different
models — Claude Opus 4.6, Gemini Pro and Gemini Flash. Each worked in its own copy of the repository and its own
branch ([launch](antigravity/main_dialogue.md), 11:19; logs —
[claude_opus](antigravity/stage1_agents/claude_opus/main_dialogue.md),
[gemini_flash](antigravity/stage1_agents/gemini_flash/chat.md),
[gemini_pro](antigravity/stage1_agents/gemini_pro/chat.md)). The Gemini agents started at 11:50, Claude Opus at 17:02.

The reports disagreed, and we checked the disagreements with short scripts on the data rather than by majority
vote ([review in claude.ai](claude_ai/chat_planning.md), 10.10 20:33). Every agent was wrong somewhere:
- Claude and Gemini Pro concluded from a naive `groupby().min()` that raion-level alerts started in 2022 (error 1);
- Gemini Flash and Gemini Pro missed that 38% of the rows were duplicates (error 3);
- Gemini Flash decided that Donetsk oblast was not split into raions (error 4).

Agreement proved nothing either. All three agents reported tens of thousands of overlapping alerts that do not
exist after deduplication (error 2), and none noticed that the official series had stopped on 7 September.

We checked the latter ourselves: we opened the Telegram channel and confirmed that its last post was from September
([claude.ai](claude_ai/chat_planning.md), 10.10 22:03; D02). After the review we added stage 1b, working rules for
agents and a reference table of numbers to the plan. From then on every new number was checked against that table.

### 2. Finishing stage 1: questions to the agent

**10–11.10, Antigravity main chat** ([main_dialogue.md](antigravity/main_dialogue.md)). We took Gemini Flash's work as
the base and finished stage 1b. The agent had to be stopped on details:
- 00:46 — "Why 2023–2024? We don't analyse those years." The stage 2 review later found that the period filter had
  never been implemented (error 15);
- 00:53 — mask rule (b) in `mask.py` measured from the end of the alert, while the plan said from the start. It was
  changed to the start, as in the plan.

The mask covered 5.53% of the test against a "more than 5% — discuss" threshold, and stage 2 started without that
discussion. The review in Claude Code flagged the rule violation (error 14), and examining the excess led to the
review's main finding — a four-day outage of the channel inside the test window (D15).

Two more agent errors surfaced in review. The conclusion about threat messages was recorded as verified, although
the agent's actions included neither reading the channel nor a manual check (error 11). The agent set D10 to
"settled" before checking it against the expected numbers (error 12).

### 3. Stage 2 review and a leak the tests did not catch

**11.10, Claude Code** ([log](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md)).
- **[01:31](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-941558f2).** A Claude Opus agent reviewed
  stage 2. It found the channel outage of 29.08–02.09 (error 13) and the missing period filter (error 15).
- **[01:57](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-a2c00c20).** We confirmed the outage on the
  channel and decided not to rush stage 3: stage 2 had to be redone first.
- **[02:32](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-8d9ffcec).** Our question about the order of
  operations: "the invented end is already recorded, and we look before the next alert starts — isn't that a leak
  from the future?"

The answer was yes. In 3,529 "unit × moment" pairs `AlertHistory` answered "quiet" although nobody had seen an
all-clear (error 20). The "corrupt the future" test cannot see such a leak by construction: the source itself
creates it by writing the end of the alert retroactively. This is where the `seen` table and `open_until` came
from (D16).

- **[10:27](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-ac8696cb).** A second question, about the
  architecture: "with every new feature one has to remember what to take from `intervals` and what from `seen`;
  can this be made safer?"

The analysis showed that a feature reading a retroactively recorded end passed the leakage check (error 23). This
led to closed access to history and a knowledge-at-cutoff check that fails on such a substitution (D21).

We queued stages 3–6 ([02:50](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-ec3463c8)), each one
starting with "tighten the weak spots" of the previous one.

### 4. Fresh data from another source and an honest baseline

**11.10 11:27, claude.ai → [Claude Code, 11:42](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-07b1cfda).**
Having received the alerts.in.ua token, we discussed in the planning chat what it changes. We decided not to merge
the sources but to run a separate check: the model frozen on 7 September against baselines on the API data
(stage 8).

The first result — a +0.09 PR-AUC gain — would have been three times too high: the frozen baseline had gone stale
together with its table. The agent noticed this itself and added a baseline updated on the API data (error 26).
Against it the gain is +0.017 at h = 3, with an interval that touches zero. The README says exactly that.

### 5. Review by two independent lines of agents

**11–12.10.** Once the project was complete, we ran a stage-by-stage review in two lines:
- **Claude Code.** 7 agents, one per stage or group of short stages
  ([prompts](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-3f0ef773),
  [launch](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-17af9eb5), [logs](claude_code/review_agents/)).
  The weekly usage limit stopped them overnight; in the morning we
  [resumed](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-ebff079d) them, and an eighth agent merged the
  Claude and Gemini reviews into one list.
- **Antigravity.** 7 agents on gemini-3.1-pro ([logs](antigravity/review_agents/)).

We did not take the findings on trust but checked them:
- **Hyperparameter tuning.** To our [question](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-b33039de)
  "did LightGBM choose the number of trees by peeking into the test? That breaks rule 6" the answer was "formally,
  yes": for the last `h` hours of validation the label window reached into the test (error 28). We fixed it and
  re-ran tuning; the choice did not change at any horizon.
- **The API data period.** A bug found by the stage-8 review agent (`data_end` taken as a minimum) we gave to two more
  agents: first Antigravity (12.10 12:56), then
  [Claude Code (14:15)](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-1f246dcc), both times as "look at the
  code without changing anything". Both confirmed it: downloading again on Monday would have shortened the period
  instead of extending it (error 29). Fixed in a
  [separate branch](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-33bfe373), with a test for an interrupted
  download.
- **Dependence between neighbouring days.** In Antigravity (11.10 22:30) we asked: drone attacks come in waves lasting
  several days, so neighbouring days are dependent — does the gain survive a bootstrap over 3-day blocks? The
  summarising review checked 7-day blocks (F24). At h = 6 the interval touches zero, and the gain survives all
  robustness checks only at h = 1 — as D20 and the README state.

### 6. Two alert levels and scope control on the last day

**12.10, claude.ai → Claude Code** ([log](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md)).

We remembered that Ukraine introduced yellow and red alerts in September, and that the API check window lies
entirely in the new regime (claude.ai, 18:07). The prompt for the agent was written in the planning chat, with hard
limits: 2.5 hours, no retraining of models, no changes to hyperparameters
([18:13](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-2a06390d)).

Checking every number of the text against the report caught three discrepancies in the D23 draft (error 31).
Counting areas refuted the claim "a red alert covers the whole oblast", which was already in the README (error 32).

With 3.5 hours left before the deadline we
[asked](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-a24c881b) whether a live forecast was worth doing, and
decided against it: it is in the plan as the next step.

We [restructured](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-478cc867) the README assuming its first
screening might also be done by AI: strict, specific statements, the main points first. The discrepancy between D20
and the README was [resolved](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-5a1fda93) before submission.

---

## Analysis of caught errors

The full journal is the «Пойманные ошибки ИИ» (caught AI errors) section of [DECISIONS.md](../DECISIONS.md), 32 entries, in Russian.

### Where they came from

| Source | Errors | Count |
|---|---|---|
| Stage-1 agents (Claude, Gemini Pro, Gemini Flash) | 1–7, 10 | 8 |
| Planning chat (wording of the plan) | 8, 9, 18; partly 13 | 3–4 |
| Antigravity agent, stages 1b–2 | 11, 12, 14–17 | 6 |
| Claude Code, stages 2–8 and D23 | 19–32 | 14 |

Claude Code has more errors not because it erred more often: it wrote most of the code, and by then the checks had
become automatic and caught more.

### Types

1. **Confident claim without verification** — the most frequent type: 1, 4, 6, 8, 9, 11, 25, 27, 32.
   - The most telling case is 11: the conclusion was recorded as verified, but no verification was done. The
     conclusion turned out to be right, the justification invented.
   - Error 8 is in the plan: the planning-chat assistant took "the dataset is updated daily" from the dataset's
     README without checking.
2. **Counting on dirty data or in the wrong order:** 2, 3, 7, 15, 16. Hence rules 2 and 8 in the plan: deduplicate
   before any counting, check against the reference table.
3. **Leakage and time subtleties** — the most dangerous: 18, 20, 21, 23, 28, 29. They do not show in the metrics and
   passed the existing tests.
   - In 20 the leak was created by the source itself, writing an invented alert end retroactively.
   - In 28 the training part of tuning was cut correctly, but the symmetric cut of validation was missed — while the
     docstring claimed otherwise.
4. **Silent data loss in code:** 17, 24, 30. For example, different apostrophes (U+2019 and U+0027) would have
   silently dropped three raions and 454 records (24).
5. **Inflated or unconfirmed result:** 26, 27, 31, 32 — a gain inflated threefold, or text that contradicts its own
   report.
6. **Process violation:** 12, 14 — "settled" status before verification; stage 2 started without discussing the
   mask threshold being exceeded.

### How they were caught

| Method | Errors |
|---|---|
| Cross-checking agents on the data (stage 1) | 1–4, 6, 7, 10 |
| Review by a separate agent or session | 11–18, 28, 29 |
| Our questions about logic and architecture | 20, 23; confirming 13 on the channel |
| Automatic reconciliation and completeness checks | 16, 19, 24, 30 |
| Examining a result before publishing: where does this number come from, does the text match the report | 21, 22, 26, 27, 31, 32 |
| Methodological analysis | 5, 8, 9 |

### Conclusions

- **Agreement between agents is not evidence.** What helped was not the number of agents but checking their
  disagreements with a script on the data.
- **A test catches only the class of errors it was written for.** Both leaks found by our questions (20, 23) passed
  the "corrupt the future" test. The class was closed by a new check (D21), not by re-running the old one.
- **Review by another agent paid off.** The most serious late findings (13, 15, 28, 29) came from review, not from the
  agent that wrote the code. Two review lines on different models complemented each other, and a contested finding is
  worth giving to two agents independently.
- **Automatic reconciliation with reference numbers eventually started catching errors on its own** (19, 24, 30).
- **A failing test does not always mean a bug in the code.** In 22 five test expectations were wrong and the code was
  right. Every failure was analysed on the data; none was "fixed" by bending the code.
- **AI was wrong more often in claims about data and results than in code.** Hence the main rule: re-check every
  number and every conclusion on the data before it goes into a document.

---

## Index of mentions

<details><summary>Places in the logs that mention errors, review, leakage and decision numbers (collected by script)</summary>

<!-- AUTO:candidates -->
Collected by script from keywords (Russian, Ukrainian and English); an index, not conclusions.

#### Caught errors

Claude Code — user messages (8 of 8):
- [Claude Code 2d7ee671 · 2026-10-11 01:57](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-a2c00c20) — «…тику. Добавь два теста которыъ не хватает Строки в журнал ошибок ИИ тоже делай»
- [Claude Code 2d7ee671 · 2026-10-11 02:32](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-8d9ffcec) — «…мотрели, получается что произошла утечка из будущего? Или я неправильно понимаю последовательность этих операций?»
- [Claude Code 2d7ee671 · 2026-10-11 02:36](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-d5557879) — «Да, сделай исправление и записывай в журнал ошибок ИИ»
- [Claude Code 2d7ee671 · 2026-10-11 11:41](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-87403d84) — «…дробно следуя инструкциям. Внимательно отнесись к возможным ошибкам (в том числе с апи) Документация апи: https://devs.alerts.in.ua/ Токен лежит в файле @alerts_api»
- [Claude Code 2d7ee671 · 2026-10-11 11:42](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-07b1cfda) — «…дробно следуя инструкциям. Внимательно отнесись к возможным ошибкам (в том числе с апи) Документация апи: https://devs.alerts.in.ua/ Токен лежит в файле @alerts_api»
- [Claude Code 57049ae5 · 2026-10-12 14:15](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-1f246dcc) — «…ь исправить и доавить в D20 и журнал. А вот езще по поводу бага в api check : data_end берется как минимум. Мне ведь нужно сегодлня обновить данные. Но ведь стары»
- [Claude Code 0efe39d2 · 2026-10-12 20:42](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-478cc867) — «… заинтересованного читателя. Также я бы добавил из журнала ошибок несколько самых ярких найденых ошибок с конкретным указанием что случилось бы если бы она не была»
- [Claude Code 0efe39d2 · 2026-10-12 20:55](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-667a29f1) — «…ожно и сейчас не в приоритете? А вот по поводу наличия там ошибок ии уже не знаю: для этого есть лог, а реадми как будто бы должен представлять продукт а не такие»

Claude Code — assistant replies (8 of 40):
- [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «…ики на наблюдаемое (незамаскированное) время. - Для журнала ошибок ИИ это сильная запись: три агента и ассистент планирования видели симптом и не нашли причину. --»
- [Claude Code 2d7ee671 · 2026-10-11 03:46](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-bd5cd908) — «… добавлены записи D17–D20, обновлены D16 и D18; - в журнале ошибок ИИ новые строки 21–22: ошибка в первоначальном замысле проверки утечки и пять неверных ожиданий в»
- [Claude Code 2d7ee671 · 2026-10-12 17:49](claude_code/2026-10-12_stage2-plan-decisions_2d7ee671.md#m-679052c8) — «…нье просто не было конца. **Нашёл и исправил ещё одну свою ошибку (строка 30 журнала).** Сравнения с волонтёрским рядом шли по всему периоду API, хотя закреплённый»
- [Claude Code 57049ae5 · 2026-10-12 08:41](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-04651a8e) — «…ini я уже вижу повод для перепроверки: - **Колонка «Кто».** Ошибки в коде там приписаны Gemini, хотя код этапов 2–8 писал Claude Code. - **Находка S2-1 про 'merge_l»
- [Claude Code 57049ae5 · 2026-10-12 08:51](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-7f936d12) — «…остановку канала на 49 прошлых днях. Ожидаемый ущерб — 0–10 неверных строк на 46 270 строк теста, то есть D13 подтверждается. Здесь он расходится с Gemini: тот насчит»
- [Claude Code 57049ae5 · 2026-10-12 14:27](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-4214a6bb) — «… какой-то области нет ни в одном файле, 'api_config' выдаёт ошибку. - **Тест** \[tests/test_api_config.py\](tests/test_api_config.py), 5 случаев: одно скачивание; два»
- [Claude Code 0efe39d2 · 2026-10-12 20:30](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-372b30c1) — «… ещё одну яркую вещь:** инфографика процесса — 32 пойманные ошибки ИИ по этапам, кто ошибся и кто поймал. Это прямо про критерий оценки, и данные уже лежат в DECISI»
- [Claude Code 0efe39d2 · 2026-10-12 21:43](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-f9b27be8) — «…ницы около 0,60. Фраза «Сумская и Харьковская наравне» была неверна: там B1 лучше. - **Подбор (F27).** Параметры даны для всех трёх горизонтов. Довод «все четыре лучш»

claude.ai and Antigravity — user messages (3 of 3):
- [claude.ai · 2026-10-11 00:03](claude_ai/chat_planning.md) — «…времени и положительных длительностей). Исправляю небольшую ошибку в проверке часового пояса (из-за версии библиотеки 'pandas' в тесте) и перепроверяю загрузчик дан»
- [Antigravity · 2026-10-11 22:30](antigravity/main_dialogue.md) — «…еобучения? И есть ли какие то стандарты как учитывают такие ошибки (если это вообще стоит делать) ?»
- [Antigravity · 2026-10-12 12:56](antigravity/main_dialogue.md) — «Мг, а вот давай обратим внимание на баг найденвй баг в api check, : data_end берется как минимум. Мне ведь нужно сегодлня обновить данные.»

claude.ai and Antigravity — assistant replies (6 of 21):
- [claude.ai · 2026-10-09 23:23](claude_ai/chat_planning.md) — «…чу **Случайное разбиение на train/test.** Это самая частая ошибка. Соседние часы почти одинаковы: если тревога была в 14:00 и в 16:00, то в 15:00 она почти наверня»
- [claude.ai · 2026-10-10 22:51](claude_ai/chat_planning.md) — «… дорогой агент нужнее не там, где больше работы, а там, где ошибки трудно заметить. **Где ошибки видны сразу, а где нет.** Для этапа 1б у нас уже есть эталон: ожид»
- [Antigravity · 2026-10-10 23:56](antigravity/main_dialogue.md) — «Исправляю небольшую ошибку в проверке часового пояса (из-за версии библиотеки 'pandas' в тесте) и перепроверяю загрузчик дан»
- [Antigravity · 2026-10-11 20:44](antigravity/main_dialogue.md) — «…** * Агенты будут ориентированы на выявление критических ошибок, утечек данных (data leakage), расхождений с \['PLAN.md'\](file:///D:/Flash/golova/KSE_AI\AAFS\PLAN»
- [Antigravity · 2026-10-12 12:58](antigravity/main_dialogue.md) — «…g.py', файли проекту не змінювалися). --- ### 1. Механізм бага в коді Код, де криється проблема: * \['src/alerts/api_check.py:33-37'\](file:///D:/Flash/golova/KSE»
- [Antigravity · 2026-10-10 17:24](antigravity/stage1_agents/gemini_flash/chat.md) — «…NS.md)** со всеми нашими выводами, обоснованиями и разбором ошибок ИИ. 2. Файл 'DECISIONS-gemini-flash.md' синхронизирован с ним и зафиксирован в git, чтобы в любом»

#### Review

Claude Code — user messages (4 of 4):
- [Claude Code 2d7ee671 · 2026-10-11 01:31](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-941558f2) — «…лизация этапа 2. Твоя задача: сделать детальный критический ревью того, что уже сделано. Оценить насколько соблюдены требования, выявить слабые места. Помимо общего»
- [Claude Code 57049ae5 · 2026-10-11 08:46](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-23a37b90) — «…ь работу системы? Где возможно хромает архитектура? Сделай ревью»
- [Claude Code 57049ae5 · 2026-10-11 20:04](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-3f0ef773) — «Хочу параллельно запустить агентов для ревью каждого из этапов (возможно разве что обьеденить короткие этапы). Сделай промпты для этого»
- [Claude Code 57049ae5 · 2026-10-12 14:10](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-b33039de) — «…ия пока не запускай. Про рефлексию и сдачу пока не думай В ревью біло упомянуто, что при tuning на валидации таргет заглядывает в первые часы теста. Получается, Li»

Claude Code — assistant replies (8 of 25):
- [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «# Ревью этапов 1б–2 ## Главное Ядро этапа 2 написано правильно. Я пересчитал объединение интервалов други»
- [Claude Code 57049ae5 · 2026-10-11 08:59](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-98c838f1) — «# Ревью проекта на этапе 6 Я прочитал весь код в 'src/', 'tests/' и 'scripts/', а подозрения проверил на д»
- [Claude Code 57049ae5 · 2026-10-11 20:19](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-bf2cca62) — «…скаю все семь агентов в фоне: каждый читает свой промпт из 'reviews/prompts/' и пишет отчёт в 'reviews/'. Сводный агент стартует, когда отработают все семь.»
- [Claude Code 57049ae5 · 2026-10-12 08:44](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-be98fa89) — «Первый из семи агентов, этапы 0–1б, закончил: отчёт в \[reviews/claude/stage0-1b.md\](reviews/claude/stage0-1b.md). Критичных находок нет, существенных три. - **S»
- [Claude Code 57049ae5 · 2026-10-12 08:50](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-595d09c2) — «Готов пятый агент, этап 2: отчёт в \[reviews/claude/stage2.md\](reviews/claude/stage2.md). Критичного нет. Слой данных проверен основательно: фу»
- [Claude Code 57049ae5 · 2026-10-12 08:53](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-7dd5fa49) — «…акончили. Последним был этап 5 и защита от утечки: отчёт в \[reviews/claude/stage5-leakage.md\](reviews/claude/stage5-leakage.md). Критичного нет, признаки посчитаны пр»
- [Claude Code 57049ae5 · 2026-10-12 14:11](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-4039036c) — «…нал не затрагивает. **Проверено, что выбор не изменился.** Ревьюер этапа 3 повторил подбор без этих строк. Выбор совпал полностью, включая число деревьев: \| h \| со»
- [Claude Code 0efe39d2 · 2026-10-12 21:45](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-779fdc64) — «…' коммитом 'a287f89 D20 brought in line with README and the review (F23-F29, F39)'. В коммит вошли только 'DECISIONS.md' и 'PLAN.md'. Ветка совпадает с удалённой, нез»

claude.ai and Antigravity — user messages (4 of 4):
- [claude.ai · 2026-10-10 17:33](claude_ai/chat_planning.md) — «… меньше тратить). Поэтому пишу костяк через антигравити, а ревью и доработку буду уже делать с клаудом. Но оцени и это: может на этом этапе все таки стоило бы проан»
- [claude.ai · 2026-10-10 22:50](claude_ai/chat_planning.md) — «…е на следующие этапы пущу антигравити, которого потом будет ревьюить опять опус. Что скажешь? возможно еще какие то этапы критически важны и их тоже стоит сразу пор»
- [Antigravity · 2026-10-11 20:43](antigravity/main_dialogue.md) — «…ов на модели gemini-3.1-pro, каждый из которых будет делать ревью одного-двух этапов проекта. Соответсвующие промпты возьми в @\[reviews/prompts\] . ВАЖНО: скрипты ко»
- [Antigravity · 2026-10-12 12:33](antigravity/main_dialogue.md) — «Проанализируй дополнительно ревью другого агента, лежит в папке @\[reviews/claude\]»

claude.ai and Antigravity — assistant replies (6 of 35):
- [claude.ai · 2026-10-09 23:21](claude_ai/chat_planning.md) — «… признаках, внутри написаны на C++. **Риск при проверке.** Ревьюеры будут запускать код, а сборка расширения на pybind11 на чужой машине часто ломается. В задании п»
- [Antigravity · 2026-10-11 20:58](antigravity/main_dialogue.md) — «…переключите политику с *«Ask for confirmation»* / *«Request review»* на **«Always allow»** (или аналогичный разрешающий статус). --- > 💡 **Совет:** В левой колонке»
- [Antigravity · 2026-10-11 21:17](antigravity/main_dialogue.md) — «…- ✅ **Stage 8 (Проверка на свежих данных alerts.in.ua):** \['reviews/stage8.md'\](file:///D:/Flash/golova\KSE_AI\AAFS\reviews\stage8.md) Среди его ключевых находок: *»
- [Antigravity · 2026-10-12 12:35](antigravity/main_dialogue.md) — «Проведено детальний порівняльний аналіз рев’ю обох незалежних агентів: **Claude** ('reviews/claude/') та **Gemini Pro** ('reviews/' та 'reviews/S»
- [Antigravity · 2026-10-11 21:12](antigravity/review_agents/stage3.md) — «Ревью этапа 3 (сетка и целевая переменная) завершено. Детальный отчёт сохранён в файле \['reviews/stage3.»
- [Antigravity · 2026-10-11 21:17](antigravity/review_agents/stage8.md) — «Ревью этапа 8 полностью завершено. Детальный отчёт записан в \[reviews/stage8.md\](file:///D:/Flash/golova/»

#### Leakage

Claude Code — user messages (8 of 8):
- [Claude Code 2d7ee671 · 2026-10-11 01:31](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-941558f2) — «… старых результатов (до реформы тревог) 4) Не происходит ли утечек из будущего 5) Строго ли соблюдено разбитие на районы 6) Насколько архитектурно проект готов к р»
- [Claude Code 2d7ee671 · 2026-10-11 02:32](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-8d9ffcec) — «…того, в какое время мы посмотрели, получается что произошла утечка из будущего? Или я неправильно понимаю последовательность этих операций?»
- [Claude Code 2d7ee671 · 2026-10-11 11:41](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-87403d84) — «…, его не должно быть в контроле версий, он не должен никуда утечь.»
- [Claude Code 2d7ee671 · 2026-10-11 11:42](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-07b1cfda) — «…, его не должно быть в контроле версий, он не должен никуда утечь.»
- [Claude Code 57049ae5 · 2026-10-11 08:46](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-23a37b90) — «…акие слабые места ты можешь выделить? Где могут происходить утечки или любые другие неточности, которые могут нарушить работу системы? Где возможно хромает архитек»
- [Claude Code 57049ae5 · 2026-10-11 15:08](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-86c9c6f2) — «…абое место 1: Скрытая селекция по будущему в bridged_pause (Lookahead bias) Механизм: Если в момент 𝑡 t в юните тихо, но эта тишина является паузой ≤ 15 ≤15 минут межд»
- [Claude Code 57049ae5 · 2026-10-12 14:10](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-b33039de) — «… В ревью біло упомянуто, что при tuning на валидации таргет заглядывает в первые часы теста. Получается, LightGBM формально подбирал число деревьев, заглядывая в тест?»
- [Claude Code 0efe39d2 · 2026-10-12 20:42](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-478cc867) — «…ких но добротных решений можно упомянуть run_all и проверки утечек. В общем, не так скромно давай перепишем»

Claude Code — assistant replies (8 of 31):
- [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «…sv' относятся к 2022–2025 годам. 3. **Важно.** Склейка пауз заглядывает на 15 минут вперёд для признаков других единиц. Запланированное правило масок выбрасывает строки»
- [Claude Code 2d7ee671 · 2026-10-11 02:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-ceb77260) — «…k.csv' и 'units.csv' совпали с прошлой версией. - **Масштаб утечки**, которую закрыло исправление: 3 529 пар «единица × момент», затронуто 358 часовых моментов (5%)»
- [Claude Code 2d7ee671 · 2026-10-11 10:29](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-f6923194) — «…реза и остаётся тем же в обеих версиях. Это ровно тот класс утечки из D16, который нашли вы, а не тест. **Стоит ли исправлять:** да, и это дёшево. Предлагаю два из»
- [Claude Code 2d7ee671 · 2026-10-11 12:57](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-5a9ec86b) — «…на основном тесте. При h = 6 преимущества нет. - **Проверки утечки на периоде API пройдены.** **Что поймали проверки по ходу** (записано в журнал ошибок ИИ, строки»
- [Claude Code 57049ae5 · 2026-10-11 15:15](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-3bfead3d) — «…е менял, скрипты проверок лежат в scratchpad. **Коротко.** Утечек нет, и теперь это подтверждено проверками, а не только рассуждениями. Две дыры из прошлого ревью»
- [Claude Code 57049ae5 · 2026-10-12 08:45](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-3aa44539) — «…советует поискать в них значение токена. - **S7-2. Проверка утечки не проверяет сам бэктест.** В 'leakage.forecasts_at' своя копия правила отбора обучающих строк, и»
- [Claude Code 57049ae5 · 2026-10-12 09:24](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-a19e8706) — «…ь.** Оба набора независимо воспроизвели прогнозы бит в бит. Утечки, которая меняла бы метрики, не нашёл никто. **Выводы README сильнее, чем показывают данные:** -»
- [Claude Code 0efe39d2 · 2026-10-12 21:05](claude_code/2026-10-12_yellow-red-alerts_0efe39d2.md#m-e256aa90) — «…ailable day; - Two-level alert system (yellow / red); - Leakage control; - Embedding interface; - Documented decisions. - Почему это важно, объясняется в те»

claude.ai and Antigravity — user messages (2 of 2):
- [claude.ai · 2026-10-09 23:20](claude_ai/chat_planning.md) — «…r solution on the latest period. Make sure there is no data leakage: nothing your model is trained on or uses as an input may come from after the time at which the»
- [claude.ai · 2026-10-09 23:23](claude_ai/chat_planning.md) — «Хорошо, плюсы пока откидываем. Что такое бэктест без утечек?»

claude.ai and Antigravity — assistant replies (6 of 24):
- [claude.ai · 2026-10-09 23:21](claude_ai/chat_planning.md) — «…ь спроектировать структуру репозитория и схему бэктеста без утечек.»
- [claude.ai · 2026-10-10 00:00](claude_ai/chat_planning.md) — «…аботы, чтобы он не додумывал структуру данных и не создавал утечек, и уроки из Kizashi. Положи файл в корень репозитория и попроси Claude Code прочитать его перед н»
- [Antigravity · 2026-10-11 20:44](antigravity/main_dialogue.md) — «…w$ отчёт в 'reviews/stage4-6.md' * Агент 5: '05_stage5-leakage.md' $\rightarrow$ отчёт в 'reviews/stage5-leakage.md' * Агент 6: '06_stage7.md' $\rightarro»
- [Antigravity · 2026-10-11 21:16](antigravity/main_dialogue.md) — «… бейзлайны, модели, тюнинг) - ⏳ **Stage 5** (признаки, гео, leakage checks) - ⏳ **Stage 7** (отчёт, README, аудит цифр) Все агенты активно работают. Продолжаю ожид»
- [Antigravity · 2026-10-11 21:23](antigravity/main_dialogue.md) — «Шостий агент (Етап 5 і перевірка на витік даних) щойно успішно завершив роботу та зберіг звіт 'reviews/stage5-leakage.md'. Останній, 4-й аген»
- [Antigravity · 2026-10-11 21:22](antigravity/review_agents/stage5-leakage.md) — «Ревью этапа 5 и защиты от утечки данных успешно завершено, детальный отчёт сохранён в \[reviews/stage5-leakage.md\](file:///D:/Flash»

#### Decision numbers D (first mention of each)

- D0: [claude.ai · 2026-10-10 22:09](claude_ai/chat_planning.md) — «…ьтату. ## Что в файлах **'DECISIONS.md'** — единый журнал D00–D14: - у каждого решения есть находка, решение, причина, альтернативы и статус («зафиксировано» или»
- D1: [claude.ai · 2026-10-10 17:41](claude_ai/chat_planning.md) — «…выдать. ## Кто прав по спорным пунктам Хэш файла совпал с D01 Claude. Ниже результаты моих проверок на этом снимке после дедупликации, в рабочем периоде с 7 нояб»
- D2: [claude.ai · 2026-10-10 17:41](claude_ai/chat_planning.md) — «…ерекрытий нет: это всё были дубликаты. Claude применил свой D02 непоследовательно \| \| Донецкая область \| «Не исключаем, особый режим» — не решение \| «Не разбита на»
- D4: [Claude Code 2d7ee671 · 2026-10-11 01:34](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-e7570f41) — «Структура подтверждает D04/D05. Теперь объём «старых» данных, проходящих через этап 2, и время работы.»
- D5: [Claude Code 2d7ee671 · 2026-10-11 01:34](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-e7570f41) — «Структура подтверждает D04/D05. Теперь объём «старых» данных, проходящих через этап 2, и время работы.»
- D6: [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «…реформы (раздел 3). - Донецкая область удалена полностью, а D06 и этап 5 рассчитывают на неё как на входной признак. Отдельной таблицы «только для признаков» нет.»
- D7: [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «…8–100% эпизодов. Это решение стоит одной строкой записать в D07. ## 2. Двойной подсчёт **В интервалах двойного подсчёта нет.** - В выходной таблице 0 перекрытий»
- D9: [Antigravity · 2026-10-10 23:57](antigravity/main_dialogue.md) — «…ata/mask.csv' создана. 4. **Угрозы и ложные старты ('1б.4 - D09')**: * Ограничение зафиксировано в 'DECISIONS.md'. Посты типа «Загроза БпЛА» 🔴 практически не пр»
- D10: [Antigravity · 2026-10-10 23:57](antigravity/main_dialogue.md) — «…ладываются маски '>24h' и фиктивные '1h' (правила из пункта D10), а также глобальная маска после '2026-09-07'. Таблица 'data/mask.csv' создана. 4. **Угрозы и ложны»
- D12: [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «…* Строки, где 't' попадает в паузу ≤ 15 минут, исчезают (по D12 это 960 строк, 0,15%). Это почти гарантированные положительные строки, исчезновение которых определ»
- D13: [Claude Code 57049ae5 · 2026-10-12 08:51](claude_code/2026-10-11_critical-analysis_57049ae5.md#m-7f936d12) — «…'t+h = data_end') ведут себя согласованно. - **Правый край (D13) оценён количественно.** Агент повторил остановку канала на 49 прошлых днях. Ожидаемый ущерб — 0–10»
- D14: [claude.ai · 2026-10-10 22:09](claude_ai/chat_planning.md) — «…у. ## Что в файлах **'DECISIONS.md'** — единый журнал D00–D14: - у каждого решения есть находка, решение, причина, альтернативы и статус («зафиксировано» или «до»
- D15: [Claude Code 2d7ee671 · 2026-10-11 01:43](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-78814db7) — «…нижены до самого конца данных. **Что сделать (новая запись D15):** - Добавить правило маски (г): «нет ни одного события по стране дольше N часов» маскируется для»
- D16: [Claude Code 2d7ee671 · 2026-10-11 02:17](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-deab166e) — «Добавляю D15 (перерыв в работе канала) и D16 (доступ к истории на момент 't') после D14.»
- D17: [Claude Code 2d7ee671 · 2026-10-11 03:01](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-0e74313d) — «…ботает: сквозной запуск за 14 с, сверка проходит. Записываю D17 в 'DECISIONS.md' и отмечаю этап в 'PLAN.md'.»
- D18: [Claude Code 2d7ee671 · 2026-10-11 03:13](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-2755d4b8) — «Записываю D18 (этап 4) в 'DECISIONS.md'.»
- D19: [Claude Code 2d7ee671 · 2026-10-11 03:23](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-f8d49de3) — «Пока идёт прогон, пишу D19 и обновляю D16 под таблицу 'seen'.»
- D20: [Claude Code 2d7ee671 · 2026-10-11 03:25](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-b46dfd75) — «…овлены. Ждём результатов бэктеста при h = 3, чтобы записать D20 с реальными числами. Как только придут события, продолжу.»
- D21: [Claude Code 2d7ee671 · 2026-10-11 10:53](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-3ca1e74d) — «… что это и чем заменено. В 'DECISIONS.md' добавлены запись D21 и строка 23 в журнале ошибок ИИ. Ошибка такая: мою проверку утечки я объявил закрывающей утечки при»
- D22: [Claude Code 2d7ee671 · 2026-10-11 12:24](claude_code/2026-10-11_stage2-plan-decisions_2d7ee671.md#m-702821f6) — «Записываю D22 с цифрами этапа 8 и ручной проверкой 15 пар названий.»
- D23: [claude.ai · 2026-10-12 18:09](claude_ai/chat_planning.md) — «…НЕ менять, набор признаков НЕ менять (правило 6). В конце — D23 в DECISIONS.md и раздел в README. Известные факты (с источниками, не додумывать сверх них): - Пост»
<!-- /AUTO:candidates -->

</details>
