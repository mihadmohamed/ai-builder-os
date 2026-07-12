# Concept Governing Truth — R74

Status: APPROVED FOR RUNTIME TRIAL

Purpose:
- define the governing concept truth for the external V2 learning catalog
- keep concept truth stable while allowing the tutoring agent to personalize teaching around that truth
- separate vendor-grounded concepts from OS-curated operational concepts clearly

Current decision:
- this governing truth is approved as the stable concept spine for runtime validation
- some implementation-anchor descriptions may still be refined after observing real tutoring behavior
- the next review loop should focus on whether the live agent can turn this truth into strong personalized teaching and implementation context

How to use this draft:
- treat these fields as the stable truth layer for each concept
- do not treat the prose here as the final learner-facing explanation
- allow the tutoring agent to personalize:
  - entry point
  - explanation order
  - metaphor
  - example choice
  - OS-context depth
- keep the following stable unless explicitly revised:
  - concept facts
  - concept relationships
  - important distinctions
  - implementation anchors
  - risks and misconceptions

Implementation-anchor rule:
- implementation anchors are source evidence, not the final teaching artifact
- the agent should use anchors to generate a profile-aware implementation walkthrough that explains:
  - how the concept is used in the OS
  - why the OS uses it that way
  - where it sits in the broader workflow or system flow
  - how the relevant pieces relate to one another
- an implementation walkthrough should not degrade into a file list unless the learner explicitly asks for raw file pointers
- in this draft, implementation anchors should be written as descriptive OS surfaces with enough context to show:
  - what the surface does
  - why it matters to the concept
  - how it participates in the broader operating flow

Source policy:
- concept definitions should prefer high-reliability primary sources such as OpenAI, Anthropic, and MCP documentation
- where the concept is not named directly in vendor docs but is still important to how AI Builder OS operates, mark it as an OS-curated operational concept
- OS-curated does not mean invented or illegitimate; it means the concept is a durable operating abstraction synthesized from:
  - official platform concepts
  - common agent-system design patterns
  - the actual implementation and workflow model in this repo

## Family 1 — Agent workflow systems

### Agents

Type:
- Vendor-grounded core concept

Concept facts:
- Agents are applications that plan, call tools, and keep enough state to complete multi-step work.
- An agent is not just a model. It includes model reasoning plus application-owned state, tools, and execution boundaries.

Concept relationships:
- Parent/gateway concept for:
  - Workflows
  - Orchestration
  - Handoffs
  - Results and state
  - Traces / observability
  - Human hand-back

Important distinctions:
- Not the same as a single model call.
- Not the same as one prompt.
- Not the same as a workflow; the workflow is the broader process that the agent participates in.

Implementation anchors:
- bounded agent runtime that turns live PM, Experience, UI, Learning, and Orchestrator roles into governed operating units rather than loose model calls
- shared Agents workspace surface that exposes those roles as distinct work lanes inside the OS
- trace and run persistence that makes agent behavior inspectable after execution instead of leaving it as invisible model activity

Risks / misconceptions:
- Treating the model itself as the whole agent.
- Anthropomorphizing the agent and ignoring application logic.
- Assuming tool access alone is enough to make something an effective agent.

### Workflows

Type:
- OS-curated operational concept grounded in official agent patterns

Concept facts:
- Workflows are structured sequences of steps, transitions, and decisions that move work toward an outcome.
- In agent systems, workflows often include both automated and human-governed steps.

Concept relationships:
- Child of `Agents` as part of the broader agentic operating model.
- Parent concept for:
  - Orchestration
  - Handoffs
  - Results and state
  - Traces / observability
  - Human hand-back

Important distinctions:
- Workflow is the process shape; orchestration is the decision logic inside that process.
- Workflow is not the same as one agent turn.

Implementation anchors:
- task and requirement registries that hold the durable shape of work as it moves through statuses, priorities, and handoffs
- scenario-based workflow validation that makes expected multi-step behavior concrete instead of leaving workflows implicit
- routing and approval state in the OS that determines how work advances, pauses, or returns to a human

Risks / misconceptions:
- Assuming workflow means rigid automation only.
- Treating hidden prompt behavior as if it were sufficient workflow design.
- Ignoring human checkpoints as part of real workflows.

### Orchestration

Type:
- OS-curated operational concept grounded in official agent patterns

Concept facts:
- Orchestration is the logic that decides what should happen next, which role or tool should act, and how state should move across steps.
- Good orchestration turns a capable model into a coherent multi-step system.

