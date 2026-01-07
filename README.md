# AI ThinkCanvas

A structured AI brainstorming tool that guides you through a 5-stage framework: **WIDEN → DIAGNOSE → CONVERGE → SELECT → PRD**. Built with GPT-5 reasoning models, PostgreSQL, and React.

## Features

- **5-Stage Structured Workflow**: Systematic problem-solving from exploration to PRD generation
- **GPT-5 Reasoning**: Transparent AI reasoning process with expandable reasoning display
- **PostgreSQL Backend**: Scalable database supporting 3000+ concurrent users
- **Interactive Stage Progression**: Auto-generation of stage content with user input at key transitions
- **Solution Selection**: Visual grid-based selection of solution options with scoring
- **PRD Generation**: Automatic Product Requirements Document creation for selected solutions

## How It Works

The system guides you through five stages:

1. **WIDEN** - Explore the problem space
   - Personas: Key stakeholders affected
   - Pains: Specific pain points (5-8 items)
   - Workarounds: Current solutions in use
   - Metrics: KPIs and success indicators
   - Insights: Non-obvious observations (5 items)
   - Risks: Critical obstacles (3 items)

2. **DIAGNOSE** - Root cause analysis
   - Select a pain point from WIDEN stage
   - 5-Why analysis to drill into root causes
   - Root cause hypotheses with evidence
   - Validation test plan
   - Privacy and data constraints

3. **CONVERGE** - Generate solution options
   - Process & Workflow options (2-3)
   - Analytics & ML options (2-3)
   - Automation & AI options (2-3)
   - Scoring: Impact, Feasibility, Confidence, Time-to-Value
   - Recommended pilot project with implementation plan

4. **SELECT** - Choose a solution
   - Visual grid of solution options
   - Filter by category and score
   - Custom solution input option
   - Select solution to prototype

5. **PRD** - Generate Product Requirements Document
   - Executive Summary
   - Problem Statement
   - Solution Overview
   - Prototype Scope (MVP features)
   - Success Metrics
   - Implementation Timeline (4-8 weeks)
   - Required Resources
   - Risk Mitigation

## Prerequisites

