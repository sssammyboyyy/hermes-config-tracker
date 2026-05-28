"""
OpenRouter Free Model Registry & Intelligent Selector
Models are selected based on task specialty for optimal zero-coverage performance.
All models are from OpenRouter's free tier (suffix :free).
"""

# Registry: model_id -> {specialties, description, speed_tier}
FREE_MODEL_REGISTRY = {
    "google/gemini-2.0-flash-lite-preview-02-05:free": {
        "specialties": ["general", "code_generation", "data_extraction", "html_generation"],
        "description": "Fast general-purpose. Best for HTML mockup generation, code output, data parsing.",
        "speed_tier": "fast",
        "context_window": "medium",
        "best_for": "Mockup generation, UI code, structured data extraction",
    },
    "google/gemini-2.0-flash-001:free": {
        "specialties": ["vision", "multimodal", "screenshot_analysis", "ui_design"],
        "description": "Gemini Flash with vision. Best for screenshot-to-code, visual analysis.",
        "speed_tier": "medium",
        "context_window": "large",
        "best_for": "Vision-to-code, screenshot analysis, UI mockup from images",
    },
    "meta-llama/llama-4-maverick:free": {
        "specialties": ["reasoning", "complex_analysis", "audit_synthesis", "report_narrative"],
        "description": "Llama 4 Maverick. Best for complex reasoning, audit synthesis, narrative copy.",
        "speed_tier": "medium",
        "context_window": "large",
        "best_for": "Audit reports, complex analysis, professional copy writing",
    },
    "meta-llama/llama-4-scout:free": {
        "specialties": ["general", "scraping_assist", "lightweight", "fast_extraction"],
        "description": "Llama 4 Scout. Lightweight and fast. Good for simple extraction tasks.",
        "speed_tier": "fast",
        "context_window": "medium",
        "best_for": "Quick tasks, lightweight extraction, simple transformations",
    },
    "deepseek/deepseek-chat:free": {
        "specialties": ["code_generation", "technical", "algorithmic", "debugging"],
        "description": "DeepSeek Chat. Strong at code, technical reasoning, algorithmic tasks.",
        "speed_tier": "medium",
        "context_window": "medium",
        "best_for": "Code generation, technical analysis, debugging pipelines",
    },
    "deepseek/deepseek-r1:free": {
        "specialties": ["deep_reasoning", "audit_logic", "complex_decisioning", "strategy"],
        "description": "DeepSeek R1. Chain-of-thought reasoning. Best for audit logic and strategy.",
        "speed_tier": "slow",
        "context_window": "large",
        "best_for": "Audit decision logic, complex reasoning, strategic recommendations",
    },
    "openrouter/auto:free": {
        "specialties": ["auto_routing", "fallback", "general"],
        "description": "Auto-router. OpenRouter picks the best free model for the task.",
        "speed_tier": "variable",
        "context_window": "variable",
        "best_for": "Fallback, unknown tasks, general-purpose when unsure",
    },
}

# Task-to-specialty mapping: determines which model to use based on what we're doing
TASK_ROUTING = {
    # Mockup Agent tasks
    "mockup_generation": "google/gemini-2.0-flash-001:free",      # Vision: screenshot -> HTML
    "screenshot_to_code": "google/gemini-2.0-flash-001:free",     # Vision: analyze & generate
    "html_mockup": "google/gemini-2.0-flash-lite-preview-02-05:free",  # Fast HTML generation

    # Website Audit tasks
    "performance_analysis": "deepseek/deepseek-r1:free",          # Deep reasoning on metrics
    "ux_heuristic": "meta-llama/llama-4-maverick:free",           # Narrative + reasoning
    "competitor_analysis": "deepseek/deepseek-r1:free",            # Strategic comparison

    # GBP Audit tasks
    "review_sentiment": "meta-llama/llama-4-maverick:free",       # Sentiment + narrative
    "response_strategy": "deepseek/deepseek-r1:free",              # Strategic recommendations

    # Report Assembly tasks
    "report_narrative": "meta-llama/llama-4-maverick:free",       # Professional copy
    "roi_calculation": "deepseek/deepseek-chat:free",             # Technical accuracy
    "gap_synthesis": "deepseek/deepseek-r1:free",                 # Complex reasoning

    # General / fallback
    "general": "google/gemini-2.0-flash-lite-preview-02-05:free",
    "code_fallback": "deepseek/deepseek-chat:free",
    "reasoning_fallback": "openrouter/auto:free",
}


def get_model_for_task(task: str) -> dict:
    """Select the optimal free model for a given task."""
    model_id = TASK_ROUTING.get(task, TASK_ROUTING["general"])
    model_info = FREE_MODEL_REGISTRY.get(model_id, FREE_MODEL_REGISTRY["google/gemini-2.0-flash-lite-preview-02-05:free"])
    return {"model_id": model_id, **model_info}


def get_all_models() -> dict:
    """Return the full registry."""
    return FREE_MODEL_REGISTRY


def get_task_routing() -> dict:
    """Return the task-to-model routing table."""
    return TASK_ROUTING


# Quick CLI test
if __name__ == "__main__":
    print("=== FREE MODEL REGISTRY ===")
    for mid, info in FREE_MODEL_REGISTRY.items():
        short_name = mid.split("/")[-1]
        print(f"  {short_name}: {info['speed_tier']:6s} | {info['best_for']}")

    print("\n=== TASK ROUTING ===")
    for task, model in TASK_ROUTING.items():
        short = model.split("/")[-1]
        print(f"  {task:30s} -> {short}")

    print("\n=== SELECTOR TEST ===")
    test_tasks = ["mockup_generation", "performance_analysis", "report_narrative", "gap_synthesis", "general"]
    for t in test_tasks:
        result = get_model_for_task(t)
        print(f"  {t:30s} -> {result['model_id'].split('/')[-1]} ({result['description']})")
