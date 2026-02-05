# Testing Claude Skills Manually

## Setup (One-time)

```bash
# 1. Create virtual environment (if not exists)
python3 -m venv venv

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt
```

## Testing Skills

### Test System Health Skill

```bash
# Make sure venv is activated
source venv/bin/activate

# Run the skill
python .claude/skills/system-health/scripts/check_system_health.py
```

**Expected output:**
- System hostname, OS version, CPU count
- Memory usage (total, available, used, percent)
- Disk usage (total, used, free, percent)
- Top 10 processes by memory
- Network interface count
- System uptime
- Status: "healthy"

### Test Top Processes Skill

```bash
# Make sure venv is activated
source venv/bin/activate

# Run with default limit (10 processes)
python .claude/skills/top-processes/scripts/get_top_processes.py

# Run with custom limit (5 processes)
python .claude/skills/top-processes/scripts/get_top_processes.py --limit 5

# Run with more processes (20)
python .claude/skills/top-processes/scripts/get_top_processes.py --limit 20
```

**Expected output:**
- Status: "success"
- Count of processes returned
- Total memory used by top processes
- Array of process details (name, PID, memory MB, CPU %, username)

## Validate JSON Output

```bash
# Pipe output through json.tool to validate
source venv/bin/activate
python .claude/skills/system-health/scripts/check_system_health.py | python -m json.tool

python .claude/skills/top-processes/scripts/get_top_processes.py | python -m json.tool
```

## Check Exit Codes

```bash
source venv/bin/activate

# Run skill
python .claude/skills/system-health/scripts/check_system_health.py

# Check exit code (0 = success, 1 = error)
echo $?
```

## Using with Claude Code

In Claude Code, simply ask:

- **"Check system health"**
- **"What's the system status?"**
- **"Show me resource usage"**
- **"Which processes are using the most memory?"**
- **"Show me top 5 processes"**

Claude will automatically:
1. Detect the relevant skill
2. Activate venv
3. Run the appropriate script
4. Parse the JSON output
5. Respond in natural language

## Troubleshooting

### "ModuleNotFoundError: No module named 'psutil'"
- Make sure venv is activated: `source venv/bin/activate`
- Install dependencies: `pip install -r requirements.txt`

### "source: no such file or directory: venv/bin/activate"
- Create venv first: `python3 -m venv venv`
- Then activate: `source venv/bin/activate`

### "Permission denied"
- Make scripts executable: `chmod +x .claude/skills/*/scripts/*.py`

### JSON output shows "status": "error"
- Check the "error" field in the output for details
- Verify psutil is installed: `pip list | grep psutil`
- Check Python version: `python --version` (should be 3.7+)

## Quick Test All

```bash
#!/bin/bash
# Save as test_skills.sh and run with: bash test_skills.sh

source venv/bin/activate

echo "Testing system-health skill..."
python .claude/skills/system-health/scripts/check_system_health.py | python -m json.tool > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ system-health: PASS"
else
    echo "✗ system-health: FAIL"
fi

echo "Testing top-processes skill..."
python .claude/skills/top-processes/scripts/get_top_processes.py --limit 5 | python -m json.tool > /dev/null
if [ $? -eq 0 ]; then
    echo "✓ top-processes: PASS"
else
    echo "✗ top-processes: FAIL"
fi

echo "All tests complete!"
```
