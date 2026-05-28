"""
OpenRouter Free Model Registry & Intelligent Selector
Models are selected based on task specialty for optimal zero-cost performance.
All models are from OpenRouter's free tier (suffix :free).

Source of truth: /home/samuelj121314/daemon/model_registry.py
This copy is kept in the skill for portability and version tracking.
"""

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

TASK_ROUTING = {
    "mockup_generation": "google/gemini-2.0-flash-001:free",
    "screenshot_to_code": "google/gemini-2.0-flash-001:free",
    "html_mockup": "google/gemini-2.0-flash-lite-preview-02-05:free",
    "performance_analysis": "deepseek/deepseek-r1:free",
    "ux_heuristic": "meta-llama/llama-4-maverick:free",
    "competitor_analysis": "deepseek/deepseek-r1:free",
    "review_sentiment": "meta-llama/llama-4-maverick:free",
    "response_strategy": "deepseek/deepseek-r1:free",
    "report_narrative": "meta-llama/llama-4-maverick:free",
    "roi_calculation": "deepseek/deepseek-chat:free",
    "gap_synthesis": "deepseek/deepseek-r1:free",
    "general": "google/gemini-2.0-flash-lite-preview-02-05:free",
    "code_fallback": "deepseek/deepseek-chat:free",
    "reasoning_fallback": "openrouter/auto:free",
}


def get_model_for_task(task):
    """Select the optimal free model for a given task. Returns dict with model_id + metadata."""
    model_id = TASK_ROUTING.get(task, TASK_ROUTING["general"])
    model_info = FREE_MODEL_REGISTRY.get(model_id, FREE_MODEL_REGISTRY["google/gemini-2.0-flash-lite-preview-02-05:free"])
    return {"model_id": model_id, **model_info}


def get_all_models():
    return FREE_MODEL_REGISTRY


def get_task_routing():
    return TASK_ROUTING
