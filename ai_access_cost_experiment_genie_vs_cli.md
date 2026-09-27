# AI Access Cost Experiment: Genie vs. AI-Assisted CLI

## Purpose

Evaluate the most cost-effective and governable way to let AI work with enterprise data and tools.

This experiment is intentionally **headless by default**. The human interface should be natural language, while execution happens through programmatic interfaces such as CLI, SQL, APIs, or MCP.

The central question is:

> **If AI can already translate natural language into CLI and SQL, when does an additional AI-native abstraction such as Genie or MCP justify its additional cost and complexity?**

The demo uses a synthetic **Virtual Pet Adoption Center** dataset to keep the scenario memorable, safe, and easy to reason about.

---

## Working Thesis

AI changes the traditional CLI-vs-MCP tradeoff.

Historically, CLI had a significant usability barrier: users needed to know commands, syntax, flags, query languages, and platform-specific details.

With a capable AI assistant, the interaction can instead be:

```text
Human intent
  ↓
AI assistant
  ↓
Generated CLI / SQL / API operation
  ↓
Enterprise platform
```

The user does not need to memorize the command syntax.

That means:

- CLI remains a strong deterministic execution layer.
- Genie must justify itself through semantic context, self-service analytics, reduced interaction cycles, or stronger business understanding.
- MCP must justify itself through standardized discovery, governed tool access, reusable context, portability, and multi-tool reasoning.
- Playwright is not the primary integration path. It is used only when visual confirmation is valuable.

---

# Experiment Design

## Design Principles

1. **Headless by default**
   - No dependence on manual browser interaction.
   - No copy/paste SQL as part of the normal workflow.
   - No human required to know CLI syntax.
   - Authentication should support unattended execution where feasible.

2. **Same question, different access path**
   - Keep the underlying data and business questions consistent.
   - Compare the access patterns rather than changing the workload.

3. **Measure, do not speculate**
   - Capture actual platform usage where available.
   - Measure interaction count, latency, correctness, and human effort.
   - Separate observed results from assumptions.

4. **Read-only first**
   - Initial comparisons should focus on read/query operations.
   - Write actions should be introduced only after permission boundaries are explicit.

5. **Playwright only when we need eyes**
   - Browser automation is for visual validation, debugging, screenshots, and evidence.
   - API/CLI/MCP remain the preferred machine interfaces.

---

# Scope

## Required Components

### Databricks
Primary analytical platform.

Use it for:
- storing the synthetic adoption dataset
- SQL analytics
- Genie experiments
- system usage/billing inspection
- CLI/API execution
- later MCP comparison if useful

### AI Assistant
Use a capable reasoning model to translate natural-language intent into:
- SQL
- Databricks CLI commands
- API calls
- evaluation and interpretation

### Virtual Pet Adoption Center Dataset
Synthetic, humorous data designed to support operational, analytical, and ambiguous business questions.

---

## Optional Components

### Salesforce
Salesforce can be added later as an operational system if it strengthens the story.

Potential role:
- pet records
- adopter records
- applications
- workflow/status tracking

It is **not required** for the core Genie-vs-CLI cost experiment.

### MCP
MCP is an experimental comparison path, not the assumed winner.

Use it when testing:
- tool discovery
- reusable context
- governed access
- cross-system reasoning
- portability across AI clients

### Playwright
Use only when visual validation matters.

Example:

> "We have been headless the entire time. Now show me what Tax Fraud actually looks like in the app."

Use Playwright to:
- open the UI
- confirm the rendered experience
- capture evidence
- exit

---

# Synthetic Dataset

## Pets

| Pet | Species | Breed | Age | Status | Energy | Chaos | Behavior Risk | Good With Kids | Bio |
|---|---|---|---:|---|---|---:|---:|---|---|
| Sir Barksalot III | Dog | Corgi | 4 | Available | Extreme | 8 | 42 | Yes | Steals socks and hides them in air vents |
| Chairman Meow | Cat | Domestic Shorthair | 7 | Available | Low | 4 | 18 | Maybe | Will only drink water from a human glass |
| Dumpster Fire | Cat | Orange Tabby | 2 | Available | Extreme | 10 | 78 | No | Has opened three child-proof cabinets |
| Kevin | Goat | Nigerian Dwarf | 3 | Available | High | 10 | 55 | Yes | Escaped a petting zoo twice |
| Lasagna | Dog | Basset Hound | 6 | Pending | Low | 2 | 10 | Yes | Refuses to walk uphill |
| Tax Fraud | Parrot | African Grey | 18 | Available | High | 9 | 61 | Maybe | Repeats confidential-sounding phrases |
| Princess Murdermittens | Cat | Maine Coon | 5 | Available | Medium | 7 | 69 | No | Majestic and highly experienced in boundary enforcement |
| Gary | Dog | Chihuahua Mix | 9 | Available | Extreme | 9 | 64 | No | Has personal grievances |
| Potato Supreme | Rabbit | Flemish Giant | 4 | Available | Low | 3 | 12 | Yes | Considerably larger than expected |
| Beef Wellington | Dog | English Bulldog | 5 | Adopted | Low | 2 | 8 | Yes | Snores loudly enough to interrupt meetings |
| Reverend Bitey | Cat | Siamese | 8 | Available | Medium | 8 | 73 | No | Believes ankles require supervision |
| Crouton | Dog | Great Dane | 2 | Available | High | 7 | 28 | Yes | Thinks he is a lap dog |
| Wi-Fi Password | Ferret | Ferret | 3 | Available | Extreme | 10 | 47 | Maybe | Disappears into furniture and returns with objects |
| Linda from Accounting | Cat | Tortoiseshell | 11 | Available | Low | 6 | 31 | Maybe | Judges spending decisions silently |
| Meatball | Pig | Mini Pig | 4 | Available | Medium | 8 | 36 | Yes | Has learned how to open the refrigerator |

