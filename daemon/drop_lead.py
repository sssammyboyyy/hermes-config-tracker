"""
Lead Dropper — Inject a new job into the hermes_pipeline queue.
Usage: python3 drop_lead.py "Client Name" "https://target-domain.com"
"""
import sys
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials in .env")
    sys.exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def drop_lead(client_name: str, target_domain: str):
    # Check if this domain already exists
    existing = supabase.table('hermes_pipeline').select('project_id, current_state').eq('target_domain', target_domain).execute()
    if existing.data:
        row = existing.data[0]
        pid = row['project_id']
        state = row['current_state']
        print(f"EXISTS: '{client_name}' -> {target_domain} (ID: {pid}, State: {state})")
        # Reset to QUEUED so the daemon picks it up again
        supabase.table('hermes_pipeline').update({'current_state': 'QUEUED', 'locked_at': None, 'processing_node_id': None, 'error_log': None, 'updated_at': 'now'}).eq('project_id', pid).execute()
        print(f"RESET: State set to QUEUED. Daemon will re-process.")
        return

    payload = {
        "client_name": client_name,
        "target_domain": target_domain,
        "current_state": "QUEUED"
    }
    try:
        response = supabase.table('hermes_pipeline').insert(payload).execute()
        pid = response.data[0]['project_id']
        print(f"SUCCESS: '{client_name}' -> {target_domain}")
        print(f"  Project ID: {pid}")
        print(f"  State: QUEUED — daemon will pick it up within 5 seconds.")
    except Exception as e:
        print(f"FAILED: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 drop_lead.py \"Client Name\" \"https://target-domain.com\"")
        sys.exit(1)
    drop_lead(sys.argv[1], sys.argv[2])
