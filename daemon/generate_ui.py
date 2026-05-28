import os
from collections import Counter
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_primary_brand_color(hex_list):
    if not hex_list:
        return '#ff6900'  # JCE Media default fallback

    # Filter out common backgrounds/text colors (whites, blacks, grays)
    ignore_list = ['#ffffff', '#000000', '#111111', '#222222', '#333333', '#f8f9fa', '#f3f4f6', '#32373c']
    filtered_colors = [c.lower() for c in hex_list if c.lower() not in ignore_list]

    if not filtered_colors:
        return hex_list[0]

    # Return the most frequent non-generic color
    return Counter(filtered_colors).most_common(1)[0][0]

def generate_html_report(domain_target, project_id, client_name, gmb_rating, extracted_colors):
    primary_color = get_primary_brand_color(extracted_colors)
    lost_leads_text = "50% Drop in Conversions" if gmb_rating < 4.9 else "Optimized Map Pack"

    html_content = (
        '<!DOCTYPE html>\n'
        '<html lang="en">\n'
        '<head>\n'
        '    <meta charset="UTF-8">\n'
        '    <meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
        '    <title>Diagnostic Audit: ' + client_name + '</title>\n'
        '    <style>\n'
        '        :root { --brand-primary: ' + primary_color + '; }\n'
        '        body { background-color: #0f172a; color: #f8fafc; font-family: -apple-system, sans-serif; padding: 2rem; }\n'
        '        .glass-card {\n'
        '            background: rgba(255, 255, 255, 0.05);\n'
        '            backdrop-filter: blur(10px);\n'
        '            border: 1px solid rgba(255, 255, 255, 0.1);\n'
        '            border-radius: 12px;\n'
        '            padding: 2rem;\n'
        '            margin-bottom: 1.5rem;\n'
        '            border-top: 4px solid var(--brand-primary);\n'
        '        }\n'
        '        h1 { font-size: 2rem; margin-bottom: 0.5rem; }\n'
        '        .metric-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 2rem; }\n'
        '        .metric { padding: 1rem; background: rgba(0,0,0,0.3); border-radius: 8px; }\n'
        '        .alert-text { color: #ef4444; font-weight: bold; }\n'
        '    </style>\n'
        '</head>\n'
        '<body>\n'
        '    <div class="glass-card">\n'
        '        <h1>Zero-Fluff Conversion Audit</h1>\n'
        '        <p>Target: <strong>' + domain_target + '</strong></p>\n'
        '\n'
        '        <div class="metric-grid">\n'
        '            <div class="metric">\n'
        '                <h3>Core Web Vitals (Speed-to-Lead)</h3>\n'
        '                <p class="alert-text">Diagnostic Flag Detected</p>\n'
        '                <p>In the ZA market, response time decay kills 50% of conversions after 5 minutes. Your current infrastructure is bleeding leads.</p>\n'
        '            </div>\n'
        '            <div class="metric">\n'
        '                <h3>Local Visibility (ReviewTap Trigger)</h3>\n'
        '                <p class="alert-text">Map Pack Rating: ' + str(gmb_rating) + ' / 5.0</p>\n'
        '                <p>Capturing local intent requires a 4.9+ baseline. ' + lost_leads_text + '.</p>\n'
        '            </div>\n'
        '        </div>\n'
        '    </div>\n'
        '</body>\n'
        '</html>'
    )

    # Output directly to the git-tracked repo
    repo_path = "/home/samuelj121314/workspace/hermes-config-tracker"
    output_path = repo_path + "/report_" + project_id + ".html"

    with open(output_path, "w") as f:
        f.write(html_content)

    return output_path


if __name__ == "__main__":
    # Fetch the live project and generate
    response = supabase.table('hermes_pipeline').select('*').eq('current_state', 'LIVE').execute()
    if response.data:
        data = response.data[0]
        path = generate_html_report(
            data['target_domain'],
            data['project_id'],
            data['client_name'],
            data.get('gmb_rating', 4.8),
            data.get('extracted_hex_colors', [])
        )
        print("SUCCESS: " + path)
    else:
        print("No LIVE projects found.")
