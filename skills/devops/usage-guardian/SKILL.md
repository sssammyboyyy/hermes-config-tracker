---
name: usage-guardian
description: "Track and enforce API call limits — 200 calls/day, 10 calls/minute. Halts pipeline if limits approached."
version: 1.0.0
author: MAS Orchestrator
license: MIT
platforms: [linux]
metadata:
  hermes:
    tags: [mas, usage, guardian, rate-limit, cost-control]
    related_skills: [marketing-audit]
---

# Usage Guardian — API Call Tracker

Tracks all OpenRouter API calls and enforces hard limits.

## Hard Limits

| Limit | Value |
|-------|-------|
| Daily max | 200 calls |
| Per-minute max | 10 calls |

## State File

Usage tracked in: `/home/samuelj121314/mas-system/temp/usage-guardian.json`

```json
{
  "date": "2026-05-26",
  "total_calls": 0,
  "calls_per_minute": [
    {"minute": "12:30", "count": 3},
    {"minute": "12:31", "count": 5}
  ],
  "calls": [
    {
      "timestamp": "2026-05-26T12:30:00Z",
      "agent": "mockup-generator",
      "model": "openrouter/google/gemini-2.0-flash-001:free",
      "tokens_estimated": 2048
    }
  ]
}
```

## Check Before Every API Call

```python
import json, datetime, os

USAGE_FILE = "/home/samuelj121314/mas-system/temp/usage-guardian.json"

def check_usage():
    """Returns (allowed: bool, reason: str)"""
    if not os.path.exists(USAGE_FILE):
        return True, "No usage file yet"
    
    with open(USAGE_FILE) as f:
        data = json.load(f)
    
    today = datetime.date.today().isoformat()
    if data.get("date") != today:
        # New day, reset
        return True, "New day, usage reset"
    
    # Daily limit
    if data.get("total_calls", 0) >= 200:
        return False, "DAILY LIMIT REACHED: 200/200 calls. Halting pipeline."
    
    # Per-minute limit
    now = datetime.datetime.now().strftime("%H:%M")
    for entry in data.get("calls_per_minute", []):
        if entry["minute"] == now and entry["count"] >= 10:
            return False, f"MINUTE LIMIT REACHED: 10 calls in minute {now}. Pausing."
    
    return True, "OK"

def record_call(agent, model, tokens=0):
    """Record an API call"""
    today = datetime.date.today().isofile()
    now = datetime.datetime.now()
    minute_key = now.strftime("%H:%M")
    
    if os.path.exists(USAGE_FILE):
        with open(USAGE_FILE) as f:
            data = json.load(f)
    else:
        data = {"date": today, "total_calls": 0, "calls_per_minute": [], "calls": []}
    
    if data["date"] != today:
        data = {"date": today, "total_calls": 0, "calls_per_minute": [], "calls": []}
    
    data["total_calls"] += 1
    
    # Per-minute tracking
    found = False
    for entry in data["calls_per_minute"]:
        if entry["minute"] == minute_key:
            entry["count"] += 1
            found = True
            break
    if not found:
        data["calls_per_minute"].append({"minute": minute_key, "count": 1})
    
    # Trim old minute entries
    data["calls_per_minute"] = data["calls_per_minute"][-20:]
    
    # Call log
    data["calls"].append({
        "timestamp": now.isoformat(),
        "agent": agent,
        "model": model,
        "tokens_estimated": tokens
    })
    
    with open(USAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)
    
    return data["total_calls"]
```

## Integration with Pipeline

Before making ANY OpenRouter API call in any agent:
1. Call `check_usage()` — if False, halt immediately and report
2. Make the API call
3. Call `record_call()` to log it

## Limit Reached Behavior

If a limit is hit:
1. **Do not retry** — the limit is hard
2. Report to user: which limit, current count, recommendation
3. If mid-pipeline, mark that stage as "failed due to rate limit" and continue with fallback data