Concept relationships:
- Child of `Workflows`
- Adjacent to:
  - Handoffs
  - Results and state
  - Traces / observability
  - Workflow Evals

Important distinctions:
- Orchestration is coordination logic, not the same as tool execution.
- Orchestration is not identical to scheduling or sequencing; it can include policy and routing judgment.

Implementation anchors:
- orchestrator next-step logic that decides what role or workflow move should happen next
- workflow gates and routing rules that stop the system from advancing blindly when structure or approval is missing
- scenario-based evaluations that check whether the OS made the right routing and sequencing decisions

Risks / misconceptions:
- Treating orchestration as just “what happens next” without explicit criteria.
- Hiding too much orchestration policy inside prompts instead of inspectable logic.

### Handoffs

Type:
- OS-curated operational concept grounded in official agent patterns

Concept facts:
- Handoffs are explicit transfers of responsibility or context from one role, step, or workflow stage to another.
- Handoffs matter because context can be lost, mis-scoped, or misinterpreted at boundaries.

Concept relationships:
- Child of `Workflows`
- Closely linked to:
  - Orchestration
  - Results and state
  - Human hand-back

Important distinctions:
- A handoff is not just the next message in a thread.
- A handoff is a boundary event with scope and ownership implications.

Implementation anchors:
- routed findings and approval records that show work moving from one responsible role or decision point to another
- PM clarification and approval flows that make ownership transfer explicit instead of conversationally fuzzy
- persisted workflow artifacts that preserve what was handed off, why, and to whom

Risks / misconceptions:
- Assuming context transfers automatically and losslessly.
- Treating handoffs as purely conversational instead of workflow-state transitions.

### Results and state

Type:
- OS-curated operational concept

Concept facts:
- Results are durable outcome snapshots.
- State is the durable current condition that determines what the system should do next.
- Agent systems need inspectable state or they become hard to reason about and recover.

Concept relationships:
- Child of `Workflows`
- Supports:
  - Handoffs
  - Orchestration
  - Learning concept progression

Important distinctions:
- Result is not the same as state.
- UI display state is not the same as canonical durable product truth.

Implementation anchors:
- canonical requirement and task registries that store the durable state of planned and active work
- per-user learning profile and session files that preserve learning progress across time
- runtime stores that separate durable user state from transient UI state so the OS can recover and resume coherently

Risks / misconceptions:
- Confusing in-memory UI state with durable workflow truth.
- Assuming a finished model answer is enough without durable state updates.

### Traces / observability

Type:
- Vendor-grounded plus OS-curated operational framing

Concept facts:
- Traces are end-to-end records of agent decisions, tool calls, and workflow steps.
- Observability is the broader ability to inspect what happened and why.

Concept relationships:
- Child of `Workflows`
- Supports:
  - Workflow Evals
  - Trace grading
  - Reliability Evals

Important distinctions:
- Traces describe behavior.
- Evals judge whether that behavior was acceptable.

Implementation anchors:
- trace persistence in the runtime that records what the agent did, what tools it used, and how the run ended
- operations dashboards that turn raw traces into readable operating evidence for the Product Director
- trace inspection and summary logic that condenses long execution history into meaningful review surfaces

Risks / misconceptions:
- Treating raw trace volume as understanding.
- Assuming observability alone makes a system trustworthy.

### Human hand-back

Type:
- OS-curated operational concept grounded in bounded-agent best practice

Concept facts:
- Human hand-back means the system deliberately pauses and returns control when ambiguity, risk, or missing context makes autonomous continuation unsafe.
- This is a quality feature, not just an error condition.

Concept relationships:
- Child of `Workflows`
- Adjacent to:
  - Safety Evals
  - Orchestration
  - Results and state

Important distinctions:
- Hand-back is not the same as failure.
- Hand-back is not the same as generic “ask a question”; it is a bounded decision to stop and return responsibility.

Implementation anchors:
- `hand_back_reason` in learning session state
- approval and blocked-state flows
- bounded runtime guardrails

Risks / misconceptions:
- Believing a good agent should never hand back.
- Letting the agent bluff through uncertainty instead of escalating.

## Family 2 — Evals and reliability

### Evals

Type:
- Vendor-grounded core concept

Concept facts:
- Evals are repeatable checks for whether an AI-assisted system behaves acceptably across known cases.
- Evals provide evidence stronger than anecdotal success or one good demo.

Concept relationships:
- Gateway concept for:
  - Agent-output quality evals
  - Tool Selection Evals
  - Workflow Evals
  - Memory Evals
  - Safety Evals
  - Cost Evals
  - Latency Evals
  - Reliability Evals
