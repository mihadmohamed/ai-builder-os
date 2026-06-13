# R74 — Learning Layer Initiative

Status: Drafted for implementation
Requirement: R74
Task: Task 166

## Purpose

Define the holistic learning-layer initiative so AI Builder OS can treat learning as a first-class operating capability rather than a sidecar notebook.

## Initiative outcome

The learning layer should eventually let the operator:
- learn concepts already built into the OS
- learn new concepts introduced during building
- learn concepts not yet present in the OS by building them intentionally
- receive suggestions for what concepts to learn next

## Core capability tracks

### 1. Built-in concept teaching
The OS should be able to explain concepts already present in its workflows, validation stack, and architecture in context.

### 2. New-concept capture during building
When a new concept appears in current work, the OS should help catch it early and turn it into a learning flow rather than letting it pass by as surface familiarity.

### 3. Concept recommendation
The OS should propose likely next concepts to learn based on:
- current trajectory
- current product work
- current gaps
- long-term narrative and credibility goals

### 4. Build-to-learn pathways
For concepts not yet implemented in the OS, the learning layer should support bounded experiments where the concept is learned partly by building it.

## Guiding principles

- Learning should be integrated into using the OS, not bolted on afterward.
- The operator should not need to know what they do not know before the OS can help.
- Concepts should be connected to implementation, validation, workflow, and product judgment.
- The learning layer should remain private-first and local-first in the current slice.

## V3-or-better standard

This initiative should be considered mature only when the OS can:
- teach
- capture
- recommend
- route learning into building and reflection

in a way that feels coherent rather than fragmented.

## Expanded ambition

The learning layer should now be treated as one of the defining OS capabilities, not just a strong helper system.

That means the next phase should include:
- a learning agent that guides understanding actively
- concept lifecycle management over time
- concept relationships and dependencies
- personalized next-learning guidance based on background and trajectory
- a true pull-through from concept exposure -> explanation -> build-to-learn -> learned state -> revisit when needed

## Learning-agent standard

The learning agent should help the operator reach simple, jargon-free understanding rather than superficial term familiarity.

The agent should:
- explain concepts simply
- ask the operator to re-explain them simply
- notice when the explanation still depends on vague jargon or borrowed phrasing
- push understanding forward through clarification, examples, nearby distinctions, or build-to-learn suggestions

This follows a Feynman-style principle:
if the operator cannot explain the concept simply, the system should treat understanding as incomplete.

## Concept-management standard

The concept system should support more than note capture.

It should eventually allow concepts to be:
- upcoming
- in progress
- learned
- reopened
- extended with new doubts
- related to other concepts
- influenced by build-to-learn experiments
