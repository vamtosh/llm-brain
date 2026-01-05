# CLAUDE.md - Technical Notes for Brainstorming Partner

This file contains technical details, architectural decisions, and important implementation notes for future development sessions.

## Project Overview

Brainstorming Partner is a structured AI brainstorming tool that uses OpenAI's API to guide users through a 3-stage framework: WIDEN → DIAGNOSE → CONVERGE. Unlike traditional chatbots, this tool provides a systematic approach to problem-solving with clear stages for exploration, diagnosis, and solution generation.

## Architecture

### Backend Structure (`backend/`)

**`config.py`**
- Contains `OPENAI_API_KEY` (from `.env` file)
- Contains `PRIMARY_MODEL` (default: "gpt-4o")
- Contains `BRAINSTORM_MODELS` (list of models for multi-perspective brainstorming)
- Backend runs on **port 8001** (NOT 8000)

**`openai_client.py`**
- `query_model()`: Single async model query using OpenAI SDK
- `query_models_parallel()`: Parallel queries using `asyncio.gather()`
- Returns dict with 'content' key
- Graceful degradation: returns None on failure

**`brainstorm.py`** - The Core Logic
- `stage1_widen()`: Surface personas, pains, workarounds, metrics, insights, risks
- `stage2_diagnose()`: Apply 5-Why technique and propose root cause hypotheses with evidence
- `stage3_converge()`: Generate and cluster ideas into Process, Analytics, ML/Automation, Other
- `run_full_brainstorm()`: Orchestrates all three stages sequentially
- `generate_conversation_title()`: Creates concise titles for brainstorming sessions

**`storage.py`**
- JSON-based conversation storage in `data/conversations/`
- Each conversation: `{id, created_at, messages[]}`
- Assistant messages contain: `{role, stage1, stage2, stage3}`
- Each stage is a dict with `{model, response}` structure

**`main.py`**
- FastAPI app with CORS enabled for localhost:5173 and localhost:3000
- POST `/api/conversations/{id}/message` returns all three stages
- POST `/api/conversations/{id}/message/stream` streams stages progressively
- Metadata includes model used and stages completed

### Frontend Structure (`frontend/src/`)

**`App.jsx`**
- Main orchestration: manages conversations list and current conversation
- Handles message sending with progressive streaming updates
- Maintains loading state for each stage independently

**`components/ChatInterface.jsx`**
- Multiline textarea (3 rows, resizable)
- Enter to send, Shift+Enter for new line
- User messages wrapped in markdown-content class
- Stage-specific loading indicators

**`components/Stage1.jsx`**
- Displays WIDEN output: personas, pains, workarounds, metrics, insights, risks
- ReactMarkdown rendering with markdown-content wrapper
- Simple single-panel view (no tabs needed)

**`components/Stage2.jsx`**
- Displays DIAGNOSE output: 5-Why analysis and root cause hypotheses
- Shows supporting/disproving evidence for each hypothesis
- ReactMarkdown rendering

**`components/Stage3.jsx`**
- Displays CONVERGE output: clustered solution ideas
- Shows categorized ideas with impact/effort assessment
- Green-tinted background (#f0fff0) for visual distinction

**Styling (`*.css`)**
- Light mode theme
- Primary color: #4a90e2 (blue)
- Global markdown styling in `index.css` with `.markdown-content` class
- 12px padding on all markdown content

## Key Design Decisions

### Stage 1: WIDEN Prompt Structure
The WIDEN stage systematically explores six dimensions:
1. Personas (stakeholders)
2. Pains (specific problems)
3. Workarounds (current solutions)
4. Metrics (measurable indicators)
5. Insights (patterns and observations)
6. Risks (obstacles and constraints)

This ensures comprehensive problem space exploration before diving into solutions.

### Stage 2: DIAGNOSE with 5-Why
The 5-Why technique forces deep analysis:
- Selects most critical pain point from Stage 1
- Iteratively asks "why" five times to uncover root causes
- Proposes 2-3 hypotheses with supporting/disproving evidence
- Assesses likelihood (High/Medium/Low) for each hypothesis

This prevents jumping to solutions before understanding the problem.

### Stage 3: CONVERGE with Clustering
Solution ideas are organized into four categories:
- 🔧 Process & Workflow
- 📊 Analytics & Insights
- 🤖 ML & Automation (including generative AI)
- 💡 Other Innovations

Each cluster includes impact/effort assessment and quick win identification.

### Sequential Stage Execution
Unlike the original council design (parallel execution), brainstorming stages are sequential:
- Stage 2 requires Stage 1 output as context
- Stage 3 requires both Stage 1 and Stage 2 outputs
- This enables progressive refinement and depth

### Error Handling Philosophy
- Each stage can fail independently without breaking the flow
- Error messages are user-friendly
- Graceful degradation when API calls fail

### UI/UX Transparency
- All stages visible in order
- Clear stage titles and descriptions
- Progressive loading indicators
- Markdown rendering for structured output

## Important Implementation Details

### Relative Imports
All backend modules use relative imports (e.g., `from .config import ...`). Run as `python -m backend.main` from project root.

### Port Configuration
- Backend: 8001
- Frontend: 5173 (Vite default)
- Update both `backend/main.py` and `frontend/src/api.js` if changing

### Markdown Rendering
All ReactMarkdown components must be wrapped in `<div className="markdown-content">` for proper spacing.

### Model Configuration
Models are configured in `backend/config.py`. The PRIMARY_MODEL is used for all three stages. BRAINSTORM_MODELS can be extended for multi-perspective brainstorming (future enhancement).

## Common Gotchas

1. **Module Import Errors**: Always run backend as `python -m backend.main` from project root
2. **CORS Issues**: Frontend must match allowed origins in `main.py` CORS middleware
3. **Missing OpenAI SDK**: Ensure `openai` package is installed via `uv sync`
4. **API Key**: Must be set in `.env` file as `OPENAI_API_KEY`

## Future Enhancement Ideas

- Multi-model perspectives (use BRAINSTORM_MODELS for diverse viewpoints)
- Export brainstorming sessions to structured formats (PDF, Markdown)
- Visual mind mapping of Stage 1 outputs
- Integration with project management tools
- Templates for common brainstorming scenarios
- Collaborative brainstorming (multi-user sessions)
- Stage-specific temperature tuning
- Custom prompt templates per stage

## Data Flow Summary

```
User Challenge
    ↓
Stage 1 (WIDEN): Explore problem space → personas, pains, workarounds, metrics, insights, risks
    ↓
Stage 2 (DIAGNOSE): 5-Why analysis → root cause hypotheses with evidence
    ↓
Stage 3 (CONVERGE): Generate ideas → cluster into categories → prioritize
    ↓
Return: {stage1, stage2, stage3, metadata}
    ↓
Frontend: Display progressively with clear stage separation
```

The entire flow is async but sequential (not parallel) to maintain context across stages.

## Differences from Original LLM Council

This codebase was transformed from the original LLM Council project:

**What Changed:**
- Replaced OpenRouter with OpenAI API
- Changed from parallel multi-model evaluation to sequential single-model brainstorming
- Removed anonymization and peer ranking logic
- Simplified data structures (no more label_to_model mappings)
- Updated all prompts to match brainstorming framework
- Redesigned UI for single-model workflow

**What Stayed:**
- Overall 3-stage structure
- FastAPI backend with streaming support
- React frontend with stage-based UI
- JSON storage system
- Markdown rendering approach
- Port configuration (8001/5173)
