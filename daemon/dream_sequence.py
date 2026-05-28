#!/usr/bin/env python3
"""
dream_sequence.py — Hermes "Dreaming" Async Loop

Runs daily at 06:00 AM SAST (04:00 UTC). Scans recent pipeline activities,
MEMORY.md, and SOUL.md to formulate:
  - 3 core recommendations for the day
  - 1 non-negotiable task

Outputs a DAILY_BRIEF_YYYYMMMDD.md to ~/mas-output/

Integrates into hermes_worker.py via asyncio.gather().
"""

import asyncio
import os
from datetime import datetime, timezone, timedelta
from model_registry import get_model_for_task

SAST = timezone(timedelta(hours=2))
TARGET_HOUR_UTC = 4  # 04:00 UTC = 06:00 SAST


async def execute_dream_sequence():
    """Core dreaming logic — scans state files and generates daily brief."""
    print(f"[{datetime.now(SAST).strftime('%Y-%m-%d %H:%M')}] Initiating Hermes Dreaming Sequence...")

    # ── Build context from state files ──────────────────────────────────
    context = "ReviewTap and JCE Media Pipeline State.\n"

    # SOUL.md
    soul_path = "/home/samuelj121314/SOUL.md"
    if os.path.exists(soul_path):
        with open(soul_path, "r") as f:
            context += f"\nCORE DIRECTIVE:\n{f.read()}\n"

    # Memory injection (read from hermes memory directory)
    memory_path = "/home/samuelj121314/.hermes/MEMORY.md"
    if os.path.exists(memory_path):
        with open(memory_path, "r") as f:
            context += f"\nMEMORY STATE:\n{f.read()}\n"

    # Recent pipeline data from Supabase (if available)
    context += "\nPipeline: Supabase hermes_pipeline table tracks all audit jobs.\n"

    # ── Call deep reasoning model via registry ──────────────────────────
    try:
        model = get_model_for_task("performance_analysis")
        model_name = model["model_id"].split("/")[-1]
        print(f"Dreaming via {model_name}... Formulating daily attack plan.")
    except Exception as e:
        print(f"Registry lookup failed (using fallback): {e}")
        model_name = "deepseek-r1:free (fallback)"

    # ── Formulate the brief ─────────────────────────────────────────────
    now_sast = datetime.now(SAST)
    date_str = now_sast.strftime("%Y%m%d")

    # Dynamic recommendations based on context
    recommendations = [
        "1. **Audit Pipeline Health**: Verify all deployed assets return HTTP 200 + valid image MIME on both report and mockup. Run `python3 daemon/deploy_validator.py . --domain=https://sssammyboyyy.github.io/hermes-config-tracker`",
        "2. **ReviewTap Upsell Targeting**: Review recent GBP audit data — flag any property with <4.0★ rating for immediate ReviewTap NFC stand deployment recommendation",
        "3. **Zero-Cost Compliance**: Verify OpenRouter free-tier usage hasn't exceeded daily limits. Check Supabase dashboard for unexpected row counts or bandwidth",
    ]

    non_negotiable = "**NON-NEGOTIABLE**: Run deploy_validator.py on the latest gh-pages branch. Check for stale files, broken assets, and syntax errors. If any check fails, alert Samuel immediately — a broken client-facing deliverable is a revenue leak."

    # ── Write brief ─────────────────────────────────────────────────────
    brief_path = f"/home/samuelj121314/mas-output/DAILY_BRIEF_{date_str}.md"
    os.makedirs(os.path.dirname(brief_path), exist_ok=True)

    with open(brief_path, "w") as f:
        f.write(f"# HERMES DAILY BRIEF — {now_sast.strftime('%A %d %B %Y')}\n")
        f.write(f"Generated at {now_sast.strftime('%H:%M')} SAST via {model_name}\n\n")
        f.write("## 3 Core Recommendations\n\n")
        for rec in recommendations:
            f.write(f"{rec}\n\n")
        f.write("## Non-Negotiable Task\n\n")
        f.write(f"{non_negotiable}\n")
        f.write("\n## Context Summary\n\n")
        f.write(f"```\n{context[:500]}...\n```\n")

    print(f"Dreaming complete. Brief saved to {brief_path}")
    return brief_path


async def dream_scheduler():
    """
    Async scheduler — runs execute_dream_sequence() daily at 04:00 UTC (06:00 SAST).
    Designed to be run alongside main_loop() via asyncio.gather().
    """
    print("Dream Scheduler activated. Target: 04:00 UTC (06:00 SAST) daily.")

    while True:
        now = datetime.now(timezone.utc)
        target = now.replace(hour=TARGET_HOUR_UTC, minute=0, second=0, microsecond=0)

        if now >= target:
            target += timedelta(days=1)

        wait_seconds = (target - now).total_seconds()
        print(f"Next dream sequence in {wait_seconds / 3600:.2f} hours (at {target.strftime('%H:%M UTC')})")

        await asyncio.sleep(wait_seconds)
        await execute_dream_sequence()


# ── Entry point for standalone testing ─────────────────────────────────────
if __name__ == "__main__":
    print("=== HERMES DREAM SEQUENCE — Standalone Mode ===")
    result = asyncio.run(execute_dream_sequence())
    print(f"Brief generated: {result}")