---

## Suggested Adoption Application Pattern

Seed applications unevenly so the dataset has both a visible trend and useful outliers.

Examples:

- Lasagna: 14 applications
- Kevin: 11 applications despite Chaos Level 10
- Dumpster Fire: 1 application
- Gary: 2 applications
- Tax Fraud: moderate interest despite high chaos/risk
- Beef Wellington: already adopted

This supports analysis such as:

- Does chaos correlate with fewer applications?
- Which animals are outliers?
- Which factors matter more than chaos?
- Does age, behavior risk, energy, or species explain adoption delay?

---

# Experiment Paths

## Path A: AI-Assisted CLI / SQL

Interaction pattern:

```text
User
  ↓
AI assistant
  ↓
SQL / Databricks CLI / API
  ↓
Databricks
  ↓
Structured result
  ↓
AI interpretation
```

### Example Prompt

> Show me all available pets with chaos level above 8 and fewer than three applications.

The user should not need to know:
- SQL syntax
- Databricks CLI syntax
- warehouse identifiers
- API syntax

The AI translates intent into execution.

---

## Path B: Genie

Interaction pattern:

```text
User
  ↓
Genie
  ↓
Semantic / analytical reasoning
  ↓
Databricks compute
  ↓
Answer
```

Use the **same questions** as the CLI path.

Capture:
- number of turns
- quality of generated answer
- compute consumed
- Genie-specific usage
- latency
- whether Genie surfaced useful business context not present in a direct SQL answer

---

## Path C: MCP

Only add MCP after the direct paths are understood.

Use MCP to test whether it provides value through:

- standardized tool discovery
- governed tool exposure
- reusable resources/context
- client portability
- permission-aware access
- cross-tool reasoning

Do not treat MCP as a replacement for:
- source-system APIs
- CLI
- identity
- permissions
- data governance
- audit controls

---

# Test Questions

Run each question through the relevant access paths.

## 1. Deterministic

> How many available pets have a chaos level above 8?

Expected characteristics:
- simple filter
- easy to verify
- likely ideal for SQL/CLI

---

## 2. Slightly More Complex

> Show me available pets with chaos level above 8 and fewer than three adoption applications.

Expected characteristics:
- join or aggregation
- still deterministic
- clear validation path

---

## 3. Analytical

> Does chaos level appear associated with fewer applications or longer time to adoption?

Expected characteristics:
- aggregation
- trend analysis
- interpretation
- opportunity for Genie to add semantic value

---

## 4. Outlier Analysis

> Kevin has a chaos level of 10 but gets lots of applications. Why might Kevin be an outlier?

Expected characteristics:
- requires comparison across multiple features
- should distinguish correlation from explanation
- good test of reasoning quality

---

## 5. Ambiguous Business Question

> Which pets need intervention right now, and why?

Expected characteristics:
- requires definition of "intervention"
- likely needs business assumptions or context
- useful test of semantic reasoning and clarification behavior

---

# Measurement Framework

For each question and access path, capture the following.

| Dimension | Measure |
|---|---|
| Platform cost | Compute / DBUs / query cost where available |
| AI-layer cost | Genie-specific usage or equivalent |
| Time to answer | Start-to-finish elapsed time |
| Interaction count | Number of prompts/turns required |
| Correctness | Did the answer match the source data? |
| Reproducibility | Can the same result be recreated reliably? |
| Explainability | Can the path to the answer be understood? |
| Business context | Did the system correctly interpret domain meaning? |
| Technical skill required | What expertise did the human actually need? |
| Governance | Identity, permissions, logging, write boundaries |
| Automation fit | How easily can this run unattended? |

---