- `Replays` is a supporting technique for evals rather than a full peer category.

Important distinctions:
- Broader than unit tests.
- Broader than grading final outputs only.

Implementation anchors:
- deterministic eval framework for multi-dimensional agent evaluation, used in the OS to judge output quality, tool choice, workflow behavior, memory behavior, safety, cost, latency, and reliability
- project-local eval runners that execute the OS validation contract and make evaluation a routine operating step rather than a special activity
- scenario-based eval runner that turns workflow and agent expectations into named cases the OS must handle correctly

Risks / misconceptions:
- Thinking evals prove total correctness.
- Mistaking a nice-looking interaction for sufficient evidence.

### Agent-output quality evals

Type:
- OS-curated operational concept grounded in common eval practice

Concept facts:
- These evals judge the quality of the final output the agent produces.
- They focus on qualities like correctness, usefulness, completeness, or clarity.

Concept relationships:
- Child of `Evals`
- Sibling to:
  - Workflow Evals
  - Tool Selection Evals
  - Memory Evals

Important distinctions:
- Final-answer quality is only one part of a broader eval strategy.
- A good output does not prove the underlying workflow or tool choices were sound.

Implementation anchors:
- scenario expectations over generated outputs, used in the OS to check whether the final answers from PM, Experience, UI, and Learning surfaces are actually useful and grounded
- quality-oriented eval examples in the framework that distinguish “the system answered” from “the system answered well enough to trust”

Risks / misconceptions:
- Treating output quality as the whole system quality story.
- Ignoring how the result was produced.

### Tool Selection Evals

Type:
- OS-curated operational concept grounded in tool-using agent evaluation

Concept facts:
- Tool Selection Evals judge whether the system chose the right tool, avoided unnecessary tools, and used tools in a sensible order.

Concept relationships:
- Child of `Evals`
- Closely related to `Tool selection` as a capability concept

Important distinctions:
- This evaluates a decision about tools.
- It is not the same as evaluating the final answer or the whole workflow.

Implementation anchors:
- tool-selection coverage in the eval framework, used in the OS to judge whether agents chose the right tools, avoided unnecessary tools, and used them in a sensible order

Risks / misconceptions:
- Checking only whether a tool was used at all.
- Ignoring unnecessary or poorly ordered tool use.

### Workflow Evals

Type:
- OS-curated operational concept grounded in agent eval practice

Concept facts:
- Workflow Evals judge whether the system followed an acceptable sequence of steps, transitions, and route decisions.

Concept relationships:
- Child of `Evals`
- Parent of `Trace grading` in the current learning model

Important distinctions:
- Workflow quality is about process behavior, not just final output quality.

Implementation anchors:
- workflow scenarios that define expected routing, sequencing, cleanup, and terminal outcomes across the OS
- scenario-runner handling that executes those workflow cases and shows whether the system followed an acceptable path, not just whether it produced an answer

Risks / misconceptions:
- Treating “it completed” as sufficient workflow quality.

### Trace grading

Type:
- Vendor-grounded core concept

Concept facts:
- Trace grading assigns structured scores or labels to an agent trace to assess correctness, quality, or adherence to expectations.

Concept relationships:
- Specialized child of `Workflow Evals`
- Depends on `Traces / observability`

Important distinctions:
- It judges the path taken, not just the final answer.

Implementation anchors:
- trace-quality tests and grader logic that judge whether the workflow path itself was acceptable, complete, and well-routed
- trace and operations surfaces that let the Product Director inspect why a run was considered clean, risky, or incomplete

Risks / misconceptions:
- Believing trace grading is unnecessary when outputs look correct.

### Memory Evals

Type:
- OS-curated operational concept grounded in memory evaluation practice

Concept facts:
- Memory Evals judge whether the system remembered, retrieved, ignored, or rejected state appropriately over time.

Concept relationships:
- Child of `Evals`
- Adjacent to `Memory systems`

Important distinctions:
- Evaluates memory behavior, not the memory architecture itself.

Implementation anchors:
- memory checks in the eval framework that test whether the OS remembered, reused, or rejected state appropriately
- persistent concept-state and learning-session surfaces that make memory behavior observable instead of hypothetical

Risks / misconceptions:
- Assuming persistence alone means memory is working correctly.

### Safety Evals

Type:
- OS-curated operational concept grounded in safety evaluation practice

Concept facts:
- Safety Evals judge whether the system stays inside authorization, policy, approval, and bounded-execution constraints.

