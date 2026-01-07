# CLAUDE.md - Technical Notes for Brainstorming Partner

This file contains technical details, architectural decisions, and important implementation notes for future development sessions.

## Project Overview

Brainstorming Partner is a structured AI brainstorming tool that uses OpenAI's GPT-5-mini API to guide users through a 3-stage framework: **WIDEN → DIAGNOSE → CONVERGE**. Unlike traditional chatbots, this tool provides a systematic approach to problem-solving with clear stages for exploration, diagnosis, and solution generation.

The application uses **PostgreSQL** for data persistence, supports **multi-user concurrent sessions**, and features **interactive stage progression** with auto-save and reasoning display.

## Architecture

### Backend Structure (`backend/`)

#### **`config.py`**
- Contains `OPENAI_API_KEY` (loaded from `.env` file via `python-dotenv`)
- Contains `PRIMARY_MODEL` (default: "gpt-5-mini")
- Contains `REASONING_EFFORT` (default: "medium" - can be "low", "medium", or "high")
- Contains `DATABASE_URL` (PostgreSQL connection string from `.env`)
- Backend runs on **port 8001** (NOT 8000)

#### **`openai_client.py`**
- `query_model()`: Single async model query using OpenAI's **responses API** for GPT-5 models
- Uses `client.responses.create()` instead of `client.chat.completions.create()`
- Includes `reasoning={"effort": "medium"}` parameter for GPT-5 reasoning models
- **Reasoning extraction**: Extracts reasoning summary from `response.output` array using **object property access** (`.type`, `.text`) NOT dictionary methods (`.get()`)
- Returns dict with:
  - `content`: Main response text from `response.output_text`
  - `reasoning`: Extracted reasoning summary combining summary_text items
- **CRITICAL**: OpenAI response objects use dot notation for properties, not dict methods

#### **`brainstorm.py`** - Core Processing Logic
- `process_stage_message()`: Main entry point for processing messages in any stage
- Takes stage name, user message, and context dictionary
- Calls `query_model()` with stage-specific prompt
- Returns dict with `content`, `reasoning`, and `metadata`
- `generate_conversation_title()`: Creates concise 5-7 word titles for brainstorming sessions

#### **`stage_manager.py`** - Stage Orchestration
Core stage management system with GPT-5.1 optimized prompts:

**Stage Definitions:**
- `Stage.WIDEN`: Explore problem space (personas, pains, workarounds, metrics, insights, risks)
- `Stage.DIAGNOSE`: 5-Why analysis and root cause hypotheses
- `Stage.CONVERGE`: Generate and cluster solution ideas

**Key Methods:**
- `get_next_stage(current_stage)`: Returns next stage in sequence (widen → diagnose → converge → complete)
- `can_advance(stage, context)`: Checks if stage has output and can advance
- `requires_user_input(from_stage, to_stage)`: Returns dict with `required`, `type`, `description` for stage transitions
  - WIDEN → DIAGNOSE: Requires pain point selection (`type: "pain_point_selection"`)
  - DIAGNOSE → CONVERGE: No input required
- `build_context_for_stage(stage, previous_stages, user_input)`: Builds context dict for new stage with references to previous outputs
- `get_auto_prompt_for_stage(stage, context)`: **NEW** - Generates automatic prompt when advancing to a stage
  - DIAGNOSE: Includes selected pain point in prompt
  - CONVERGE: References previous stage analysis

**Prompt Structure (GPT-5.1 Best Practices):**
All prompts use XML-style sections with explicit word counts:
- `<task_requirements>`: Enumerated list of required outputs
- `<output_formatting>`: Exact markdown structure with word counts per element
- `<quality_standards>`: Behavioral expectations and completion criteria

Example WIDEN prompt structure:
```markdown
## 1. PERSONAS
- [List 3-5 stakeholder personas, each in 15-30 words]

## 2. PAINS
- [List 5-8 specific pain points, each in 20-50 words describing the problem and its impact]

## 3. WORKAROUNDS
...
```

