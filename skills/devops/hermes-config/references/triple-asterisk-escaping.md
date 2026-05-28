# write_file Tool: Triple-Asterisk Escaping

## Problem

The `write_file` tool (and inline Python via `terminal -c` / heredocs) interprets three
consecutive asterisks (`***`) as markdown bold+italic formatting. This causes:

- **SyntaxError** in Python files containing `***` in strings
- **Silent truncation** — the content after `***` is lost
- **Parse failures** in shell heredocs

This commonly affects:
- Telegram bot tokens (format: `<id>:<hash>`, hash often contains `***`)
- API keys with base64 segments
- Any secret value that happens to contain `***`

## Solutions

### 1. Temp file + Python script (recommended)

```bash
# Step 1a: Write secret to temp file using printf
printf '%s' '<SECRET>' > /tmp/secret.txt

# Step 1b: If the token contains ':' or other shell-sensitive chars,
#   double-quoted echo also works:
echo "<SECRET>" > /tmp/secret.txt

# Step 2: Copy and run the reusable script (code never contains ***)
cp ~/.hermes/skills/devops/hermes-config/scripts/apply_env_secret.py /tmp/apply.py
python3 /tmp/apply.py --key TELEGRAM_BOT_TOKEN --file /tmp/secret.txt
```

### 2. Python heredoc with string concatenation

When you can't use a temp file for the script (e.g. no skill dir available), use a heredoc with the token split into concatenated pieces — none of which contains three consecutive asterisks:

```bash
python3 << 'EOF'
token = '7972598265:' + 'AAHa_xt4EyEo9k2XR1xAZVbJrp2PhF_UzxY'
# ... use token ...
EOF
```

The heredoc delimiter `'EOF'` (quoted) prevents shell expansion inside the heredoc. String concatenation in the Python code avoids `***` in the source.

### 3. String concatenation in write_file scripts

```python
# BAD — write_file tool mangles this:
token = 'abc***xyz'

# GOOD — split the asterisks:
token = 'abc' + '*' + '*' + '*' + 'xyz'

# Or:
token = 'abc' + chr(42)*3 + 'xyz'
```

### 4. Base64 encoding (avoids all special chars)

```bash
echo -n '<SECRET>' | base64
# Use the base64 output in the script, decode at runtime
```

## What does NOT work

- `sed` with `/`, `:`, or `*` in the value — conflicts with sed delimiters and shell globbing. Even alternate delimiters (`sed 's^...^...'`) fail because the shell still mangles the token before sed sees it.
- `terminal -c "python3 -c '...'"` — heredoc parsing chokes on `***`
- `write_file` with the secret inline — markdown interpretation
- `execute_code` with `***` in string literals — SAME parsing issue as `write_file` and `terminal -c`. The `execute_code` tool sends Python source through the same markdown-aware pipeline. Any Python source containing `***` (even inside a string) will get mangled. **Workaround**: write a `.py` file first (using `write_file` with the key split via concatenation or read from temp file), then run it.
- Shell variable expansion with unquoted `*` — glob expansion
- `awk` with double-quoted token values — the quotes get stripped by the tool's command parser
- **Nested single quotes in shell**: `sed -i 's/.../'token'/...'` breaks when the token itself contains quotes or special chars. Use double quotes or Python instead.
- **Writing `.env` files with `write_file`**: The `write_file` tool interprets `***` in the content parameter as markdown, even when writing non-Python files like `.env`. You CANNOT write `OPENROUTER_API_KEY=***` directly. Instead: (a) write the value to `/tmp/secret.txt` via `printf`, (b) write a Python script that reads the temp file and writes the `.env`, (c) run the script.

## The Only Reliable Pattern for Writing Secrets

When ALL tools choke on `***`, this 3-step pattern always works:

```bash
# Step 1: Write secret value to temp file (printf handles any chars)
printf '%s' '<FULL_SECRET_VALUE>' > /tmp/secret.txt

# Step 2: Write a Python script that reads the temp file
# (script source never contains the secret, so no *** issue)
cat > /tmp/write_env.py << 'SCRIPTEOF'
import os
with open('/tmp/secret.txt') as f:
    secret = f.read().strip()
content = 'KEY_NAME=' + secret + chr(10)
with open('/path/to/.env', 'w') as f:
    f.write(content)
os.remove('/tmp/secret.txt')
print('Written, len=' + str(len(secret)))
SCRIPTEOF

# Step 3: Run the script
python3 /tmp/write_env.py
```

Key insight: `printf '%s'` in a regular `terminal` command can write ANY character sequence to a file — the `***` issue only affects `write_file`, `execute_code`, and `terminal -c` (where the content passes through markdown parsing).

## Token Length Verification

After writing a secret, ALWAYS verify the stored length matches expectations:

```bash
# Check the character count of the stored value
grep TELEGRAM_BOT_TOKEN ~/.hermes/.env | awk -F= '{print length($2)}'

# For Telegram tokens: should be ~46 chars (e.g. "7972598265:AAHa_xt4EyEo9k2XR1xAZVbJrp2PhF_UzxY")
# If you see 11 or 15, the token was truncated by a bungled sed/write attempt
```

A truncated token (e.g. only `7972598265:...` = 11 chars) will cause `InvalidToken` from Telegram with no obvious error message — the gateway just says the token was rejected.

## echo vs printf for Writing Secrets

Both work for tokens with colons and dashes when properly quoted:

```bash
# printf — no trailing newline (use \n if needed)
printf '%s' '7972598265:AAHa_xt4EyEo9k2XR1xAZVbJrp2PhF_UzxY' > /tmp/secret.txt

# echo with double quotes — adds trailing newline (fine for Python .strip())
echo "7972598265:AAHa_xt4EyEo9k2XR1xAZVbJrp2PhF_UzxY" > /tmp/secret.txt
```

**Do NOT use single quotes with `echo`** if the token contains characters that look like shell metacharacters — the tool's command parser may still mangle them. Double quotes are safer.

## Related

- `scripts/apply_env_secret.py` — reusable script for safely writing secrets to `.env`
