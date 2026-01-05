"""3-stage Brainstorming orchestration."""

from typing import List, Dict, Any, Tuple, Optional
from .openai_client import query_model
from .config import PRIMARY_MODEL
from .stage_manager import StageManager


async def process_stage_message(
    stage: str,
    user_message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Process a user message within a specific stage.

    Args:
        stage: Current stage (widen, diagnose, converge)
        user_message: User's message/question
        context: Context from previous stages and user selections

    Returns:
        Dict with content, reasoning, and metadata
    """
    # Get stage-specific system prompt with context
    system_prompt = StageManager.get_system_prompt(stage, context)

    # Build messages for the model
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message}
    ]

    # Query the model
    response = await query_model(PRIMARY_MODEL, messages)

    if response is None:
        return {
            "content": f"Error: Unable to generate response for {stage} stage.",
            "reasoning": None,
            "metadata": {"error": True}
        }

    return {
        "content": response.get('content', ''),
        "reasoning": response.get('reasoning'),  # Will be populated when we add reasoning display
        "metadata": {
            "model": PRIMARY_MODEL,
            "stage": stage
        }
    }


async def stage1_widen(challenge: str) -> Dict[str, Any]:
    """
    Stage 1: WIDEN - Rapidly surface personas, pains, workarounds, metrics, insights, and risks.

    Args:
        challenge: The user's challenge or problem statement

    Returns:
        Dict with structured exploration of the problem space
    """
    widen_prompt = f"""You are a strategic brainstorming partner helping to explore a challenge comprehensively.

CHALLENGE: {challenge}

Your task is to WIDEN the problem space by systematically surfacing:

1. **PERSONAS**: Who are the key stakeholders affected by this challenge? (e.g., end-users, decision-makers, technical teams, customers)

2. **PAINS**: What are the specific pain points, frustrations, or problems that each persona experiences?

3. **WORKAROUNDS**: What current workarounds or makeshift solutions are people using? What does this reveal about their needs?

4. **METRICS**: What metrics or KPIs would indicate success or failure in addressing this challenge? What can be measured?

5. **INSIGHTS**: What underlying patterns, trends, or non-obvious observations can you identify about this challenge?

6. **RISKS**: What are the potential risks, constraints, or obstacles that could impede progress?

Please structure your response with clear sections for each category above. Be specific and concrete. Aim for breadth and diversity of perspectives."""

    messages = [{"role": "user", "content": widen_prompt}]

    response = await query_model(PRIMARY_MODEL, messages)

    if response is None:
        return {
            "model": PRIMARY_MODEL,
            "response": "Error: Unable to generate WIDEN analysis."
        }

    return {
        "model": PRIMARY_MODEL,
        "response": response.get('content', '')
    }


async def stage2_diagnose(challenge: str, widen_output: str) -> Dict[str, Any]:
    """
    Stage 2: DIAGNOSE - Drill into a pain point using 5-Why technique and propose root cause hypotheses.

    Args:
        challenge: The original challenge
        widen_output: Output from Stage 1

    Returns:
        Dict with diagnostic analysis and root cause hypotheses
    """
    diagnose_prompt = f"""You are a strategic brainstorming partner helping to diagnose root causes of a challenge.

ORIGINAL CHALLENGE: {challenge}

STAGE 1 EXPLORATION:
{widen_output}

Your task is to DIAGNOSE the challenge by drilling deeper:

## Part 1: Select a Key Pain Point
From the Stage 1 exploration, identify the MOST CRITICAL pain point that deserves deeper investigation. Explain why you chose this one.

## Part 2: 5-Why Analysis
Apply the 5-Why technique to drill into this pain point:
- Why #1: [Ask why this pain point exists]
- Why #2: [Ask why the answer to #1 is true]
- Why #3: [Ask why the answer to #2 is true]
- Why #4: [Ask why the answer to #3 is true]
- Why #5: [Ask why the answer to #4 is true]

## Part 3: Root Cause Hypotheses
Based on your 5-Why analysis, propose 2-3 ROOT CAUSE HYPOTHESES. For each hypothesis:

**Hypothesis [N]**: [State the hypothesis clearly]
- **Supporting Evidence**: What evidence or observations support this hypothesis?
- **Disproving Evidence**: What evidence or observations would disprove or weaken this hypothesis?
- **Likelihood**: High/Medium/Low and why

Be analytical and critical. Look for systemic issues, not just surface symptoms."""

    messages = [{"role": "user", "content": diagnose_prompt}]

    response = await query_model(PRIMARY_MODEL, messages)

    if response is None:
        return {
            "model": PRIMARY_MODEL,
            "response": "Error: Unable to generate DIAGNOSE analysis."
        }

    return {
        "model": PRIMARY_MODEL,
        "response": response.get('content', '')
    }


async def stage3_converge(
    challenge: str,
    widen_output: str,
    diagnose_output: str
) -> Dict[str, Any]:
    """
    Stage 3: CONVERGE - Generate and cluster ideas into actionable categories.

    Args:
        challenge: The original challenge
        widen_output: Output from Stage 1
        diagnose_output: Output from Stage 2

    Returns:
        Dict with clustered solution ideas
    """
    converge_prompt = f"""You are a strategic brainstorming partner helping to generate and organize solutions.

ORIGINAL CHALLENGE: {challenge}

STAGE 1 (WIDEN):
{widen_output}

STAGE 2 (DIAGNOSE):
{diagnose_output}

Your task is to CONVERGE on actionable solutions:

## Part 1: Generate Ideas
Brainstorm 10-15 diverse solution ideas that address the challenge. Consider:
- Quick wins vs. long-term solutions
- Low-cost vs. high-investment approaches
- Incremental improvements vs. transformative changes
- Technical, process, and organizational solutions

## Part 2: Cluster Ideas
Organize these ideas into the following categories:

### 🔧 PROCESS & WORKFLOW
Ideas that improve processes, workflows, or operational efficiency

### 📊 ANALYTICS & INSIGHTS
Ideas that leverage data, analytics, or measurement

### 🤖 ML & AUTOMATION
Ideas that use machine learning, AI, or generative AI techniques

### 💡 OTHER INNOVATIONS
Ideas that don't fit the above categories but offer value

## Part 3: Prioritization Framework
For each cluster, suggest:
- **Impact**: Potential impact (High/Medium/Low)
- **Effort**: Required effort (High/Medium/Low)
- **Quick Wins**: Which 2-3 ideas could be implemented quickly?

Be creative and specific. Think about practical implementation."""

    messages = [{"role": "user", "content": converge_prompt}]

    response = await query_model(PRIMARY_MODEL, messages)

    if response is None:
        return {
            "model": PRIMARY_MODEL,
            "response": "Error: Unable to generate CONVERGE analysis."
        }

    return {
        "model": PRIMARY_MODEL,
        "response": response.get('content', '')
    }


async def generate_conversation_title(challenge: str) -> str:
    """
    Generate a short title for a brainstorming session.

    Args:
        challenge: The brainstorming challenge

    Returns:
        A short title (3-5 words)
    """
    title_prompt = f"""Generate a very short title (3-5 words maximum) that summarizes the following brainstorming challenge.
The title should be concise and descriptive. Do not use quotes or punctuation in the title.

Challenge: {challenge}

Title:"""

    messages = [{"role": "user", "content": title_prompt}]

    response = await query_model(PRIMARY_MODEL, messages, timeout=30.0)

    if response is None:
        return "New Brainstorm"

    title = response.get('content', 'New Brainstorm').strip()

    # Clean up the title - remove quotes, limit length
    title = title.strip('"\'')

    # Truncate if too long
    if len(title) > 50:
        title = title[:47] + "..."

    return title


async def run_full_brainstorm(challenge: str) -> Tuple[Dict, Dict, Dict, Dict]:
    """
    Run the complete 3-stage brainstorming process.

    Args:
        challenge: The user's challenge or problem statement

    Returns:
        Tuple of (stage1_result, stage2_result, stage3_result, metadata)
    """
    # Stage 1: WIDEN
    stage1_result = await stage1_widen(challenge)

    if "Error" in stage1_result.get("response", ""):
        return stage1_result, {}, {}, {}

    # Stage 2: DIAGNOSE
    stage2_result = await stage2_diagnose(
        challenge,
        stage1_result.get("response", "")
    )

    # Stage 3: CONVERGE
    stage3_result = await stage3_converge(
        challenge,
        stage1_result.get("response", ""),
        stage2_result.get("response", "")
    )

    # Metadata (can be extended with analytics in the future)
    metadata = {
        "model": PRIMARY_MODEL,
        "stages_completed": ["widen", "diagnose", "converge"]
    }

    return stage1_result, stage2_result, stage3_result, metadata
