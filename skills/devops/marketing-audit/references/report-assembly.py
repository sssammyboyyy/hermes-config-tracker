# Report Assembly Reference — MAS Pipeline

Example Python code (run via `execute_code`) to merge audit data into the report template and write the final HTML.

## Template Placeholders

The template at `/home/samuelj121314/mas-system/report-template.html` uses `{{TOKEN}}` placeholders. Replace all of these with real data.

## Full Assembly Script

```python
import json, datetime, os

TEMP_DIR = '/home/samuelj121314/mas-system/temp'
TEMPLATE_PATH = '/home/samuelj121314/mas-system/report-template.html'
OUTPUT_DIR = '/home/samuelj121314/mas-output'

# Read all stage outputs
with open(os.path.join(TEMP_DIR, 'audit-data.json')) as f:
    data = json.load(f)

# Read template
with open(TEMPLATE_PATH) as f:
    html = f.read()

now = datetime.datetime.utcnow()
timestamp = now.strftime('%Y%m%dT%H%M%SZ')

# --- Build gap HTML fragments ---

def build_gap_cards(gaps):
    """Convert list of gap strings to HTML gap cards."""
    return '\n'.join(
        f'<div class="gap-card"><h4>{g.split("—")[0].strip()}</h4><p>{g}</p></div>'
        for g in gaps
    )

# --- Status classes ---
def status_class(value, good_thresh, warn_threshold, lower_is_better=True):
    if lower_is_better:
        if value <= good_thresh: return 'status-good'
        if value <= warn_threshold: return 'status-warn'
        return 'status-bad'
    else:
        if value >= good_thresh: return 'status-good'
        if value >= warn_threshold: return 'status-warn'
        return 'status-bad'

# --- Extract data ---
gbp = data.get('gbp', {})
web = data.get('website', {})
perf = web.get('performance', {})
seo = web.get('seo', {})
conv = web.get('conversion', {})

# --- Build replacements ---
replacements = {
    '{{BUSINESS_NAME}}': data.get('business_name', 'Unknown'),
    '{{BUSINESS_TYPE}}': data.get('business_type', 'Other'),
    '{{AUDIT_DATE}}': now.strftime('%B %d, %Y at %H:%M UTC'),
    '{{TARGET_URL}}': data.get('url', ''),
    '{{EXECUTIVE_SUMMARY}}': data.get('executive_summary', 'Audit completed. See detailed findings below.'),
    '{{GBP_RATING}}': str(gbp.get('rating', 'N/A')),
    '{{REVIEW_COUNT}}': str(gbp.get('review_count', 0)),
    '{{RESPONSE_RATE}}': f"{gbp.get('response_rate', 0)*100:.0f}%",
    '{{LCP_SCORE}}': f"{perf.get('lcp_estimated_ms', 0)/1000:.2f}s" if perf.get('lcp_estimated_ms') else 'N/A',
    '{{GBP_SUMMARY}}': gbp.get('summary', 'No GBP data available.'),
    '{{GBP_GAPS}}': build_gap_cards(gbp.get('gaps', [])),
    '{{REVIEWS_TABLE}}': data.get('reviews_table_html', '<p>No reviews available.</p>'),
    '{{FCP_VALUE}}': f"{perf.get('fcp_estimated_ms', 0)/1000:.2f}s (est.)" if perf.get('fcp_estimated_ms') else 'N/A',
    '{{FCP_STATUS_CLASS}}': status_class(perf.get('fcp_estimated_ms', 9999)/1000, 1.5, 3.0),
    '{{FCP_STATUS}}': 'GOOD' if perf.get('fcp_estimated_ms', 9999)/1000 < 1.5 else ('WARNING' if perf.get('fcp_estimated_ms', 9999)/1000 < 3.0 else 'SLOW'),
    '{{LCP_VALUE}}': f"{perf.get('lcp_estimated_ms', 0)/1000:.2f}s (est.)" if perf.get('lcp_estimated_ms') else 'N/A',
    '{{LCP_STATUS_CLASS}}': status_class(perf.get('lcp_estimated_ms', 9999)/1000, 2.5, 4.0),
    '{{LCP_STATUS}}': 'GOOD' if perf.get('lcp_estimated_ms', 9999)/1000 < 2.5 else ('WARNING' if perf.get('lcp_estimated_ms', 9999)/1000 < 4.0 else 'SLOW'),
    '{{TTI_VALUE}}': f"{perf.get('tti_estimated_ms', 0)/1000:.2f}s (est.)" if perf.get('tti_estimated_ms') else 'N/A',
    '{{TTI_STATUS_CLASS}}': status_class(perf.get('tti_estimated_ms', 9999)/1000, 3.0, 5.0),
    '{{TTI_STATUS}}': 'GOOD' if perf.get('tti_estimated_ms', 9999)/1000 < 3.0 else ('WARNING' if perf.get('tti_estimated_ms', 9999)/1000 < 5.0 else 'SLOW'),
    '{{CLS_VALUE}}': str(perf.get('cls', 'N/A')),
    '{{CLS_STATUS_CLASS}}': 'status-warn',
    '{{CLS_STATUS}}': 'N/A',
    '{{H1_STATUS}}': 'Present' if seo.get('has_h1') else 'Missing',
    '{{H1_CLASS}}': 'status-good' if seo.get('has_h1') else 'status-bad',
    '{{H1_RESULT}}': 'Yes' if seo.get('has_h1') else 'No',
    '{{CTA_STATUS}}': 'Present' if conv.get('has_cta') else 'Missing',
    '{{CTA_CLASS}}': 'status-good' if conv.get('has_cta') else 'status-bad',
    '{{CTA_RESULT}}': 'Yes' if conv.get('has_cta') else 'No',
    '{{PHONE_STATUS}}': 'Present' if conv.get('has_phone') else 'Missing',
    '{{PHONE_CLASS}}': 'status-good' if conv.get('has_phone') else 'status-bad',
    '{{PHONE_RESULT}}': 'Yes' if conv.get('has_phone') else 'No',
    '{{WEBSITE_GAPS}}': build_gap_cards(web.get('gaps', [])),
    '{{AVG_RESPONSE_TIME}}': str(gbp.get('avg_response_time_hours', 'N/A')),
    '{{MOCKUP_IFRAME}}': data.get('mockup_html', '<div style="padding:80px;text-align:center;background:#f8f9fa;color:#666;"><p><strong>Mockup unavailable</strong></p><p>Site took too long to render in headless browser.</p></div>'),
    '{{YEAR}}': str(now.year),
}

# Apply all replacements
for key, value in replacements.items():
    html = html.replace(key, str(value))

# Write output
output_path = os.path.join(OUTPUT_DIR, f'audit-{timestamp}.html')
os.makedirs(OUTPUT_DIR, exist_ok=True)
with open(output_path, 'w') as f:
    f.write(html)

print(f"REPORT_PATH: {output_path}")
print(f"REPORT_SIZE: {len(html)} bytes")
```

## Notes

- The template uses `{{TOKEN}}` placeholders. Every token must be replaced or the raw `{{...}}` will appear in the output.
- `build_gap_cards()` wraps each gap string in a styled `.gap-card` div. The first `—` in the gap text is used as the heading separator.
- Status classes: `status-good` (green), `status-warn` (orange), `status-bad` (red).
- If mockup generation failed, include a placeholder div explaining why.
- Default values use `9999` for missing numeric metrics so they always show as "bad" status rather than crashing the comparison.