- **Python 3.10+** with [uv](https://docs.astral.sh/uv/) package manager
- **PostgreSQL 12+** (running locally or remote)
- **Node.js 18+** for frontend
- **OpenAI API Key** with access to GPT-5 models

## Setup

### 1. Install Dependencies

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

### 2. Set Up PostgreSQL Database

**Option A: Local PostgreSQL**
```bash
# Create database
createdb brainstorm_db

# Run schema
psql brainstorm_db < backend/database/schema.sql
```

**Option B: Remote PostgreSQL (e.g., AWS RDS, Heroku Postgres)**
- Create database on your PostgreSQL provider
- Note the connection string

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# OpenAI API Configuration
OPENAI_API_KEY=sk-your-actual-api-key-here

# Database Configuration
# Local PostgreSQL:
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/brainstorm_db

# Remote PostgreSQL (example):
# DATABASE_URL=postgresql://user:password@host:5432/brainstorm_db
```

**Get your OpenAI API key:** [OpenAI Platform](https://platform.openai.com/api-keys)

### 4. Configure Models (Optional)

Edit `backend/config.py` to customize:

```python
# Primary model for brainstorming
PRIMARY_MODEL = "gpt-5-mini"

# Reasoning effort for gpt-5 models (low, medium, high)
REASONING_EFFORT = "medium"
```

**Note:** GPT-5 models use the new reasoning API. Higher reasoning effort provides more thorough analysis but takes longer.

## Running the Application

### Development Mode

**Option 1: Use the start script**
```bash
chmod +x start.sh
./start.sh
```

**Option 2: Run manually**

Terminal 1 (Backend):
```bash
uv run python -m backend.main
```
- Backend runs on **http://localhost:8001**
- Auto-initializes database connection pool on startup

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```
- Frontend runs on **http://localhost:5173**
- Connects to backend at http://localhost:8001

Then open **http://localhost:5173** in your browser.

### Production Deployment

#### Backend Deployment

**Using uvicorn directly:**
```bash
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8001
```

**Using gunicorn (recommended for production):**
```bash
pip install gunicorn
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8001
```

**Environment variables for production:**
- Set `OPENAI_API_KEY` in your deployment environment
- Set `DATABASE_URL` to your production PostgreSQL connection string
- Configure CORS in `backend/main.py` to allow your frontend domain

#### Frontend Deployment

**Build for production:**
```bash
cd frontend
npm run build
```

**Preview production build:**
```bash
npm run preview
```

**Deploy static files:**
- The `frontend/dist/` directory contains the production build
- Deploy to any static hosting service (Vercel, Netlify, AWS S3, etc.)
- Update `frontend/src/api.js` to point to your production backend URL

**Example deployment platforms:**
- **Vercel**: Connect GitHub repo, set build command `cd frontend && npm run build`, output directory `frontend/dist`
- **Netlify**: Same configuration as Vercel
- **AWS S3 + CloudFront**: Upload `frontend/dist/` to S3 bucket, configure CloudFront distribution

#### Database Setup for Production

1. **Create production database** on your PostgreSQL provider
2. **Run schema:**
   ```bash
   psql $DATABASE_URL < backend/database/schema.sql
   ```
3. **Set DATABASE_URL** in your deployment environment

#### CORS Configuration

Update `backend/main.py` to allow your frontend domain:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Development
        "https://your-production-domain.com"  # Production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## Tech Stack

- **Backend:**
  - FastAPI (Python 3.10+)
  - PostgreSQL with asyncpg (async connection pooling)
  - OpenAI Python SDK (GPT-5 reasoning API)
  - Uvicorn ASGI server

- **Frontend:**
  - React 19 + Vite
  - react-markdown for rendering
  - Modern CSS with flexbox/grid

- **Package Management:**
  - uv for Python dependencies
  - npm for JavaScript dependencies

- **Storage:**
  - PostgreSQL database (not JSON files)
  - Tables: conversations, messages, stage_contexts, documents

## Project Structure

```
llm-brain/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── config.py             # Configuration (API keys, models)
│   ├── stage_manager.py      # Stage orchestration and prompts
│   ├── brainstorm.py         # Core message processing
│   ├── openai_client.py      # OpenAI API client
│   ├── database/
│   │   ├── client.py         # Database connection pool
│   │   ├── repositories.py   # Data access layer
│   │   └── schema.sql         # Database schema
│   └── solution_extractor.py # Solution parsing utilities
├── frontend/
│   ├── src/
│   │   ├── App.jsx           # Main application
│   │   ├── api.js            # API client
│   │   └── components/
│   │       ├── ChatInterface.jsx
│   │       ├── SolutionSelector.jsx
│   │       ├── PRDViewer.jsx
│   │       └── ...
│   └── package.json
├── .env                      # Environment variables (not in git)
├── pyproject.toml            # Python dependencies
└── README.md
```

## API Endpoints

- `GET /api/conversations` - List all conversations
- `POST /api/conversations` - Create new conversation
- `GET /api/conversations/{id}` - Get conversation with messages
- `POST /api/conversations/{id}/message` - Send message
- `GET /api/conversations/{id}/stage-status` - Get stage status
- `POST /api/conversations/{id}/advance-stage` - Advance to next stage
- `DELETE /api/conversations/{id}` - Delete conversation

## Troubleshooting

### Backend won't start
- Check PostgreSQL is running: `pg_isready`
- Verify `DATABASE_URL` in `.env` is correct
- Check port 8001 is available: `lsof -ti:8001`

### Frontend can't connect to backend
- Verify backend is running on port 8001
- Check CORS configuration in `backend/main.py`
- Verify API base URL in `frontend/src/api.js`

### Database errors
- Ensure database exists: `psql -l | grep brainstorm_db`
- Run schema: `psql brainstorm_db < backend/database/schema.sql`
- Check connection string format: `postgresql://user:pass@host:port/dbname`

### Solution Selector is empty
- Check browser console for extraction logs
- Verify CONVERGE stage output follows expected markdown format
- Ensure messages have `stage` field set correctly

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
