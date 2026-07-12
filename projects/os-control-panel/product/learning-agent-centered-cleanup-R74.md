# Learning Agent Centered Cleanup — R74

## Why this cleanup is needed

The learning layer has crossed an important threshold.

It now has:
- a persistent learning-agent session
- concept lifecycle state
- concept relationships
- build-to-learn pathways
- background-aware recommendations

But the experience still carries traces of the earlier helper era.

That creates a split model:
- the live learning agent feels like the real future
- older helper and manual-management flows still behave like equal peers

This makes the product feel less coherent than it should.

## Product truth

The OS should now lean heavily toward:
- agent-centered learning

It should lean away from:
- multiple same-weight learning helpers
- heavy manual concept maintenance as the default path
- separate note-capture-style learning flows that bypass the live session

## What no longer feels right as first-class behavior

### 1. Concept helper as a parallel learning path

The concept helper made sense before the live agent existed.

Now it creates duplication:
- concept helper
- persistent learning session

Only one of those should feel primary.

Recommendation:
- retire the concept helper from the main user-facing path
- this is now the right direction for the product, because the live learning agent has become the clear primary concept-learning experience

### 2. Manual concept editing as the main continuation path

The concept manager currently still behaves like a record editor:
- lifecycle status dropdown
- current understanding textarea
- open questions textarea
- note textarea
- multiple lifecycle buttons

This is still useful in edge cases, but it should not feel like the main way learning progresses.

Recommendation:
- make the agent the primary way concept understanding advances
- keep manual editing as a secondary maintenance path
- likely move concept editing behind an `Edit concept` expander or similar lower-emphasis control

### 3. Helper-era routing inside Learn next

The learning layer still contains traces of older helper-first routing logic.

Recommendation:
- Learn next should primarily mean:
  - resume active learning session
  - start a new learning session from a recommendation
- helper-era drafting and clarification flows should stop competing for top-level attention

### 4. Build-to-learn as a separate planning helper rather than a child of the learning agent

Build-to-learn is getting cleaner, but it still partly reflects an older helper model.

Recommendation:
- the learning agent should increasingly own when build-to-learn is suggested
- Builds should remain a real destination, but concept and build moves should feel orchestrated by the agent rather than assembled manually

## Desired operating model

### Learn next

Primary purpose:
- start or resume the live learning agent

### Concepts

Primary purpose:
- browse concept state
- see linked build status
- view relationships and history
- continue learning

Secondary purpose:
- edit concept state manually when needed

### Builds

Primary purpose:
- manage build-to-learn pathways
- capture what building taught
- link back into concepts

### Profile

Primary purpose:
- provide background and trajectory context for the learning agent

## The core product shift

The learning layer should move from:
- helpers + state editors

to:
- a learning agent with supporting libraries

That means:
- the agent teaches
- the agent checks understanding
- the agent suggests builds
- the agent helps update concept state
- the surrounding surfaces support the agent instead of competing with it

## Recommended next cleanup slices

### Slice 1
Retire concept helper from the main user path.

### Slice 2
Simplify concept manager into:
- concept summary
- status
- open questions
- linked build
- relationships
- history
- continue learning

Manual editing should be reduced in prominence.

### Slice 3
Make the agent the default owner of concept progression:
- in progress
- learned
- reopened
- build next

The user should confirm those moves rather than hand-author them most of the time.

## Success signal

The learning layer feels like:
- one coherent agent-centered system

not:
- a strong agent surrounded by older helper-era remnants