Concept relationships:
- Child of `Evals`
- Adjacent to `Human hand-back`

Important distinctions:
- Safety is a separate quality dimension from usefulness or correctness.

Implementation anchors:
- bounded runtime guardrails that prevent live agents from operating outside approved limits
- output guardrails that block ungrounded or unsafe claims before they are accepted
- approval-gated actions that keep higher-risk capabilities under human control

Risks / misconceptions:
- Treating safety as only a prompting concern.
- Assuming harmless-looking output means the run was safe.

### Cost Evals

Type:
- OS-curated operational concept grounded in runtime measurement

Concept facts:
- Cost Evals judge whether runs stay inside acceptable token or monetary budgets.

Concept relationships:
- Child of `Evals`
- Sibling to `Latency Evals` and `Reliability Evals`

Important distinctions:
- Cost is an operational quality dimension, not a semantic correctness dimension.

Implementation anchors:
- token and estimated cost tracking in the runtime, used in the OS to make agent cost visible and enforceable rather than hidden inside provider billing

Risks / misconceptions:
- Optimizing cost without regard for accuracy or reliability.

### Latency Evals

Type:
- OS-curated operational concept grounded in runtime measurement

Concept facts:
- Latency Evals judge whether the system responds within acceptable time bounds.

Concept relationships:
- Child of `Evals`
- Sibling to `Cost Evals` and `Reliability Evals`

Important distinctions:
- Fast is not the same as correct or useful.

Implementation anchors:
- duration measurement in runtime and eval infrastructure, used in the OS to judge whether agent behavior is fast enough for the intended operating loop

Risks / misconceptions:
- Treating low latency as proof of quality.
- Ignoring the latency costs of multi-step tool loops.

### Reliability Evals

Type:
- OS-curated operational concept grounded in repeated-run quality

Concept facts:
- Reliability Evals judge consistency across repeated runs, completion integrity, and regression stability.

Concept relationships:
- Child of `Evals`
- Closely linked to `Traces / observability`

Important distinctions:
- Reliability is not the same as one successful run.

Implementation anchors:
- repeated-run checks and reliability framing in the eval framework, used in the OS to distinguish one lucky pass from durable repeatable behavior

Risks / misconceptions:
- Assuming anecdotal stability is enough.

### Replays

Type:
- OS-curated operational concept

Concept facts:
- Replays run historical or captured interactions through the system again to test behavior against known cases.

Concept relationships:
- Supporting technique for `Evals`
- Especially useful for:
  - Agent-output quality evals
  - Workflow validation

Important distinctions:
- Replay is a method or technique, not a complete eval family of its own.
- Replay should not be treated as a peer eval subtype alongside output quality, workflow, memory, safety, cost, latency, or reliability.

Implementation anchors:
- ParentMate replay-backed eval runner
- replay fixtures and examples

Risks / misconceptions:
- Thinking replay coverage equals full production realism.

## Family 3 — Context and knowledge systems

### Memory systems

Type:
- OS-curated operational concept grounded in official memory/retrieval patterns

Concept facts:
- Memory systems decide what should persist across time and how that state can be retrieved or reused later.

Concept relationships:
- Gateway concept for:
  - Retrieval
  - File search
  - RAG
- Adjacent to `Memory Evals`

Important distinctions:
- Memory persistence is broader than a one-time retrieval step.

Implementation anchors:
- concept state store
- session/profile persistence
- runtime user state files

Risks / misconceptions:
- Treating all stored context as useful memory.
- Persisting too much without structure or retrieval discipline.

### Retrieval

Type:
- Vendor-grounded core concept

Concept facts:
- Retrieval fetches relevant context from a larger knowledge base at the moment it is needed.
- In OpenAI’s Retrieval API framing, retrieval is powered by vector stores and search over indexed data.

Concept relationships:
- Child of `Memory systems`
- Parent/supporting concept for:
  - File search
  - RAG

Important distinctions:
- Retrieval gets relevant context now.
- Memory decides what should persist over time.

Implementation anchors:
- retrieval concept grounding
- future or adjacent lookup patterns around file and knowledge access

Risks / misconceptions:
- Assuming retrieval quality is automatic once data exists.

### File search

Type:
- Vendor-grounded core concept

Concept facts:
- File search is a tool pattern that searches uploaded files or knowledge stores for relevant information before answer generation.

Concept relationships:
- Child of `Retrieval`

Important distinctions:
- File search is one concrete retrieval mechanism.
- It is not the same as the whole memory strategy.

Implementation anchors:
- file-search concept grounding
- retrieval/tool family linkage

