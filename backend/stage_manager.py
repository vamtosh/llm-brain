"""Stage management for interactive brainstorming workflow."""

from typing import Optional, Dict, Any, List
from enum import Enum


class Stage(str, Enum):
    """Brainstorming stages."""
    WIDEN = "widen"
    DIAGNOSE = "diagnose"
    CONVERGE = "converge"
    COMPLETE = "complete"


class StageManager:
    """Manages stage progression and context."""

    STAGE_ORDER = [Stage.WIDEN, Stage.DIAGNOSE, Stage.CONVERGE, Stage.COMPLETE]

    # Stage-specific system prompts (using user-provided prompts)
    STAGE_PROMPTS = {
        Stage.WIDEN: """Act as a deep research aide. Your goal is to comprehensively explore the problem space.

For the provided topic or challenge, you must:
1. List key personas (stakeholders affected)
2. Identify top pains (specific problems each persona faces)
3. Document current workarounds (existing solutions)
4. Define success metrics (KPIs that indicate progress)
5. Provide 5 key insights (non-obvious observations tailored to the challenge)
6. Highlight 3 critical risks (obstacles that could impede progress)

Be specific, concrete, and tailored to the challenge. Structure your response with clear sections for each category.""",

        Stage.DIAGNOSE: """For the selected pain point, conduct a rigorous root cause analysis.

Your tasks:
1. Run a Five Whys analysis on the selected pain point
2. Propose 3 root-cause hypotheses
3. For each hypothesis, provide:
   - Supporting evidence
   - Disproof evidence (what would invalidate this hypothesis)
   - Minimum data cut needed to validate
   - Data owners who can provide this data
4. Output:
   - Root-cause map (visual/text representation)
   - Test plan (how to validate hypotheses)
   - Privacy constraints (data handling considerations)

Be analytical and systematic.""",

        Stage.CONVERGE: """Generate and cluster AI-driven solution ideas for the diagnosed root causes.

Create 3 distinct option categories:

1. **Process-Only** (Policy, ways of working)
   - No technology required
   - Organizational/process changes

2. **Analytics/ML** (Forecasting, optimization, recommendations)
   - Data-driven insights
   - Predictive/prescriptive analytics

3. **Automation** (Computer Vision, Generative AI, RAG/copilots, tasking)
   - AI-powered automation
   - GenAI applications

For each option, score on:
- Impact (1-10)
- Feasibility (1-10)
- Confidence (1-10)
- Time-to-Value (in months)

**Final Recommendation:**
Identify ONE pilot project with:
- Smallest integration surface
- Clearest value proof
- Can be developed as a prototype using an AI assistant

Provide specific implementation details for the recommended pilot."""
    }

    @staticmethod
    def get_next_stage(current_stage: str) -> Optional[str]:
        """Get the next stage in the sequence."""
        try:
            current = Stage(current_stage)
            current_idx = StageManager.STAGE_ORDER.index(current)
            if current_idx < len(StageManager.STAGE_ORDER) - 1:
                return StageManager.STAGE_ORDER[current_idx + 1].value
            return None
        except (ValueError, IndexError):
            return None

    @staticmethod
    def can_advance(current_stage: str, stage_context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if we can advance from current stage."""
        if current_stage == Stage.COMPLETE.value:
            return False

        # For linear progression, we can always advance
        # In future, could add validation logic here
        return True

    @staticmethod
    def requires_user_input(from_stage: str, to_stage: str) -> Dict[str, Any]:
        """Check what user input is needed when advancing between stages."""
        if from_stage == Stage.WIDEN.value and to_stage == Stage.DIAGNOSE.value:
            return {
                "required": True,
                "type": "pain_point_selection",
                "description": "Select a pain point to diagnose from the WIDEN stage output"
            }

        if from_stage == Stage.DIAGNOSE.value and to_stage == Stage.CONVERGE.value:
            return {
                "required": False,
                "type": "optional_notes",
                "description": "Optional: Add any additional context before generating solutions"
            }

        return {"required": False}

    @staticmethod
    def get_system_prompt(stage: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Get the system prompt for a stage with context."""
        base_prompt = StageManager.STAGE_PROMPTS.get(Stage(stage), "")

        # Add context from previous stages
        context_section = ""
        if context:
            if stage == Stage.DIAGNOSE.value and "widen_output" in context:
                context_section = f"""
## CONTEXT FROM WIDEN STAGE:
{context['widen_output']}

## SELECTED PAIN POINT:
{context.get('selected_pain_point', 'Not specified - please select the most critical pain point from above')}

---
"""
            elif stage == Stage.CONVERGE.value:
                if "widen_output" in context:
                    context_section += f"""
## CONTEXT FROM WIDEN STAGE:
{context['widen_output']}

"""
                if "diagnose_output" in context:
                    context_section += f"""
## CONTEXT FROM DIAGNOSE STAGE:
{context['diagnose_output']}

"""
                if "additional_notes" in context:
                    context_section += f"""
## ADDITIONAL CONTEXT:
{context['additional_notes']}

"""
                context_section += "---\n"

        return context_section + base_prompt

    @staticmethod
    def build_context_for_stage(
        stage: str,
        previous_stages: Dict[str, Dict[str, Any]],
        user_selections: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build context object for a stage from previous stages."""
        context = {}

        if stage == Stage.DIAGNOSE.value:
            if Stage.WIDEN.value in previous_stages:
                context["widen_output"] = previous_stages[Stage.WIDEN.value].get("output", "")
            if user_selections and "selected_pain_point" in user_selections:
                context["selected_pain_point"] = user_selections["selected_pain_point"]

        elif stage == Stage.CONVERGE.value:
            if Stage.WIDEN.value in previous_stages:
                context["widen_output"] = previous_stages[Stage.WIDEN.value].get("output", "")
            if Stage.DIAGNOSE.value in previous_stages:
                context["diagnose_output"] = previous_stages[Stage.DIAGNOSE.value].get("output", "")
            if user_selections and "additional_notes" in user_selections:
                context["additional_notes"] = user_selections["additional_notes"]

        return context

    @staticmethod
    def validate_stage_transition(from_stage: str, to_stage: str) -> bool:
        """Validate that the stage transition is allowed (linear progression only)."""
        try:
            from_idx = StageManager.STAGE_ORDER.index(Stage(from_stage))
            to_idx = StageManager.STAGE_ORDER.index(Stage(to_stage))
            # Only allow moving forward one stage at a time
            return to_idx == from_idx + 1
        except (ValueError, IndexError):
            return False