# Cost Questions to Answer

## Genie

Measure:
- Genie usage
- underlying SQL/compute
- number of interactions
- query complexity
- equivalent cost if free/promotional pricing applies

Key question:

> Does Genie reduce enough human effort or improve the quality of the answer enough to justify the additional AI layer?

---

## AI-Assisted CLI / SQL

Measure:
- SQL warehouse compute
- job/API cost
- number of generated operations
- number of retries
- time to correct answer

Key question:

> If a general AI assistant already translates intent into SQL and CLI, how much additional value does a platform-specific AI interface provide?

---

# Governance Experiment

For each access path, document:

1. Whose identity is executing?
2. What data can it read?
3. What actions can it perform?
4. Are writes disabled, allowed, or approval-gated?
5. What is logged?
6. Can activity be attributed to a user/service principal?
7. How are credentials stored and rotated?
8. What prevents prompt-driven privilege expansion?
9. Can the interface expose only approved capabilities?
10. Can the same policy be reused across clients?

---

# Headless Requirement

The final demo should not require normal UI interaction.

Preferred runtime model:

```text
Natural-language request
        ↓
AI reasoning
        ↓
Programmatic access
        ↓
Salesforce / Databricks / MCP
        ↓
Result
```

Use service identities and non-interactive authentication where appropriate.

Browser/UI use is acceptable only for:
- initial administrative bootstrap
- visual verification
- screenshots
- debugging
- demonstration evidence

The architecture should **not depend on Playwright** for normal data access.

---

# Playwright Cameo

Playwright is the "eyes on demand" tool.

Possible demo moment:

> "Everything so far has been headless. But I do not entirely trust Tax Fraud. Let's actually look."

Then:

1. launch the application
2. navigate to the pet list
3. visually confirm records
4. capture a screenshot/trace
5. close the browser
6. return to headless execution

Evaluation question:

> Did visual validation reveal anything our API/data-level checks did not?

---

# Optional Salesforce Extension

If Salesforce is included, give it equal narrative weight with Databricks.

## Salesforce Role

Operational system:
- Pet
- Adopter
- Adoption Application
- status/workflow
- notes
- behavior risk
- match score

## Databricks Role

Analytical system:
- historical trends
- application volume
- adoption time
- outlier detection
- cost analysis
- Genie comparison

Potential flow:

```text
Salesforce operational data
        ↓
Ingestion / replication
        ↓
Databricks
        ↓
Genie vs CLI vs MCP experiment
```

Do not add Salesforce if the integration plumbing distracts from the core experiment.

---

# Decision Framework

## Prefer AI-Assisted CLI / API When

- the action is known
- the workflow is repeatable
- deterministic behavior matters
- results are easy to validate
- scripting is desirable
- headless automation is important
- cost transparency is important

---

## Prefer Genie When

- semantic context reduces user effort
- business users need self-service analytics
- complex questions require fewer interaction cycles
- platform-native context materially improves the answer
- explanations are meaningfully better than direct query results

---

## Prefer MCP When

- the AI must discover available capabilities
- multiple clients need the same governed interface
- business context/resources should be exposed consistently
- cross-tool reasoning is required
- tool contracts and permission boundaries need standardization

---

# Expected Talk Narrative

## Opening

> I thought I wanted to give a talk about MCP. Then I started using CLI more often.

> The reason was surprising: I no longer needed to know the commands. I could describe what I wanted to an AI assistant, and it could translate my intent into SQL or CLI operations.

> That changed the question for me.

> If natural language is available either way, what exactly are we paying the additional AI abstraction for?

---

## Experiment Story

1. Create a deliberately ridiculous synthetic pet-adoption dataset.
2. Ask the same business questions through multiple access paths.
3. Measure cost, effort, quality, and governance.
4. Use Playwright only when visual evidence is useful.
5. Let Genie, CLI, and MCP earn their place based on evidence.

---

## Key Insight

> **Natural language alone is no longer enough to justify an AI-native interface.**

The value must come from something beyond syntax translation:

- business semantics
- contextual grounding
- governance
- discovery
- reuse
- reduced interaction cycles
- portability
- better decision quality

---

# Success Criteria

The experiment is successful if it produces:

- a repeatable headless CLI/SQL path
- a comparable Genie path
- measured usage/cost data
- an evidence-based comparison
- clear governance observations
- at least one case where the cheaper/simple path wins
- at least one case where a richer AI abstraction demonstrates real incremental value
- a defensible explanation of where MCP does and does not belong

The goal is **not** to prove that CLI, Genie, or MCP is best.

The goal is to understand:

> **Which access pattern earns its complexity and cost for which kind of work?**

---

# Working Demo Punchline

> If Tax Fraud the parrot can expose hidden assumptions in our AI architecture, the experiment is doing its job.
