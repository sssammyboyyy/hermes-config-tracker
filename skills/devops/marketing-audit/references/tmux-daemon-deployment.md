# Tmux Persistent Daemon Deployment

## Pattern: Background Python Daemon That Survives SSH Disconnect

### Create and Start
```bash
# Kill any hanging processes (use pgrep first — see mas-pipeline-patterns mistake 21)
pgrep -f "hermes_worker.py" && kill $(pgrep -f "hermes_worker.py") || true

# Create detached tmux session
tmux new-session -d -s hermes-daemon

# Inject startup sequence
tmux send-keys -t hermes-daemon "cd /home/samuelj121314/daemon" C-m
tmux send-keys -t hermes-daemon "source venv/bin/activate" C-m
tmux send-keys -t hermes-daemon "clear" C-m
tmux send-keys -t hermes-daemon "echo '--- PERSISTENT HERMES WORKER ONLINE ---'" C-m
tmux send-keys -t hermes-daemon "python3 hermes_worker.py" C-m

# Verify
tmux ls
tmux capture-pane -t hermes-daemon -p
```

### Reattach (Next Session)
```bash
tmux attach-session -t hermes-daemon
```

### Detach Without Killing
Press `Ctrl+B`, release, then press `D`. Daemon keeps running.

### Check Status Without Attaching
```bash
tmux ls                          # List sessions
tmux capture-pane -t hermes-daemon -p  # View current output
```

### Stop Daemon
```bash
# Graceful: send Ctrl+C in the pane
tmux send-keys -t hermes-daemon C-c
sleep 2
tmux send-keys -t hermes-daemon "exit" C-m

# Nuclear: kill the session entirely
tmux kill-session -t hermes-daemon
```

### Key Rules
- Never `pkill -f python3` to stop the daemon — too broad, kills Hermes gateway
- Always use `pgrep` first to verify the PID before killing
- The daemon's working directory MUST be `daemon/` (relative paths like `../MEMORY_.md` depend on it)
- Use absolute paths in the worker for production: `os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', f'MEMORY_{project_id}.md')`
