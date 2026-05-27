# NotebookLM MCP — Research & Truth System

## What It Does
Uploads research documents about a business/industry into Google NotebookLM, then queries those notebooks during audit generation to:
1. Generate truth-specific copy (not generic templates)
2. Extract brand voice from actual content
3. Identify competitive positioning opportunities
4. Surface review themes for each property
5. Generate property-specific descriptions

## Configuration Required

### Step 1: Enable notebooklm MCP on the VM

Add to ~/.hermes/config.yaml under mcp_servers:

```yaml
mcp_servers:
  notebooklm:
    command: npx
    args: ["-y", "@google/notebooklm-mcp-server"]
    env:
      GOOGLE_API_KEY: "${GOOGLE_API_KEY}"
```

OR if using a custom wrapper:

```yaml
mcp_servers:
  notebooklm:
    command: node
    args: ["/home/samuelj121314/.hermes/mcp/notebooklm-mcp/index.js"]
    env:
      GOOGLE_API_KEY: "${GOOGLE_API_KEY}"
```

### Step 2: Set GOOGLE_API_KEY

Already in .env as part of Google Cloud project gen-lang-client-0110871691.

## Research Data Structure

Before each audit, create /tmp/research/[client-name]/:

```
african-sky/
├── website-content.txt      # Full text extraction from their site
├── gbp-reviews.json         # All Google reviews per property
├── competitors.json         # Competitor data from Places API
├── industry-notes.txt       # SA hospitality industry insights
└── brand-voice.txt          # Their actual taglines, descriptions, USP
```

## NotebookLM Workflow

### Phase 1: Upload (once per client type/industry)
1. Create notebook: "South African Hospitality Industry"
2. Upload: industry reports, tourism stats, hospitality trends
3. This becomes the BASE knowledge for ALL hotel clients

### Phase 2: Per-Client Notebook
1. Create notebook: "[Client Name] — Research"
2. Upload: website-content.txt, gbp-reviews.json, competitors.json, brand-voice.txt
3. Query during audit:
   - "What is [client]'s actual brand voice based on their website?"
   - "What are the top 3 review themes for [property]?"
   - "What makes [client] different from competitors?"
   - "Write a compelling hero section for [client] using their actual language"
   - "What specific copy would resonate with [client]'s target guest?"

### Phase 3: Copy Generation
Use NotebookLM insights to:
- Write property descriptions in the client's actual voice
- Create headlines that match their positioning
- Reference specific amenities/services they actually offer
- Address real pain points from reviews
- Highlight real differentiators vs competitors

## Quality Impact

Without NotebookLM:
- Generic copy: "Experience South Africa's Finest Hotels"
- Quality: 6/10

With NotebookLM:
- Truth-based copy: "WHERE WOULD YOU LIKE TO STAY? African Sky Hotels and Resorts welcomes you to our portfolio of hotels in White River, Ermelo, Harrismith, Newcastle and Werlte in Germany."
- Quality: 9/10

## Integration with Audit Pipeline

In marketing-audit skill, add step:

```
Phase 0: Research & Upload (BEFORE mockup generation)
  1. Scrap client website → save to /tmp/research/[client]/website-content.txt
  2. Fetch GBP reviews → save to /tmp/research/[client]/gbp-reviews.json
  3. Fetch competitors → save to /tmp/research/[client]/competitors.json
  4. Extract brand voice → save to /tmp/research/[client]/brand-voice.txt
  5. Upload to NotebookLM via MCP
  6. Query for copy insights
  7. Use insights to generate mockup copy
```

## Note

NotebookLM MCP is NOT yet configured. This skill documents the intended setup.
When GOOGLE_API_KEY is available and notebooklm-mcp-server npm package is installed,
it can be activated by adding the mcp_servers config entry.

Current workaround: Use web_search + site scraping + OpenRouter queries to simulate
NotebookLM insights until MCP is configured.
