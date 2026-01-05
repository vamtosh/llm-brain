# Brainstorming Partner

A structured AI brainstorming tool that helps you explore challenges using a 3-stage framework: WIDEN → DIAGNOSE → CONVERGE.

## How It Works

When you submit a challenge or problem, the system guides you through three stages:

1. **Stage 1: WIDEN** - Rapidly surface the problem space
   - Personas: Who are the key stakeholders?
   - Pains: What specific pain points exist?
   - Workarounds: What makeshift solutions are people using?
   - Metrics: What can be measured?
   - Insights: What non-obvious patterns exist?
   - Risks: What obstacles could impede progress?

2. **Stage 2: DIAGNOSE** - Drill into root causes
   - Select the most critical pain point
   - Apply 5-Why technique to uncover root causes
   - Propose root cause hypotheses
   - Identify supporting and disproving evidence
   - Assess likelihood of each hypothesis

3. **Stage 3: CONVERGE** - Generate and cluster solutions
   - Generate 10-15 diverse solution ideas
   - Cluster into categories:
     - 🔧 Process & Workflow
     - 📊 Analytics & Insights
     - 🤖 ML & Automation (including generative AI)
     - 💡 Other Innovations
   - Prioritize by impact and effort
   - Identify quick wins

## Setup

### 1. Install Dependencies

The project uses [uv](https://docs.astral.sh/uv/) for Python package management.

**Backend:**
```bash
uv sync
```

**Frontend:**
```bash
cd frontend
npm install
cd ..
```

### 2. Configure API Key

Create a `.env` file in the project root:

```bash
OPENAI_API_KEY=sk-...
```

Get your API key from [OpenAI Platform](https://platform.openai.com/api-keys).

### 3. Configure Models (Optional)

Edit `backend/config.py` to customize the models:

```python
# Primary model for brainstorming
PRIMARY_MODEL = "gpt-4o"

# Alternative models for multi-perspective brainstorming
BRAINSTORM_MODELS = [
    "gpt-4o",
    "gpt-4o-mini",
]
```

## Running the Application

**Option 1: Use the start script**
```bash
./start.sh
```

**Option 2: Run manually**

Terminal 1 (Backend):
```bash
uv run python -m backend.main
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

## Tech Stack

- **Backend:** FastAPI (Python 3.10+), OpenAI Python SDK
- **Frontend:** React + Vite, react-markdown for rendering
- **Storage:** JSON files in `data/conversations/`
- **Package Management:** uv for Python, npm for JavaScript

## Brainstorming Framework

This tool implements a structured approach to problem-solving:

- **WIDEN**: Divergent thinking to explore the full problem space
- **DIAGNOSE**: Convergent analysis to identify root causes
- **CONVERGE**: Ideation and categorization of solutions

The framework is particularly useful for product challenges, technical problems, and strategic planning.
