# Setup Guide for Med Scheduler

Complete setup instructions from scratch.

## Prerequisites

- Python 3.8 or higher
- Git installed
- Internet connection

## Step-by-Step Setup

### 1. Verify Python Installation

Open Git Bash and run:

```bash
python --version
# Should show Python 3.8 or higher

# If that doesn't work, try:
python3 --version
```

### 2. Navigate to Your Project

```bash
cd /c/Users/YourName/Documents/med-scheduler
# Or wherever you cloned the repo
```

### 3. Create a Virtual Environment (Recommended)

This keeps your dependencies isolated:

```bash
# Create virtual environment
python -m venv venv

# Activate it (Git Bash):
source venv/bin/activate

# Your prompt should now show (venv)
```

**Windows PowerShell:**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

You should see:
- ✓ pyyaml
- ✓ requests
- ✓ python-dateutil
- ✓ google-generativeai

### 5. Get Gemini API Key

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click **"Create API Key"**
4. Click **"Create API key in new project"**
5. Copy the key (starts with `AIza...`)

### 6. Set API Key

**Git Bash / Mac / Linux:**
```bash
export GEMINI_API_KEY='AIzaSy...'

# To make it permanent, add to ~/.bashrc:
echo 'export GEMINI_API_KEY="AIzaSy..."' >> ~/.bashrc
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY='AIzaSy...'

# To make it permanent:
[System.Environment]::SetEnvironmentVariable('GEMINI_API_KEY', 'AIzaSy...', 'User')
```

### 7. Test the Installation

```bash
python main.py
```

You should see:
```
======================================================================
  Med Scheduler v0.1.0 - Demo
======================================================================

✓ Gemini API key found - using AI-powered rescheduling
```

## Troubleshooting

### Problem: "python: command not found"

Try `python3` instead:
```bash
python3 --version
python3 -m venv venv
python3 main.py
```

### Problem: "No module named 'yaml'"

Install dependencies:
```bash
pip install -r requirements.txt
```

### Problem: "Permission denied"

On Windows, you might need to:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Problem: API key not found

Make sure you've set it:
```bash
# Check if it's set:
echo $GEMINI_API_KEY

# Should show your key
# If empty, set it again
```

### Problem: "Rate limit exceeded"

Gemini has free tier limits:
- 60 requests per minute
- Use the rule-based fallback by not setting the API key

## Running the Demo

### Full AI Demo:

```bash
# Make sure API key is set
export GEMINI_API_KEY='your-key'

# Run demo
python main.py
```

### Rule-Based Demo (No API Key):

```bash
# Unset the key
unset GEMINI_API_KEY

# Run demo
python main.py
```

## Next Steps

1. ✅ Demo runs successfully
2. 📖 Read the code in `engine/models.py`
3. 🔧 Edit `rules/constraints.yaml` with your medications
4. 🧪 Modify `main.py` to test your scenarios
5. 🚀 Build on top of it!

## File Structure Reference

```
med_scheduler/
├── engine/
│   ├── __init__.py          # Package initialization
│   ├── models.py            # Data structures
│   ├── api_client.py        # OpenFDA API
│   ├── rule_loader.py       # YAML parser
│   └── optimizer.py         # AI logic
├── rules/
│   ├── constraints.yaml     # YOUR RULES HERE
│   ├── tags.yaml
│   └── sources.yaml
├── data/
│   └── drugs.yaml           # YOUR MEDS HERE
├── main.py                  # START HERE
└── requirements.txt
```

## Understanding the Code

### Read in this order:

1. `engine/models.py` - Understand the data structures
2. `main.py` - See how it all fits together
3. `engine/optimizer.py` - See the AI logic
4. `rules/constraints.yaml` - See how rules are defined

### Key Concepts:

- **Medication**: A drug with timing and constraints
- **Constraint**: A rule (interaction, timing, food)
- **Schedule**: All medications + constraints
- **MissedDose**: Event that triggers rescheduling
- **RescheduleProposal**: AI's recommendation

## Getting Help

1. Check the code comments (heavily documented)
2. Read `README.md`
3. Look at example data in `rules/` and `data/`
4. Experiment!

## Deactivating Virtual Environment

When you're done:

```bash
deactivate
```

---

You're all set! Run `python main.py` and explore. 🚀