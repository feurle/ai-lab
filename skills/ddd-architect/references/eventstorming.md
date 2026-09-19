# EventStorming Reference

## Colour Legend (Big Picture → Design Level)

| Colour | Element | Description |
|--------|---------|-------------|
| 🟠 Orange | **Domain Event** | Something that happened; past tense. The backbone of EventStorming. |
| 🔵 Blue | **Command** | What triggered the event (user action or system action). |
| 🟡 Yellow | **Actor** | The person or system that issued the command. |
| 🟣 Purple | **Policy / Reaction** | "Whenever [event] then [command]" — automation rules. |
| 🔴 Red | **Hot Spot / Problem** | Conflict, uncertainty, or a question to resolve with the domain expert. |
| 🟢 Green | **Read Model / Query** | Information the actor needs to make a decision before issuing a command. |
| 💗 Pink | **External System** | A system outside the domain boundary. |
| 🟨 Light Yellow | **Aggregate** | Groups commands and events that share the same consistency boundary. |

---

## Facilitation Flow

### Phase 1 — Chaotic Exploration (Big Picture)
1. Place all **Domain Events** on the timeline (left = past, right = future).
2. No filtering — capture everything, duplicates are OK.
3. Focus on "what happens", not "how it works".

### Phase 2 — Enforce the Timeline
1. Order events chronologically.
2. Identify **pivotal events** — points where the process fundamentally changes direction.
3. Mark **Hot Spots** where there is disagreement or uncertainty.

### Phase 3 — Add Commands & Actors
1. For each event, ask: *"What triggered this?"* → add a Command.
2. For each command, ask: *"Who/what issued it?"* → add an Actor or External System.

### Phase 4 — Add Policies
1. Between events and commands, look for automation: *"Whenever X happens, we always do Y."*
2. These become **Policies** (purple stickies).

### Phase 5 — Aggregate Clustering
1. Group commands and events that share a consistency boundary.
2. Name the cluster — this is your **Aggregate** candidate.
3. Groups of aggregates with the same language form **Bounded Context** candidates.

### Phase 6 — Design Level (optional, per context)
Go deeper on a specific context:
- Add **Read Models** (what does the actor need to see before acting?)
- Refine **Aggregate** internals
- Identify **Domain Services** for operations crossing aggregates

---

## EventStorming → DDD Artifacts Mapping

| EventStorming Output | DDD Artifact |
|---------------------|--------------|
| Aggregate cluster | Aggregate Root candidate |
| Pivotal event boundary | Bounded Context boundary |
| Policy (automated) | Domain Service or Saga/Process Manager |
| External System | Context integration point (ACL, OHS) |
| Hot Spot (language conflict) | Separate Bounded Context needed |
| Hot Spot (process conflict) | Invariant or business rule to clarify |

---

## Prompts for Domain Expert Interviews

Use these questions to draw out events and rules:

- "Walk me through what happens when a customer places an order — start to finish."
- "What are the most important things that can go wrong?"
- "When [event] happens, does anything else automatically happen?"
- "Is there a point in the process where someone in a different department takes over?"
- "What information do you look at before making that decision?"
- "Are there any words your team uses that mean different things to different people?"