#### **`database/`** - PostgreSQL Data Layer

**`client.py`**
- Async PostgreSQL connection pool using `asyncpg`
- `init_db()`: Creates connection pool and initializes schema
- `close_db()`: Gracefully closes connection pool
- `get_db()`: Returns database pool instance

**`schema.sql`**
Defines three main tables:

1. **conversations**
   - `id` (UUID, primary key)
   - `created_at` (timestamp)
   - `title` (text, nullable - generated after first message)
   - `current_stage` (text, default: "widen")

2. **messages**
   - `id` (UUID, primary key)
   - `conversation_id` (UUID, foreign key)
   - `role` (text: "user" or "assistant")
   - `content` (text)
   - `stage` (text: which stage this message belongs to)
   - `reasoning` (text, nullable: GPT-5 reasoning summary)
   - `metadata` (JSONB, nullable)
   - `created_at` (timestamp)

3. **stage_contexts**
   - `id` (UUID, primary key)
   - `conversation_id` (UUID, foreign key)
   - `stage` (text)
   - `user_input` (JSONB: e.g., `{"selected_pain_point": "..."}`)
   - `output` (text: final output for this stage)
   - `is_complete` (boolean)
   - `created_at`, `updated_at` (timestamps)

**`repositories/`**
- `ConversationRepository`: CRUD operations for conversations
  - `create()`, `get(id)`, `list()`, `update_stage(id, stage)`, `update_title(id, title)`
- `MessageRepository`: Message operations
  - `create()`, `list(conversation_id)`, `list_by_stage(conversation_id, stage)`
- `StageContextRepository`: Stage context tracking
  - `create_or_update()`, `get(conversation_id, stage)`, `get_all(conversation_id)`, `mark_complete()`

#### **`main.py`** - FastAPI Application

**CORS Configuration:**
```python
allow_origins=["http://localhost:5173", "http://localhost:3000"]
```

**Key Endpoints:**

1. **GET `/api/conversations`** - List all conversations (metadata only)
2. **POST `/api/conversations`** - Create new conversation
3. **GET `/api/conversations/{id}`** - Get conversation with all messages
4. **POST `/api/conversations/{id}/message`** - Send message, get response
   - Request: `{"content": "user message"}`
   - Response: `{"content": "...", "reasoning": "...", "metadata": {...}}`
5. **GET `/api/conversations/{id}/stage-status`** - Get current stage status
   - Returns: `{"current_stage": "...", "next_stage": "...", "can_advance": bool, "requires_input": {...}}`
6. **POST `/api/conversations/{id}/advance-stage`** - Advance to next stage
   - Request: `{"user_input": {"selected_pain_point": "..."}}`
   - **Auto-generates** first response for new stage
   - Returns: `{"success": true, "current_stage": "...", "content": "...", "reasoning": "..."}`

**Auto-Generation Feature:**
When advancing stages, the endpoint:
1. Updates conversation's current_stage
2. Fetches all previous stage contexts
3. Builds context for new stage with user input
4. Generates auto-prompt using `StageManager.get_auto_prompt_for_stage()`
5. Calls `process_stage_message()` to generate output
6. Saves assistant response with content and reasoning
7. Returns new content to frontend for immediate display

### Frontend Structure (`frontend/src/`)

#### **`App.jsx`**
Main application orchestrator:

**State Management:**
- `conversations`: List of all conversation metadata
- `currentConversationId`: Currently selected conversation
- `currentConversation`: Full conversation object with messages
- `stageStatus`: Current stage status from backend
- `isLoading`: Message send in progress
- `isAdvancing`: Stage advancement in progress

**Key Functions:**
- `handleSendMessage(content)`: Sends user message, adds optimistic user message to UI, adds assistant response
- `handleAdvanceStage(userInput)`: Advances stage, receives auto-generated content, adds to UI, reloads conversation and stage status

