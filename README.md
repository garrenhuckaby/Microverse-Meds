# Med Scheduler

AI-enabled medication tracker with constraint-based rescheduling. When you miss a dose, the AI analyzes your medication schedule, constraints, and interactions to recommend the safest rescheduling option.

## 🎯 What It Does

- **Tracks medications** with complex scheduling requirements
- **Loads constraints** from drug interaction databases (OpenFDA)
- **Uses AI** (Google Gemini) to intelligently reschedule missed doses
- **Considers**:
  - Drug interactions
  - Food requirements (with/without food, empty stomach)
  - Timing constraints (minimum gaps between doses)
  - Other medications in your schedule

## 📁 Project Structure

```
med_scheduler/
├── rules/                  # Constraint definitions
│   ├── constraints.yaml    # Drug interactions and timing rules
│   ├── tags.yaml          # Medication categories
│   └── sources.yaml       # API configurations
├── engine/                # Core scheduling engine
│   ├── models.py          # Data structures
│   ├── api_client.py      # OpenFDA integration
│   ├── rule_loader.py     # YAML constraint parser
│   └── optimizer.py       # AI-powered rescheduling
├── data/
│   └── drugs.yaml         # Sample drug database
├── tests/
│   └── canonical_regimens/
├── main.py                # Demo application
└── requirements.txt       # Python dependencies
```

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR-USERNAME/med-scheduler.git
cd med-scheduler
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Get a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Click "Create API Key"
3. Copy your key

### 4. Set Your API Key

**Linux/Mac/Git Bash:**
```bash
export GEMINI_API_KEY='your-api-key-here'
```

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY='your-api-key-here'
```

**Windows Command Prompt:**
```cmd
set GEMINI_API_KEY=your-api-key-here
```

### 5. Run the Demo

```bash
python main.py
```

## 📖 Demo Scenarios

The demo shows three realistic scenarios:

1. **Missed morning thyroid medication** - Complex case with empty stomach requirement
2. **Late evening diabetes medication** - Should you take it now or skip?
3. **Slightly delayed blood pressure med** - Simple 1-hour delay

## 🔧 How It Works

### When You Miss a Dose:

1. **System identifies** the missed medication and current time
2. **Loads constraints** from YAML files (drug interactions, timing rules)
3. **AI analyzes**:
   - How late is the dose?
   - What other meds are scheduled today?
   - What are the interaction rules?
   - Food/timing requirements?
4. **AI recommends**:
   - Best time to take the missed dose
   - Whether to skip it
   - Any warnings or adjustments needed

### Example:

```
Missed: Levothyroxine at 6:00 AM (empty stomach required)
Now: 8:00 AM (you're eating breakfast)
Also scheduled: Metformin at 8:00 AM (with food)

AI Recommendation:
→ Take Levothyroxine now, wait 30 min before eating
→ Delay Metformin to 8:30 AM with breakfast
→ This maintains the 4-hour gap from calcium in your breakfast
```

## 🧪 Running Without AI (Rule-Based Fallback)

Don't have an API key yet? No problem! The system has a simple rule-based fallback:

```bash
python main.py
# Will use basic timing rules instead of AI
```

## 📝 Adding Your Own Medications

Edit `rules/constraints.yaml`:

```yaml
constraints:
  - type: drug_interaction
    drug_a: your_medication
    drug_b: another_medication
    min_gap: 4h
    description: "Your interaction rule here"
```

Edit `data/drugs.yaml` to add your medications.

## 🔍 Next Steps

1. **Try the demo** to see how it works
2. **Add your medications** to `data/drugs.yaml`
3. **Define constraints** in `rules/constraints.yaml`
4. **Integrate real APIs** - OpenFDA is already set up in `engine/api_client.py`
5. **Build a UI** - Web interface, mobile app, etc.

## 🛠️ For Developers

### Key Files:

- `engine/models.py` - Start here to understand the data structures
- `engine/optimizer.py` - See how AI makes rescheduling decisions
- `engine/api_client.py` - OpenFDA integration (can add RxNorm here)
- `rules/constraints.yaml` - Define your interaction rules

### Running Tests:

```bash
# Tests coming soon!
pytest tests/
```

### Architecture:

```
User Input (Missed Dose)
    ↓
Rule Loader (YAML constraints)
    ↓
AI Optimizer (Gemini API)
    ↓
Reschedule Proposal
```

## 🔐 API Keys & Security

- **Never commit API keys** to Git
- Use environment variables
- For production, use secrets management (AWS Secrets Manager, etc.)

## 📚 Resources

- [OpenFDA API Docs](https://open.fda.gov/apis/)
- [RxNorm API](https://rxnav.nlm.nih.gov/APIs.html)
- [Gemini API Docs](https://ai.google.dev/docs)

## 🤝 Contributing

This is a demo project showing AI-powered medication management. Feel free to:
- Add more drug databases
- Improve the AI prompts
- Build a web/mobile interface
- Add machine learning for adherence prediction

## ⚠️ Disclaimer

**This is a demo project for educational purposes.**

- Not a substitute for medical advice
- Always consult healthcare providers
- Verify AI recommendations with pharmacists
- Use at your own risk

## 📄 License

MIT License - See LICENSE file

## 🎓 Built By

An electrical engineer learning software development! 🔌→💻

---

**Questions?** Open an issue or check the code comments in each file.