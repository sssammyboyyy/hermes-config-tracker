import os

file_path = "/home/samuelj121314/daemon/hermes_worker.py"
with open(file_path, "r") as f:
    code = f.read()

# 1. Inject the import statement at the top if missing
if "from model_registry import get_model_for_task" not in code:
    code = code.replace("import time", "import time\nfrom model_registry import get_model_for_task")

# 2. Replace the static model assignment with dynamic routing
target_static = '"google/gemini-2.0-flash-lite-preview-02-05:free"'
dynamic_call = 'get_model_for_task("mockup_generation")'

if target_static in code:
    code = code.replace(target_static, dynamic_call)
    with open(file_path, "w") as f:
        f.write(code)
    print("SUCCESS: Worker patched with dynamic model registry.")
else:
    print("Worker already patched or target string not found. Please review manually.")