#### **`components/ChatInterface.jsx`**
Main chat interface component:

**Features:**
- Multiline textarea (3 rows, resizable)
- Enter to send, Shift+Enter for new line
- **Expandable reasoning display**:
  - Click to expand/collapse reasoning
  - Shows last 3 lines when collapsed
  - Full reasoning when expanded
  - Visual indicator: ▶/▼ arrow
- Stage advancement UI
- Conditional rendering based on stage status

**Reasoning Display Code:**
```javascript
const [expandedReasoning, setExpandedReasoning] = useState(new Set());

const toggleReasoning = (index) => {
  const newExpanded = new Set(expandedReasoning);
  if (newExpanded.has(index)) {
    newExpanded.delete(index);
  } else {
    newExpanded.add(index);
  }
  setExpandedReasoning(newExpanded);
};
```

#### **`components/StageProgress.jsx`**
Compact stage progress indicator:

**Design:**
- Horizontal layout (icons and text side-by-side)
- Three stages: WIDEN, DIAGNOSE, CONVERGE
- Visual states: pending, active, complete
- Icons: 🔍 (widen), 🔬 (diagnose), ✨ (converge)
- Compact padding: 12px vertical (reduced from 24px)
- Small icons: 20px (reduced from 32px)

#### **`components/PainPointSelector.jsx`**
Interactive pain point selection for WIDEN → DIAGNOSE transition:

**Features:**
- Extracts pain points from WIDEN output using regex patterns
- Grid display of pain points (click to select)
- Custom pain point input option
- Shows selected pain point preview
- "Proceed to DIAGNOSE" button
- Debug warning if no pain points extracted

**Extraction Logic:**
Tries multiple regex patterns to find "## 2. PAINS" section:
1. `##?\s*(?:2\.\s*)?PAINS?\s*:?` - Standard markdown headers
2. `\*\*(?:2\.\s*)?PAINS?\*\*` - Bold formatting
3. Fallback patterns for various formats

**Scrolling:**
- Max height: 70vh for container
- Max height: 50vh for pain points grid
- Prevents viewport overflow

#### **`api.js`**
API client with base URL `http://localhost:8001`:
- `listConversations()`, `createConversation()`, `getConversation(id)`
- `sendMessage(id, content)`, `getStageStatus(id)`, `advanceStage(id, userInput)`

### Styling

**Theme:**
- Light mode only
- Primary color: `#4a90e2` (blue)
- Background: White with subtle gradients

**Button Consistency:**
All advancement buttons use unified styling:
- Padding: `14px 32px`
- Font: `15px`, weight `600`
- Color: `#4a90e2`
- Border radius: `8px`
- Hover: `translateY(-1px)` with increased shadow

**Markdown Rendering:**
- Global `.markdown-content` class in `index.css`
- 12px padding on all markdown content
- All ReactMarkdown components wrapped in `<div className="markdown-content">`

## Key Design Decisions

### 1. PostgreSQL Over JSON Storage
**Why:** Support for 3000+ concurrent users, ACID compliance, efficient queries, relational integrity

**Trade-offs:**
- More complex setup (requires PostgreSQL server)
- Better performance at scale
- Easier to implement features like search, analytics, multi-user

### 2. Linear Stage Progression
**Why:** Each stage builds on previous stage output
- Stage 2 (DIAGNOSE) requires pain point from Stage 1 (WIDEN)
- Stage 3 (CONVERGE) requires root cause analysis from Stage 2

**Implementation:**
- `StageManager.get_next_stage()` enforces sequence
- `can_advance()` checks if current stage has output
- Auto-generation ensures seamless transitions

### 3. GPT-5.1 Prompt Optimization
**Why:** More consistent, predictable, complete outputs

