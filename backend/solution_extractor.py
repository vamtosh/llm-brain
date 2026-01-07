"""Utility to extract and rank solution options from CONVERGE stage output."""

import re
from typing import List, Dict, Any, Optional


def extract_solution_options(converge_output: str) -> List[Dict[str, Any]]:
    """
    Extract solution options from CONVERGE stage markdown output.

    Returns top 5 scored options plus the recommended pilot project.

    Args:
        converge_output: Markdown text from CONVERGE stage

    Returns:
        List of solution dicts with name, category, description, scores
    """
    solutions = []

    # Extract all solution options from the three categories
    categories = {
        "Process & Workflow": r"##\s*🔧\s*PROCESS\s*&\s*WORKFLOW\s*OPTIONS?([\s\S]*?)(?=##\s*📊|##\s*🤖|$)",
        "Analytics & ML": r"##\s*📊\s*ANALYTICS\s*&\s*ML\s*OPTIONS?([\s\S]*?)(?=##\s*🤖|##\s*⭐|$)",
        "Automation & AI": r"##\s*🤖\s*AUTOMATION\s*&\s*AI\s*OPTIONS?([\s\S]*?)(?=##\s*⭐|$)"
    }

    for category, pattern in categories.items():
        match = re.search(pattern, converge_output, re.IGNORECASE)
        if match:
            category_text = match.group(1)
            solutions.extend(_parse_category_solutions(category_text, category))

    # Extract recommended pilot project
    recommended = _extract_recommended_pilot(converge_output)

    # Score and rank solutions
    scored_solutions = []
    for sol in solutions:
        sol['composite_score'] = _calculate_composite_score(sol)
        scored_solutions.append(sol)

    # Sort by composite score
    scored_solutions.sort(key=lambda x: x['composite_score'], reverse=True)

    # Get top 5
    top_5 = scored_solutions[:5]

    # Ensure recommended pilot is included
    if recommended:
        recommended['is_recommended'] = True
        # Check if recommended is already in top 5
        recommended_in_top5 = any(
            s.get('name', '').lower() == recommended.get('name', '').lower()
            for s in top_5
        )

        if not recommended_in_top5:
            # Replace the lowest scored item with recommended
            top_5[-1] = recommended
        else:
            # Mark the existing item as recommended
            for sol in top_5:
                if sol.get('name', '').lower() == recommended.get('name', '').lower():
                    sol['is_recommended'] = True

    return top_5


def _parse_category_solutions(category_text: str, category: str) -> List[Dict[str, Any]]:
    """Parse solutions from a category section."""
    solutions = []

    # Pattern to match option sections
    option_pattern = r'###\s*Option\s*\d+:\s*([^\n]+)\s*\n([\s\S]*?)(?=###\s*Option|\Z)'

    matches = re.finditer(option_pattern, category_text, re.MULTILINE)

    for match in matches:
        name = match.group(1).strip()
        content = match.group(2)

        # Extract description
        desc_match = re.search(r'\*\*Description:\*\*\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)', content)
        description = desc_match.group(1).strip() if desc_match else ""

        # Extract scores
        scores_match = re.search(
            r'\*\*Scores:\*\*\s*Impact:\s*(\d+)/10\s*\|\s*Feasibility:\s*(\d+)/10\s*\|\s*Confidence:\s*(\d+)/10\s*\|\s*Time-to-Value:\s*(\d+)\s*months?',
            content
        )

        impact = int(scores_match.group(1)) if scores_match else 5
        feasibility = int(scores_match.group(2)) if scores_match else 5
        confidence = int(scores_match.group(3)) if scores_match else 5
        time_to_value = int(scores_match.group(4)) if scores_match else 6

        solutions.append({
            'name': name,
            'category': category,
            'description': description,
            'impact': impact,
            'feasibility': feasibility,
            'confidence': confidence,
            'time_to_value': time_to_value
        })

    return solutions


def _extract_recommended_pilot(converge_output: str) -> Optional[Dict[str, Any]]:
    """Extract the recommended pilot project."""
    # Pattern to find recommended pilot section
    recommended_pattern = r'##\s*⭐\s*RECOMMENDED\s*PILOT\s*PROJECT([\s\S]*?)(?=##\s*|$)'

    match = re.search(recommended_pattern, converge_output, re.IGNORECASE)
    if not match:
        return None

    recommended_text = match.group(1)

    # Extract selected option name
    name_match = re.search(r'\*\*Selected\s*Option:\*\*\s*([^\n]+)', recommended_text)
    if not name_match:
        return None

    name_and_category = name_match.group(1).strip()

    # Try to extract just the name (remove category if present)
    name = re.sub(r'\s*\([^)]+\)\s*$', '', name_and_category).strip()

    # Extract category if present
    category_match = re.search(r'\(([^)]+)\)', name_and_category)
    category = category_match.group(1).strip() if category_match else "Recommended"

    # Extract why this option section
    why_match = re.search(r'\*\*Why\s*This\s*Option:\*\*([\s\S]*?)(?=\*\*Implementation|$)', recommended_text)
    description = why_match.group(1).strip() if why_match else ""

    # Set high scores for recommended option
    return {
        'name': name,
        'category': category,
        'description': description,
        'impact': 9,
        'feasibility': 8,
        'confidence': 9,
        'time_to_value': 2,
        'is_recommended': True
    }


def _calculate_composite_score(solution: Dict[str, Any]) -> float:
    """
    Calculate composite score for ranking.

    Formula: (Impact * 0.4) + (Feasibility * 0.3) + (Confidence * 0.2) + (TimeScore * 0.1)
    Where TimeScore = (12 - time_to_value) to favor shorter time
    """
    impact = solution.get('impact', 5)
    feasibility = solution.get('feasibility', 5)
    confidence = solution.get('confidence', 5)
    time_to_value = solution.get('time_to_value', 6)

    # Normalize time to favor shorter durations (max 12 months)
    time_score = max(0, 12 - time_to_value)

    composite = (
        impact * 0.4 +
        feasibility * 0.3 +
        confidence * 0.2 +
        time_score * 0.1
    )

    return round(composite, 2)
