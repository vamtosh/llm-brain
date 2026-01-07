"""Stage management for interactive brainstorming workflow."""

from typing import Optional, Dict, Any, List
from enum import Enum


class Stage(str, Enum):
    """Brainstorming stages."""
    WIDEN = "widen"
    DIAGNOSE = "diagnose"
    CONVERGE = "converge"
    SELECT_SOLUTION = "select_solution"
    GENERATE_PRD = "generate_prd"
    COMPLETE = "complete"


class StageManager:
    """Manages stage progression and context."""

    STAGE_ORDER = [Stage.WIDEN, Stage.DIAGNOSE, Stage.CONVERGE, Stage.SELECT_SOLUTION, Stage.GENERATE_PRD, Stage.COMPLETE]

    # Stage-specific system prompts (optimized for GPT-5.1)
    STAGE_PROMPTS = {
        Stage.WIDEN: """Act as a deep research aide. Your goal is to comprehensively explore the problem space.

<task_requirements>
For the provided topic or challenge, you must analyze and deliver ALL of the following:
1. List key personas (stakeholders affected)
2. Identify top pains (specific problems each persona faces)
3. Document current workarounds (existing solutions)
4. Define success metrics (KPIs that indicate progress)
5. Provide 5 key insights (non-obvious observations tailored to the challenge)
6. Highlight 3 critical risks (obstacles that could impede progress)
</task_requirements>

<output_formatting>
Structure your response in Markdown with the following format:

## 1. PERSONAS
- [List 3-5 stakeholder personas, each in 15-30 words]

## 2. PAINS
- [List 5-8 specific pain points, each in 20-50 words describing the problem and its impact]

## 3. WORKAROUNDS
- [List 3-5 current solutions/workarounds, each in 15-40 words]

## 4. METRICS
- [List 4-6 KPIs with specific measurement criteria, each in 10-25 words]

## 5. INSIGHTS
- [Provide exactly 5 non-obvious insights, each 25-60 words, tailored to this challenge]

## 6. RISKS
- [Highlight exactly 3 critical risks, each 30-60 words describing the obstacle and potential impact]
</output_formatting>

<quality_standards>
- Be specific, concrete, and tailored to the challenge
- Avoid generic observations; provide actionable insights
- Use concrete examples where relevant
- Persist until the task is fully handled end-to-end within this turn
- Complete all 6 sections before finishing your response
</quality_standards>""",

        Stage.DIAGNOSE: """For the selected pain point, conduct a rigorous root cause analysis.

<task_requirements>
You must complete ALL of the following analysis steps:
1. Run a Five Whys analysis on the selected pain point
2. Propose exactly 3 root-cause hypotheses
3. For each hypothesis, provide comprehensive:
   - Supporting evidence
   - Disproof evidence (what would invalidate this hypothesis)
   - Minimum data cut needed to validate
   - Data owners who can provide this data
4. Synthesize into:
   - Root-cause map (text representation showing causal relationships)
   - Test plan (concrete validation steps)
   - Privacy constraints (specific data handling requirements)
</task_requirements>

<output_formatting>
Structure your response in Markdown with the following exact format:

## FIVE WHYS ANALYSIS
**Problem:** [Restate the pain point in 15-25 words]

1. **Why?** [First why - 20-40 words]
2. **Why?** [Second why - 20-40 words]
3. **Why?** [Third why - 20-40 words]
4. **Why?** [Fourth why - 20-40 words]
5. **Why?** [Root cause - 25-50 words]

## ROOT CAUSE HYPOTHESES

### Hypothesis 1: [Concise title, 5-10 words]
- **Supporting Evidence:** [2-4 bullet points, each 15-30 words]
- **Disproof Evidence:** [What would invalidate this - 20-40 words]
- **Data Required:** [Specific data needed - 15-30 words]
- **Data Owners:** [Who has this data - 10-20 words]
- **Likelihood:** [High/Medium/Low with brief justification - 15-25 words]

### Hypothesis 2: [Concise title, 5-10 words]
[Same structure as Hypothesis 1]

### Hypothesis 3: [Concise title, 5-10 words]
[Same structure as Hypothesis 1]

## ROOT CAUSE MAP
[Text representation showing causal relationships - 100-200 words total]

## VALIDATION TEST PLAN
1. [First test step - 25-40 words with success criteria]
2. [Second test step - 25-40 words with success criteria]
3. [Third test step - 25-40 words with success criteria]

## PRIVACY & DATA CONSTRAINTS
- [List 2-4 specific constraints, each 20-40 words]
</output_formatting>

<quality_standards>
- Be analytical, systematic, and evidence-based
- Provide concrete, testable hypotheses
- Ensure all evidence is specific and measurable
- Persist until all sections are complete before finishing
- Focus on actionable insights that can drive validation
</quality_standards>""",

        Stage.CONVERGE: """Generate and cluster AI-driven solution ideas for the diagnosed root causes.

<task_requirements>
You must generate and analyze solution options across ALL three categories:

1. **Process-Only** (Policy, ways of working)
   - No technology required
   - Organizational/process changes

2. **Analytics/ML** (Forecasting, optimization, recommendations)
   - Data-driven insights
   - Predictive/prescriptive analytics

3. **Automation** (Computer Vision, Generative AI, RAG/copilots, tasking)
   - AI-powered automation
   - GenAI applications

For each option, you must score on ALL four dimensions:
- Impact (1-10): Business value potential
- Feasibility (1-10): Technical and organizational viability
- Confidence (1-10): Certainty in estimates
- Time-to-Value (in months): Expected time to realize benefits
</task_requirements>

<output_formatting>
Structure your response in Markdown with the following exact format:

## 🔧 PROCESS & WORKFLOW OPTIONS

### Option 1: [Solution name, 5-10 words]
**Description:** [What it is and how it works - 40-80 words]
**Scores:** Impact: X/10 | Feasibility: X/10 | Confidence: X/10 | Time-to-Value: X months
**Key Benefits:** [2-3 bullet points, each 15-25 words]
**Key Challenges:** [2-3 bullet points, each 15-25 words]

[Repeat for 2-3 Process options]

## 📊 ANALYTICS & ML OPTIONS

### Option 1: [Solution name, 5-10 words]
[Same structure as Process options]

[Repeat for 2-3 Analytics/ML options]

## 🤖 AUTOMATION & AI OPTIONS

### Option 1: [Solution name, 5-10 words]
[Same structure as Process options]

[Repeat for 2-3 Automation options]

## ⭐ RECOMMENDED PILOT PROJECT

**Selected Option:** [Name and category]

**Why This Option:**
- Smallest integration surface: [Explain in 20-40 words]
- Clearest value proof: [Explain in 20-40 words]
- AI-assisted prototype potential: [Explain in 20-40 words]

**Implementation Plan:**
1. **Phase 1 (Weeks 1-2):** [Specific activities - 30-50 words]
2. **Phase 2 (Weeks 3-4):** [Specific activities - 30-50 words]
3. **Phase 3 (Weeks 5-8):** [Specific activities - 30-50 words]

**Success Metrics:**
- [Metric 1 with specific target - 15-25 words]
- [Metric 2 with specific target - 15-25 words]
- [Metric 3 with specific target - 15-25 words]

**Resource Requirements:**
- Team: [Specific roles needed - 15-30 words]
- Technology: [Specific tools/platforms - 15-30 words]
- Budget: [Rough estimate with breakdown - 20-40 words]
</output_formatting>

<quality_standards>
- Generate 6-9 total options (2-3 per category minimum)
- Ensure all scores are justified and realistic
- Make the pilot recommendation concrete and actionable
- Provide specific implementation details, not generic advice
- Persist until all sections are complete before finishing
- Focus on quick wins that demonstrate clear value
</quality_standards>""",

        Stage.SELECT_SOLUTION: """This is a transition stage - no AI generation needed.
The user will select from the solution options presented from the CONVERGE stage.
This stage is handled entirely by the frontend.""",

        Stage.GENERATE_PRD: """Act as a senior product manager creating a Product Requirements Document (PRD) for a prototype.

<task_requirements>
Based on the selected solution option and previous analysis, you must create a comprehensive PRD that includes:
1. Executive Summary (high-level overview)
2. Problem Statement (from diagnosis)
3. Solution Overview (from selected option)
4. Prototype Scope (MVP features only - what's in and out)
5. Success Metrics (measurable outcomes)
6. Implementation Timeline (4-8 weeks, broken into phases)
7. Required Resources (team, technology, budget)
8. Risk Mitigation (key risks and strategies)
</task_requirements>

<output_formatting>
Structure your response as a professional markdown document:

# Product Requirements Document: [Solution Name]

## Executive Summary
[150-250 words: What is being built, why, and expected impact]

## Problem Statement
**Root Cause Analysis:**
[Reference the 5-Why analysis and root cause hypotheses from DIAGNOSE stage - 100-150 words]

**Business Impact:**
[Quantify the problem's impact on the business - 50-100 words]

## Solution Overview
**Approach:**
[Describe the selected solution approach - 150-200 words]

**Key Differentiators:**
- [Differentiator 1 - 15-30 words]
- [Differentiator 2 - 15-30 words]
- [Differentiator 3 - 15-30 words]

## Prototype Scope

### In Scope (MVP Features)
**Core Features:**
1. [Feature 1 - 20-40 words describing functionality and value]
2. [Feature 2 - 20-40 words describing functionality and value]
3. [Feature 3 - 20-40 words describing functionality and value]
4. [Feature 4 - 20-40 words describing functionality and value]

**Technical Requirements:**
- [Requirement 1 - 15-25 words]
- [Requirement 2 - 15-25 words]
- [Requirement 3 - 15-25 words]

### Out of Scope (Future Phases)
- [Future feature 1 - 20-30 words explaining why it's deferred]
- [Future feature 2 - 20-30 words explaining why it's deferred]
- [Future feature 3 - 20-30 words explaining why it's deferred]

## Success Metrics

**Primary Metrics:**
1. [Metric name]: [Baseline] → [Target] ([Timeframe])
2. [Metric name]: [Baseline] → [Target] ([Timeframe])
3. [Metric name]: [Baseline] → [Target] ([Timeframe])

**Secondary Metrics:**
- [Metric name]: [Target]
- [Metric name]: [Target]

**Validation Criteria:**
- [Success criterion 1 - 20-30 words]
- [Success criterion 2 - 20-30 words]

## Implementation Timeline

**Phase 1: Foundation (Weeks 1-2)**
- [Activity 1 - 15-25 words]
- [Activity 2 - 15-25 words]
- [Activity 3 - 15-25 words]
- **Deliverable:** [What will be completed]

**Phase 2: Core Development (Weeks 3-5)**
- [Activity 1 - 15-25 words]
- [Activity 2 - 15-25 words]
- [Activity 3 - 15-25 words]
- **Deliverable:** [What will be completed]

**Phase 3: Testing & Refinement (Weeks 6-8)**
- [Activity 1 - 15-25 words]
- [Activity 2 - 15-25 words]
- [Activity 3 - 15-25 words]
- **Deliverable:** [What will be completed]

## Required Resources

**Team:**
- [Role 1]: [Responsibilities and time commitment - 20-40 words]
- [Role 2]: [Responsibilities and time commitment - 20-40 words]
- [Role 3]: [Responsibilities and time commitment - 20-40 words]

**Technology Stack:**
- [Category 1]: [Specific tools/platforms - 15-30 words]
- [Category 2]: [Specific tools/platforms - 15-30 words]
- [Category 3]: [Specific tools/platforms - 15-30 words]

**Budget Estimate:**
- Personnel: [Cost range]
- Technology/Tools: [Cost range]
- Infrastructure: [Cost range]
- **Total:** [Total cost range]

## Risk Mitigation

**Technical Risks:**
1. **[Risk name]**
   - Impact: [High/Medium/Low]
   - Probability: [High/Medium/Low]
   - Mitigation: [Strategy - 30-50 words]

2. **[Risk name]**
   - Impact: [High/Medium/Low]
   - Probability: [High/Medium/Low]
   - Mitigation: [Strategy - 30-50 words]

**Business Risks:**
1. **[Risk name]**
   - Impact: [High/Medium/Low]
   - Probability: [High/Medium/Low]
   - Mitigation: [Strategy - 30-50 words]

2. **[Risk name]**
   - Impact: [High/Medium/Low]
   - Probability: [High/Medium/Low]
   - Mitigation: [Strategy - 30-50 words]

## Appendix

**Assumptions:**
- [Assumption 1]
- [Assumption 2]
- [Assumption 3]

**Dependencies:**
- [Dependency 1]
- [Dependency 2]

**Open Questions:**
- [Question 1]
- [Question 2]
</output_formatting>

<quality_standards>
- Be specific and actionable - avoid generic statements
- Ensure all metrics have clear baselines and targets
- Make the timeline realistic for a prototype (4-8 weeks maximum)
- Focus on MVP - resist feature creep
- Provide concrete estimates, not ranges like "TBD"
- Ensure the PRD is self-contained and comprehensive
- Persist until all sections are complete before finishing
- Use professional product management language
</quality_standards>"""
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

        if from_stage == Stage.CONVERGE.value and to_stage == Stage.SELECT_SOLUTION.value:
            # No input required to ENTER select_solution stage
            # The selection happens AT the select_solution stage itself
            return {
                "required": False,
                "type": "none",
                "description": "Proceeding to solution selection"
            }

        if from_stage == Stage.SELECT_SOLUTION.value and to_stage == Stage.GENERATE_PRD.value:
            return {
                "required": True,
                "type": "solution_details",
                "description": "Generate PRD for the selected solution"
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

            elif stage == Stage.GENERATE_PRD.value:
                if "diagnose_output" in context:
                    context_section += f"""
## PROBLEM ANALYSIS (FROM DIAGNOSE STAGE):
{context['diagnose_output']}

"""
                if "selected_solution" in context:
                    solution = context['selected_solution']
                    context_section += f"""
## SELECTED SOLUTION:
**Name:** {solution.get('name', 'N/A')}
**Category:** {solution.get('category', 'N/A')}
**Description:** {solution.get('description', 'N/A')}

"""
                if "converge_output" in context:
                    context_section += f"""
## ALL SOLUTION OPTIONS (FROM CONVERGE STAGE):
{context['converge_output']}

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

        elif stage == Stage.SELECT_SOLUTION.value:
            # This stage doesn't need AI - just passing through converge output for frontend extraction
            if Stage.CONVERGE.value in previous_stages:
                context["converge_output"] = previous_stages[Stage.CONVERGE.value].get("output", "")

        elif stage == Stage.GENERATE_PRD.value:
            # PRD needs all previous context plus selected solution
            if Stage.WIDEN.value in previous_stages:
                context["widen_output"] = previous_stages[Stage.WIDEN.value].get("output", "")
            if Stage.DIAGNOSE.value in previous_stages:
                context["diagnose_output"] = previous_stages[Stage.DIAGNOSE.value].get("output", "")
            if Stage.CONVERGE.value in previous_stages:
                context["converge_output"] = previous_stages[Stage.CONVERGE.value].get("output", "")
            if user_selections and "selected_solution" in user_selections:
                context["selected_solution"] = user_selections["selected_solution"]

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

    @staticmethod
    def get_auto_prompt_for_stage(stage: str, context: Dict[str, Any]) -> str:
        """Get the automatic prompt to trigger when advancing to a new stage."""
        if stage == Stage.DIAGNOSE.value:
            pain_point = context.get('selected_pain_point', 'the selected pain point')
            return f"Analyze the following pain point using the 5-Why technique and provide root cause hypotheses: {pain_point}"

        elif stage == Stage.CONVERGE.value:
            return "Based on the problem analysis from the WIDEN and DIAGNOSE stages, generate comprehensive solution options across all three categories (Process, Analytics/ML, and Automation) with specific recommendations."

        elif stage == Stage.SELECT_SOLUTION.value:
            # This stage is purely frontend - no AI generation needed
            return "Please select a solution option to proceed."

        elif stage == Stage.GENERATE_PRD.value:
            solution_name = context.get('selected_solution', {}).get('name', 'the selected solution')
            return f"Generate a comprehensive Product Requirements Document (PRD) for implementing a prototype of: {solution_name}"

        else:
            return "Please provide your analysis for this stage."