**Applied Best Practices:**
- XML-style labeled sections (`<task_requirements>`, `<output_formatting>`, `<quality_standards>`)
- Explicit length constraints (word counts for each element)
- Solution persistence instructions ("Persist until task fully handled end-to-end")
- Specific behavioral expectations

**Reference:** OpenAI Cookbook - GPT-5.1 Prompting Guide

### 4. Auto-Generation on Stage Advancement
**Why:** Prevent "empty stage syndrome" where users advance but see no content

**How It Works:**
1. User clicks "Proceed to DIAGNOSE"
2. Backend receives stage advancement request with user input (selected pain point)
3. Backend generates context-aware prompt automatically
4. Backend calls GPT-5 to generate DIAGNOSE output
5. Backend saves assistant message
6. Backend returns content to frontend
7. Frontend displays new content immediately

**User Experience:**
- Click button → immediately see new stage output
- No need to send another message to trigger generation
- Seamless flow through stages

### 5. Reasoning Display
**Why:** Transparency into AI thinking process, educational value

**Design:**
- Collapsed by default (shows last 3 lines with "...")
- Click to expand/collapse
- Visual indicator: 💭 icon + arrow
- Subtle styling: gray text, italic, left border

**Technical Note:**
Reasoning is extracted from OpenAI's `response.output` array, specifically from items where `type === 'reasoning'`, combining `summary_text` items.

### 6. Interactive Pain Point Selection
**Why:** User agency in choosing which problem to analyze deeply

**Design:**
- Visual grid of extracted pain points
- Click to select
- Option to enter custom pain point
- Clear preview of selection
- Prevents accidental advancement without selection

## Important Implementation Details

### Environment Setup

**Requirements:**
1. Python 3.10+ with `uv` package manager
2. PostgreSQL 12+ running on localhost:5432
3. Node.js 18+ for frontend

**Initial Setup:**
```bash
# 1. Install dependencies
uv sync

# 2. Create .env file (copy from .env.example)
cp .env.example .env

# 3. Edit .env and set:
OPENAI_API_KEY=sk-your-actual-api-key-here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/brainstorm_db

# 4. Initialize database (create database and run schema)
createdb brainstorm_db
psql brainstorm_db < backend/database/schema.sql

# 5. Start backend (from project root)
uv run python -m backend.main

# 6. Start frontend (in separate terminal)
cd frontend
npm install
npm run dev
```

### Running the Application

**Backend:**
```bash
# From project root
uv run python -m backend.main
```
- Runs on http://localhost:8001
- Requires `.env` file with OPENAI_API_KEY and DATABASE_URL
- Auto-initializes database connection pool on startup

**Frontend:**
```bash
# From frontend directory
npm run dev
```
- Runs on http://localhost:5173
- Connects to backend at http://localhost:8001

### OpenAI Response Object Handling

**CRITICAL:** OpenAI response objects are NOT dictionaries!

**Wrong (will crash):**
```python
item.get('type')  # AttributeError: 'ResponseReasoningItem' object has no attribute 'get'
summary_item.get('text', '')  # Same error
```

**Correct:**
```python
if hasattr(item, 'type') and item.type == 'reasoning':
    summary_parts = []
    for summary_item in item.summary:
        if hasattr(summary_item, 'type') and summary_item.type == 'summary_text':
            summary_parts.append(summary_item.text)
```

**Reasoning Extraction Flow:**
1. Check `response.output` array
2. Find item where `item.type == 'reasoning'`
3. Iterate through `item.summary`
4. Extract `summary_item.text` where `summary_item.type == 'summary_text'`
5. Join all summary text parts with newlines

### Database Connection

**Connection Pooling:**
```python
# backend/database/client.py
db_pool = await asyncpg.create_pool(
    DATABASE_URL,
    min_size=10,
    max_size=100,
    command_timeout=60
)
```

