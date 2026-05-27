# curl-Based Website Audit — Quick Reference

When `browser_navigate` times out, use this curl-based approach to collect all needed data in under 10 seconds.

## Full Audit Command

```bash
# Step 1: Download page with timing data
curl -s -o /tmp/audit-page.html \
  -w "DNS:%{time_namelookup}|TCP:%{time_connect}|TLS:%{time_appconnect}|TTFB:%{time_starttransfer}|TOTAL:%{time_total}|SIZE:%{size_download}|HTTP:%{http_code}" \
  --max-time 15 \
  "https://example.com/" 2>&1

# Step 2: Extract HTML elements from saved file
echo "=== Title ===" && grep -oP '<title>[^<]+</title>' /tmp/audit-page.html | head -1
echo "=== H1 ===" && grep -oP '<h1[^>]*>[^<]+</h1>' /tmp/audit-page.html | head -1
echo "=== Meta Desc ===" && grep -oP 'name="description" content="[^"]+"' /tmp/audit-page.html | head -1
echo "=== Phones ===" && grep -oP '[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}' /tmp/audit-page.html | grep -v '0\.0\.0\|127\.0\.0' | sort -u | head -5
echo "=== CTAs ===" && grep -oiP '(book|reserve|contact|call|buy|sign up|submit|get started|schedule)[^"<]{0,30}' /tmp/audit-page.html | sort -u | head -10
echo "=== Schema ===" && grep -c 'application/ld+json' /tmp/audit-page.html
echo "=== CSS/JS ===" && grep -oP '(href|src)="[^"]*\.(css|js)[^"]*"' /tmp/audit-page.html | wc -l
echo "=== Images ===" && grep -c '<img ' /tmp/audit-page.html
```

## Timing-to-Metrics Mapping

Parse the curl timing output (pipe-delimited):

```python
timing = "DNS:0.331|TCP:0.284|TLS:0.842|TTFB:1.839|TOTAL:2.834|SIZE:98926|HTTP:200"
parts = dict(p.split(':') for p in timing.split('|'))

metrics = {
    "dns_lookup_s": float(parts["DNS"]),
    "tcp_connect_s": float(parts["TCP"]),
    "tls_handshake_s": float(parts["TLS"]),
    "ttfb_s": float(parts["TTFB"]) - float(parts["TLS"]),  # server processing time
    "total_load_s": float(parts["TOTAL"]),
    "page_size_kb": int(parts["SIZE"]) // 1024,
    "http_status": int(parts["HTTP"]),
    "fcp_estimated_ms": int(float(parts["TTFB"]) * 1000),  # TTFB ≈ FCP for server-rendered
    "lcp_estimated_ms": int(float(parts["TOTAL"]) * 1000),  # total load ≈ LCP upper bound
    "tti_estimated_ms": int((float(parts["TOTAL"]) + 0.5) * 1000),  # TTI ≈ total + 500ms JS
}
```

## Why This Works

- `curl` completes in seconds even when the browser hangs on heavy JS
- `grep -oP` extracts all needed HTML elements from the raw HTML in one pass
- TTFB (time_starttransfer - time_appconnect) isolates server processing from network
- Total load time maps to LCP upper bound (actual LCP could be lower if content loads before full page)
- This method captured a complete audit of africanskyhotels.com (99KB page, 2.83s load) without the browser ever loading it

## When to Use Browser Instead

Use the browser method (Performance API) when:
- The site is known to be fast and lightweight
- You need CLS (Cumulative Layout Shift) — curl can't measure this
- You need to verify actual rendered DOM (JS frameworks may change HTML after load)

Use this curl method when:
- `browser_navigate` times out or hangs
- You only need server-side metrics (TTFB, load time, page size)
- The site uses server-side rendering (content is in the initial HTML)
