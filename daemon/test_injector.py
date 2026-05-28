import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("ERROR: Missing Supabase credentials in .env")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def inject_test_job():
    test_payload = {
        "client_name": "African Sky Hotels - Ermelo",
        "target_domain": "https://www.africanskyhotels.com",
        "current_state": "QUEUED"
    }
    
    print(f"Injecting test job for {test_payload['client_name']}...")
    
    try:
        response = supabase.table('hermes_pipeline').insert(test_payload).execute()
        print(f"SUCCESS: Job injected. Project ID: {response.data[0]['project_id']}")
    except Exception as e:
        print(f"FAILED to inject job: {str(e)}")

if __name__ == "__main__":
    inject_test_job()