**Best Practices:**
- Always use `async with db_pool.acquire() as conn:` for queries
- Handle `asyncpg.exceptions.PostgresError` for database errors
- Use parameterized queries to prevent SQL injection
- JSONB columns for flexible metadata storage

### Stage Context Flow

**Example: WIDEN → DIAGNOSE transition**

1. User completes WIDEN stage (gets persona, pains, etc.)
2. Frontend shows "Complete WIDEN Stage & Continue" button
3. User clicks button → shows PainPointSelector
4. User selects pain point → clicks "Proceed to DIAGNOSE"
5. Frontend calls `api.advanceStage(id, {selected_pain_point: "..."})`
6. Backend:
   - Marks WIDEN stage as complete
   - Updates conversation.current_stage = "diagnose"
   - Creates stage_context for DIAGNOSE with user_input
   - Builds context: `{widen_output: "...", selected_pain_point: "..."}`
   - Generates auto-prompt: "Analyze the following pain point using 5-Why..."
   - Calls GPT-5 with DIAGNOSE prompt + context
   - Saves assistant message with reasoning
   - Returns content to frontend
7. Frontend displays DIAGNOSE output immediately

## Common Gotchas

1. **Module Import Errors**
   - ❌ `python backend/main.py`
   - ✅ `python -m backend.main` (from project root)
   - ✅ `uv run python -m backend.main`

2. **Missing API Key**
   - Error: "The api_key client option must be set"
   - Fix: Create `.env` file with `OPENAI_API_KEY=sk-...`

3. **Database Connection Errors**
   - Error: "could not connect to server"
   - Fix: Ensure PostgreSQL is running: `pg_isready`
   - Fix: Create database: `createdb brainstorm_db`
   - Fix: Run schema: `psql brainstorm_db < backend/database/schema.sql`

4. **CORS Errors**
   - Error: "Access-Control-Allow-Origin"
   - Fix: Ensure frontend origin matches `allow_origins` in `backend/main.py`

5. **Port Already in Use**
   - Error: "Address already in use"
   - Fix: Kill existing process: `lsof -ti:8001 | xargs kill`

6. **Pain Points Not Extracting**
   - Check browser console for extraction logs
   - Verify WIDEN output follows expected markdown format
   - Debug box shows first 500 chars of output
   - Regex patterns in `PainPointSelector.jsx` may need adjustment

7. **Reasoning Not Showing**
   - Verify `reasoning` field is returned from backend
   - Check `msg.reasoning` exists in ChatInterface
   - Ensure reasoning extraction logic uses object properties, not dict methods

8. **Stage Not Advancing**
   - Verify backend is running on port 8001
   - Check browser console for API errors
   - Verify `can_advance` is true in stage status
   - Check if user input is required but not provided

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INPUT                                │
│                 "Our supplier lead times vary"                   │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                     STAGE 1: WIDEN                               │
│  • Extract personas, pains, workarounds, metrics, insights, risks│
│  • GPT-5 with reasoning (medium effort)                          │
│  • Store in stage_contexts: {stage: "widen", output: "..."}     │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
                   [User selects pain point]
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 2: DIAGNOSE                              │
│  • Context: widen_output + selected_pain_point                   │
│  • 5-Why analysis on selected pain                               │
│  • Root cause hypotheses with evidence                           │
│  • Store in stage_contexts: {stage: "diagnose", output: "..."}  │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
                    [User advances stage]
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                   STAGE 3: CONVERGE                              │
│  • Context: widen_output + diagnose_output                       │
│  • Generate solution options (Process, Analytics, Automation)    │
│  • Score on impact/feasibility/confidence/time-to-value          │
│  • Recommend pilot project with implementation plan              │
│  • Store in stage_contexts: {stage: "converge", output: "..."}  │
└────────────────────────────┬────────────────────────────────────┘
                             ↓
                     [Stage: COMPLETE]
