#!/usr/bin/env python3
"""
Safely apply a secret value to ~/.hermes/.env.

Usage:
    printf '%s' '<SECRET>' > /tmp/secret_value.txt
    python3 apply_env_secret.py --key TELEGRAM_BOT_TOKEN --file /tmp/secret_value.txt

    # Or pass the value directly (only if it does NOT contain ***):
    python3 apply_env_secret.py --key MY_KEY --value my-secret-value
"""

import argparse
import os
import sys

ENV_PATH = os.path.expanduser('~/.hermes/.env')


def load_secret_from_file(path: str) -> str:
    with open(path, 'r') as f:
        return f.read().strip()


def apply_secret(key: str, value: str) -> None:
    with open(ENV_PATH, 'r') as f:
        lines = f.readlines()

    found = False
    for i, line in enumerate(lines):
        stripped = line.strip()
        # Match commented-out or existing key lines
        if stripped.startswith(f'{key}=') or stripped.startswith(f'# {key}='):
            lines[i] = f'{key}={value}\n'
            found = True
            print(f'Updated line {i + 1}')
            break

    if not found:
        # Append to end of file
        lines.append(f'\n{key}={value}\n')
        print(f'Appended as line {len(lines)}')

    with open(ENV_PATH, 'w') as f:
        f.writelines(lines)

    # Verify
    with open(ENV_PATH, 'r') as f:
        for i, line in enumerate(f, 1):
            if line.strip().startswith(f'{key}=') and not line.strip().startswith('#'):
                print(f'Verified line {i}: {line.rstrip()}')
                break


def main():
    parser = argparse.ArgumentParser(description='Apply a secret to ~/.hermes/.env')
    parser.add_argument('--key', required=True, help='Environment variable name')
    parser.add_argument('--value', help='Secret value (use --file instead if value contains ***)')
    parser.add_argument('--file', help='Path to file containing the secret value')
    args = parser.parse_args()

    if args.file:
        secret = load_secret_from_file(args.file)
    elif args.value:
        secret = args.value
    else:
        print('Error: provide --value or --file', file=sys.stderr)
        sys.exit(1)

    apply_secret(args.key, secret)


if __name__ == '__main__':
    main()
