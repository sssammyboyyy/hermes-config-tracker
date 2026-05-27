---
name: memory-management
description: "Lean yet effective memory system for MAS. Rules for what to save, what to compress, and how to keep memory under 2200 chars while retaining maximum value."
version: 1.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, memory, lean, compression, persistence]
---

# Memory Management — Lean Yet Effective

Memory limit: 2,200 chars. Every char must earn its place.

## Compression Rules

### ALWAYS Compress To:
- **Abbreviations**: `build>prompt` (build first, prompt second), `GBP=core`, `GitHub Pages=GH-Pages`
- **Symbols**: `>` instead of "then", `+` instead of "and", `→` instead of "leads to"
- **Remove articles**: "the", "a", "an" — never needed
- **Acronyms**: API, GBP, GCP, JS, CSS, HTML, GH (GitHub)
- **Numbers**: "5 props" not "five properties", "3,024 rv" not "3,024 reviews"

### NEVER Compress:
- **API keys** — always store full key in .env, reference by name only
- **URLs** — always store full URLs (truncate path if needed, never domain)
- **Critical warnings** — "NEVER use regex on base64 srcdoc" not "no regex b64"

## Memory Entry Format

Each entry: `[DATE] [TOPIC]: [COMPRESSED FACTS]`

Example:
`2026-05-27 African Sky: 5 props (Pine Lake 4.2★/603rv, Ermelo 3.6★/811rv, Newcastle 4.0★/786rv, Harrismith 4.1★/532rv, Werlte DE 4.5★/292rv). Total 3,024 rv. Tagline: "WHERE WOULD YOU LIKE TO STAY?" Germany=differentiator. Ermelo=pain point. Brand: #2e3365,#31cdcf,#ff6900. Montserrat+Open Sans.`

## What Goes In Memory (Priority Order)

1. **API keys & credentials** — where stored, never the key itself
2. **Client truth data** — specific facts about current client
3. **Technical pitfalls** — mistakes that cost time
4. **Deployment patterns** — what works, what doesn't
5. **Samuel preferences** — communication style, quality bar
6. **Competitor data** — for current client only

## What NEVER Goes In Memory

- Full code snippets → use skills/ or GitHub repo
- Step-by-step procedures → use skills/
- Large data dumps → use /tmp/ files or GitHub repo
- Generic knowledge → use skills/

## Compounding Pattern

After every major session:
1. Identify 1-3 new lessons learned
2. Compress to <100 chars each
3. Replace oldest/least important memory entry
4. Update skills/ with detailed patterns
5. Push to GitHub repo for backup

## Skill vs Memory Decision

- **Memory**: "What" — facts, data, preferences, warnings
- **Skills**: "How" — procedures, patterns, checklists, templates
- **GitHub**: "Everything else" — code, assets, large data

## NotebookLM Integration (Future)

When MCP is configured:
- Upload client research → query for copy insights
- Upload competitor data → query for positioning
- Upload industry reports → query for trends
- Per-client notebooks for deep context