```

**Key Points:**
- All processing is **async** but **sequential** (not parallel)
- Each stage builds on previous stage output
- Auto-generation ensures smooth transitions
- Reasoning is captured at every stage
- Messages and contexts stored separately for flexibility

## API Response Formats

### Stage Status Response
```json
{
  "current_stage": "widen",
  "next_stage": "diagnose",
  "can_advance": true,
  "requires_input": {
    "required": true,
    "type": "pain_point_selection",
    "description": "Select a pain point from the WIDEN stage to analyze in depth"
  }
}
```

### Advance Stage Response
```json
{
  "success": true,
  "previous_stage": "widen",
  "current_stage": "diagnose",
  "message": "Advanced from widen to diagnose",
  "content": "## 5-WHY ANALYSIS...",
  "reasoning": "To effectively analyze this pain point...",
  "metadata": {
    "model": "gpt-5-mini",
    "timestamp": "2026-01-06T02:00:00Z"
  }
}
```

### Message Response
```json
{
  "content": "## 1. PERSONAS\n- Supply Chain Manager...",
  "reasoning": "Analyzing the challenge of variable supplier lead times...",
  "metadata": {
    "model": "gpt-5-mini",
    "stage": "widen"
  }
}
```

## Testing the Application

### Manual Testing Flow

1. **Create New Conversation**
   - Click "New Brainstorming Session"
   - Verify conversation appears in sidebar

2. **WIDEN Stage**
   - Enter challenge: "Our supplier lead times are unpredictable"
   - Send message
   - Verify output has 6 sections: Personas, Pains, Workarounds, Metrics, Insights, Risks
   - Verify reasoning is displayed (collapsed)
   - Click reasoning to expand/collapse

3. **Pain Point Selection**
   - Click "Complete WIDEN Stage & Continue"
   - Verify pain point selector appears
   - Verify extracted pain points in grid
   - Click a pain point to select
   - Verify "We'll analyze: ..." preview shows
   - Click "Proceed to DIAGNOSE"

4. **DIAGNOSE Stage**
   - Verify stage indicator updates to DIAGNOSE
   - Verify new output appears automatically (no need to send message)
   - Verify 5-Why analysis is shown
   - Verify root cause hypotheses with evidence
   - Verify reasoning is displayed

5. **CONVERGE Stage**
   - Click "Proceed to CONVERGE"
   - Verify stage indicator updates to CONVERGE
   - Verify solution options in 3 categories
   - Verify scoring (impact/feasibility/confidence/time)
   - Verify recommended pilot project

6. **Conversation Persistence**
   - Reload page
   - Select conversation from sidebar
   - Verify all messages and stage progress are restored

### Database Verification

```sql
-- Check conversations
SELECT id, title, current_stage, created_at FROM conversations;

-- Check messages for a conversation
SELECT role, stage, LEFT(content, 50) as content_preview, created_at
FROM messages
WHERE conversation_id = 'your-conversation-id'
ORDER BY created_at;

