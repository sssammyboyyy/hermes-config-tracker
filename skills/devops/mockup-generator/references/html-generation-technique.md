# HTML Generation Technique — Avoiding F-String JS Conflicts

## Problem
Python f-strings interpret `{}` as interpolation markers. JavaScript has curly braces everywhere. f-string + JS = SyntaxError.

## Solution: Template + Concatenation + Substitution

### Step 1: Write Template with Placeholders
Write HTML template to `/tmp/template.html` with `{{PLACEHOLDER}}` markers. JS braces in the file are safe (not in f-strings).

### Step 2: Build Dynamic Content via Concatenation
```python
cards = []
for p in properties:
    card = '<div class="pc' + badge_cls + '">\n'
    card += '  <img src="' + BASE + p['img'] + '" alt="' + p['name'] + '">\n'
    cards.append(card)
property_cards = '\n'.join(cards)
```

### Step 3: Substitute
```python
with open('/tmp/template.html') as f:
    html = f.read()
html = html.replace('{{PROPERTY_CARDS}}', property_cards)
with open(output_path, 'w') as f:
    f.write(html)
```

## When to Use
- HTML > 200 lines with embedded JS
- Dynamic sections (cards, reviews, competitors)
- NEVER use f-strings for HTML+JS

## When write_file Tool Works
- Small static HTML (< 50 lines)
- Medium HTML (50-200 lines) with minimal/brace-free JS
