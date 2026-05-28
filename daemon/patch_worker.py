import os

file_path = "/home/samuelj121314/daemon/hermes_worker.py"
with open(file_path, "r") as f:
    code = f.read()

# Add imports at the top if not present
if "import subprocess" not in code:
    code = code.replace("import time", "import time\nimport subprocess\nfrom generate_ui import generate_html_report")

# Inject the UI generation and Git push right before LIVE update
target_hook = "# Mark LIVE"
injection = """
        # Generate UI and Push to GitHub Pages
        report_path = generate_html_report(domain, project_id, job.get('client_name', 'Client'), gmb_rating, extracted_colors)
        print(f"Generated report at {report_path}")

        # Zero-Cost Hosting Auto-Deploy
        repo_dir = "/home/samuelj121314/hermes-config-tracker"
        subprocess.run(["git", "add", f"report_{project_id}.html"], cwd=repo_dir, check=True)
        subprocess.run(["git", "commit", "-m", f"Auto-deploy report for {domain}"], cwd=repo_dir, check=True)
        subprocess.run(["git", "push", "origin", "gh-pages"], cwd=repo_dir, check=True)
        print(f"[{NODE_ID}] Pushed {domain} report to gh-pages.")

        # Mark LIVE"""

already_patched = "generate_html_report" in code.split(target_hook)[0] if target_hook in code else False

if target_hook in code and not already_patched:
    code = code.replace(target_hook, injection)
    with open(file_path, "w") as f:
        f.write(code)
    print("Worker successfully patched with UI generation and Git deployment.")
else:
    if already_patched:
        print("Worker already patched.")
    else:
        print("ERROR: target hook not found.")