-- Check stage contexts
SELECT stage, is_complete, user_input, LEFT(output, 50) as output_preview
FROM stage_contexts
WHERE conversation_id = 'your-conversation-id';
```

## Future Enhancement Ideas

### Short-term
- [ ] Remove debug code from PainPointSelector once extraction is stable
- [ ] Add loading state during pain point extraction
- [ ] Improve error messages with actionable guidance
- [ ] Add conversation deletion feature
- [ ] Export conversation as Markdown/PDF

### Medium-term
- [ ] Streaming implementation for progressive output display
- [ ] Multi-model perspectives (use different models per stage)
- [ ] Visual mind mapping of WIDEN outputs
- [ ] Conversation search and filtering
- [ ] Stage-specific temperature tuning

### Long-term
- [ ] Collaborative brainstorming (multi-user sessions)
- [ ] Integration with project management tools (Jira, Linear)
- [ ] Templates for common brainstorming scenarios
- [ ] Analytics dashboard (usage patterns, popular topics)
- [ ] Custom prompt templates per stage
- [ ] Mobile-responsive design
- [ ] Dark mode theme

## Differences from Original AI ThinkCanvas

This codebase was transformed from the original AI ThinkCanvas project:

### What Changed
- ✅ **Storage**: JSON files → PostgreSQL database
- ✅ **API**: OpenRouter → OpenAI API (GPT-5-mini)
- ✅ **Workflow**: Parallel multi-model → Sequential single-model brainstorming
- ✅ **Prompts**: Generic → GPT-5.1 optimized with XML sections and word counts
- ✅ **UI**: Multi-model comparison → Linear stage progression
- ✅ **Stage Advancement**: Manual → Auto-generation with context awareness
- ✅ **Reasoning**: Hidden → Visible with expand/collapse
- ✅ **User Input**: Simple text → Interactive (pain point selection)
- ✅ **Data Model**: Flat messages → Structured (conversations, messages, stage_contexts)

### What Stayed
- ✅ Overall 3-stage structure (WIDEN → DIAGNOSE → CONVERGE)
- ✅ FastAPI backend architecture
- ✅ React frontend with Vite
- ✅ Markdown rendering for structured output
- ✅ Port configuration (backend: 8001, frontend: 5173)
- ✅ CORS setup for local development

### Key Architectural Improvements
1. **Scalability**: PostgreSQL supports 3000+ concurrent users vs JSON file locks
2. **Data Integrity**: ACID compliance, foreign keys, constraints
3. **Performance**: Indexed queries, connection pooling, async I/O
4. **Maintainability**: Clear separation (repositories, stage manager, prompts)
5. **User Experience**: Auto-generation, interactive selection, reasoning display
6. **Consistency**: GPT-5.1 prompt optimization for predictable outputs

## Troubleshooting Guide

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Check dependencies
uv sync

# Check .env file exists
cat .env

# Check PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep brainstorm_db

# Check port 8001 is free
lsof -ti:8001
```

### Frontend can't connect to backend
```bash
# Verify backend is running
curl http://localhost:8001/

# Check CORS configuration in backend/main.py
# Should include your frontend origin

# Check API base URL in frontend/src/api.js
# Should be http://localhost:8001
```

### Database errors
```bash
# Recreate database
dropdb brainstorm_db
createdb brainstorm_db
psql brainstorm_db < backend/database/schema.sql

# Check connection string in .env
# Format: postgresql://user:pass@host:port/dbname
```

### OpenAI API errors
```bash
# Verify API key is valid
# Check balance at platform.openai.com

# Check model availability
# GPT-5-mini requires API access

# Check rate limits
# Review OpenAI dashboard for usage
```

## Development Best Practices

### Backend Development
1. Always run from project root: `uv run python -m backend.main`
2. Use type hints for function parameters and return values
3. Handle database errors gracefully with try/except
4. Log important events (stage transitions, errors)
5. Use async/await consistently
6. Validate user input before database operations

### Frontend Development
1. Use functional components with hooks
2. Keep components small and focused
3. Extract reusable logic into custom hooks
4. Handle loading and error states explicitly
5. Use optimistic UI updates for better UX
6. Wrap markdown in `.markdown-content` for consistent styling

### Prompt Engineering
1. Follow GPT-5.1 best practices (XML sections, word counts)
2. Test prompts with various inputs
3. Be specific about output format
4. Include persistence instructions
5. Provide examples when helpful
6. Adjust reasoning effort based on task complexity

### Database Design
1. Use UUIDs for primary keys (better for distributed systems)
2. Add indexes on frequently queried columns
3. Use JSONB for flexible metadata
4. Set up foreign key constraints for referential integrity
5. Include timestamps (created_at, updated_at) for audit trail

---

**Last Updated:** 2026-01-06
**Current Version:** PostgreSQL + GPT-5-mini + Auto-generation + Interactive Stage Progression
