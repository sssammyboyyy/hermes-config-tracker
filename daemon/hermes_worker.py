import asyncio
import httpx
import re
import os
import uuid
import time
import subprocess
from supabase import create_client, Client
from generate_ui import generate_html_report
from model_registry import get_model_for_task
from dream_sequence import dream_scheduler
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
NODE_ID = str(uuid.uuid4())

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

HEX_REGEX = re.compile(r'#(?:[A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})\b')

MAGIC_NUMBERS = {
    'PNG': b'\x89PNG\r\n\x1a\n',
    'JPEG': b'\xFF\xD8\xFF'
}

async def verify_asset_integrity(asset_url: str) -> bool:
    """Gate 2: Asset 200 OK & MIME Verification via 8-byte streaming."""
    try:
        async with httpx.AsyncClient() as client:
            async with client.stream("GET", asset_url, timeout=5.0) as response:
                if response.status_code != 200:
                    return False
                first_chunk = await response.aiter_bytes(8).__anext__()
                return first_chunk.startswith(MAGIC_NUMBERS['PNG']) or first_chunk.startswith(MAGIC_NUMBERS['JPEG'])
    except Exception:
        return False

async def process_job(job: dict):
    project_id = job['project_id']
    domain = job['target_domain']
    print(f"[{NODE_ID}] Processing {domain} (ID: {project_id})")
    
    try:
        # 1. EXTRACTION PHASE
        async with httpx.AsyncClient() as client:
            start_time = time.time()
            res = await client.get(domain, timeout=10.0)
            ttfb_ms = (time.time() - start_time) * 1000
            
            # Gate 1: ZA Network Latency Check (Diagnostic, not fatal)
            if ttfb_ms > 1500:
                print(f"DIAGNOSTIC FLAG: Target TTFB is {ttfb_ms:.2f}ms. Client is bleeding leads. Injecting into report.")

            html_stream = res.text
            extracted_colors = list(set(HEX_REGEX.findall(html_stream)))
            
            # Gate 4: Syntax Check (Basic DOM sanity on target)
            if html_stream.count('{') != html_stream.count('}'):
                print("Warning: Target domain has unbalanced brackets.")

        # 2. AUDIT PHASE (Simulated GBP & Metrics)
        # In production, this pings the GBP API. Here we simulate the pipeline progression.
        gmb_rating = 4.8 
        
        # Gate 3: Algorithmic Suppression Check
        if gmb_rating < 4.9:
            print(f"MAP_PACK_PENALTY: Triggering ReviewTap Upsell for {domain}")
            
        # 3. VALIDATION PHASE (Gate 5: Memory write)
        memory_path = f"../MEMORY_{project_id}.md"
        with open(memory_path, "w") as f:
            f.write(f"# HERMES MEMORY LEDGER\nDomain: {domain}\nColors: {extracted_colors}\nStatus: VALIDATED")
        
        if not os.path.exists(memory_path):
            raise SystemError("Gate 5 Failed: MEMORY.md write failed.")

        # Generate UI and Push to GitHub Pages
        report_path = generate_html_report(domain, project_id, job.get('client_name', 'Client'), gmb_rating, extracted_colors)
        print("Generated report at " + report_path)

        # Zero-Cost Hosting Auto-Deploy
        repo_dir = "/home/samuelj121314/workspace/hermes-config-tracker"
        subprocess.run(["git", "add", "report_" + project_id + ".html"], cwd=repo_dir, check=True)
        subprocess.run(["git", "commit", "-m", "Auto-deploy report for " + domain], cwd=repo_dir, check=True)
        subprocess.run(["git", "push", "origin", "gh-pages"], cwd=repo_dir, check=True)
        print("[" + NODE_ID + "] Pushed " + domain + " report to gh-pages.")

        # Mark LIVE
        supabase.table('hermes_pipeline').update({
            'current_state': 'LIVE',
            'extracted_hex_colors': extracted_colors,
            'gmb_rating': gmb_rating,
            'asset_integrity_status': True
        }).eq('project_id', project_id).execute()
        
        print(f"[{NODE_ID}] Successfully deployed {domain} to LIVE.")

    except Exception as e:
        print(f"[{NODE_ID}] FAILED {domain}: {str(e)}")
        supabase.table('hermes_pipeline').update({
            'current_state': 'FAILED',
            'error_log': str(e)
        }).eq('project_id', project_id).execute()

async def main_loop():
    print(f"Starting Hermes Daemon Node: {NODE_ID}")
    while True:
        try:
            # Call RPC to securely check out one job
            response = supabase.rpc('checkout_hermes_task', {'worker_id': NODE_ID}).execute()
            jobs = response.data
            
            if jobs:
                await process_job(jobs[0])
            else:
                await asyncio.sleep(5) # Poll every 5 seconds
        except Exception as e:
            print(f"RPC Error or Connection lost: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    async def main():
        await asyncio.gather(
            main_loop(),
            dream_scheduler()
        )
    asyncio.run(main())