Risks / misconceptions:
- Confusing file search with generic memory.
- Treating file search as equivalent to manual browsing.

### RAG

Type:
- Vendor-grounded widely used concept

Concept facts:
- Retrieval-augmented generation retrieves relevant external context first, then uses that context to ground the model’s response.

Concept relationships:
- Child of `Retrieval`
- Adjacent to `Memory systems`

Important distinctions:
- RAG is not the same as long-term memory.
- Retrieval can support RAG, but not all retrieval patterns are full RAG systems.

Implementation anchors:
- RAG concept grounding in the learning layer
- hierarchy placement under retrieval

Risks / misconceptions:
- Using RAG by default whenever a concept feels knowledge-heavy.

## Family 4 — Tool and capability access

### Tool use

Type:
- Vendor-grounded core concept

Concept facts:
- Tool use lets a model call tools to access data, perform actions, or reach capabilities outside its built-in knowledge.

Concept relationships:
- Gateway concept for:
  - Function calling
  - Connectors
  - MCP
  - Tool selection

Important distinctions:
- Tool use is the broad capability pattern.
- Function calling is one structured mechanism inside that broader pattern.

Implementation anchors:
- tool surfaces and definitions
- runtime allowlists
- connector/plugin infrastructure

Risks / misconceptions:
- Assuming tools make the model right by default.

### Function calling

Type:
- Vendor-grounded core concept

Concept facts:
- Function calling is a structured tool-calling mechanism where the model emits schema-constrained calls that the application executes.

Concept relationships:
- Child of `Tool use`
- Sibling to `MCP` and `Connectors`

Important distinctions:
- Function calling is not the same as unrestricted agent autonomy.
- Schema correctness does not guarantee that the chosen function was semantically appropriate.

Implementation anchors:
- structured callable tool interfaces
- schema-defined tool contracts

Risks / misconceptions:
- Treating valid schema output as proof of good judgment.

### MCP

Type:
- Vendor-grounded core concept

Concept facts:
- Model Context Protocol is a standard for connecting AI applications to external systems, including tools, data sources, and workflows.

Concept relationships:
- Child of `Connectors` in the current learning hierarchy
- Adjacent to `Function calling`

Important distinctions:
- MCP is a protocol layer, not a single tool.
- MCP is not the same as memory or retrieval.
- MCP should not be taught as a peer of `Connectors`; it is a narrower standard that can structure or power connector-style access.

Implementation anchors:
- MCP tooling and documentation surfaces
- capability-access framing in the OS

Risks / misconceptions:
- Treating MCP as a synonym for all tool use.

### Connectors

Type:
- Vendor-grounded with OS-curated operational framing

Concept facts:
- Connectors are packaged integrations that expose external services to the model, often through MCP-backed or MCP-adjacent interfaces.

Concept relationships:
- Child of `Tool use`
- Parent/supporting concept for `MCP`

Important distinctions:
- Connector is the integration surface.
- MCP is the standard/protocol that may power or structure the connection.
- `Connectors` should be taught before `MCP`, because it is the broader product/integration concept and the more natural learner entry point.

Implementation anchors:
- connector/plugin infrastructure
- hosted wrapper and capability surfaces

Risks / misconceptions:
- Assuming every connector is equally safe, reliable, or high-quality.

### Tool selection

Type:
- OS-curated operational concept grounded in tool-using agent design

Concept facts:
- Tool selection is the runtime decision about which available tool, if any, should be used for the current task.

Concept relationships:
- Child of `Tool use`
- Closely related to `Tool Selection Evals`

Important distinctions:
- Tool selection is the capability behavior.
- Tool Selection Evals judge whether that behavior was good.

Implementation anchors:
- runtime tool choice logic
- deferred tool definitions and search
- evaluation coverage for tool-choice quality

Risks / misconceptions:
- Thinking more tools automatically means better outcomes.

## Resolved curation decisions

1. `Replays` is a supporting evaluation technique, not a peer eval subtype.
2. `Tool use` is the gateway concept for the tool/capability family.
3. `Function calling` is a specialized child under `Tool use`, not a parallel gateway.
4. `Connectors` remains the broader concept and `MCP` remains a specialized child under it, rather than treating them as siblings.

## Personalization rule after approval

Once this draft is approved, personalization should happen around this truth layer by adapting:
- learner entry point
- metaphor
- explanation order
- example choice
- OS-context depth

Personalization should not silently mutate:
- concept facts
- hierarchy truth
- important distinctions
- implementation anchors
- core risks and misconceptions
