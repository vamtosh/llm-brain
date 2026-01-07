import { useState, useEffect } from 'react';
import './SolutionSelector.css';

export default function SolutionSelector({ convergeOutput, onAdvance }) {
  const [solutions, setSolutions] = useState([]);
  const [selectedSolution, setSelectedSolution] = useState(null);
  const [customSolution, setCustomSolution] = useState({ name: '', description: '' });
  const [useCustom, setUseCustom] = useState(false);

  useEffect(() => {
    // Extract solutions from CONVERGE output
    const extracted = extractSolutions(convergeOutput);
    setSolutions(extracted);
  }, [convergeOutput]);

  const handleAdvance = () => {
    const solution = useCustom ? customSolution : selectedSolution;
    if (solution && solution.name && solution.description) {
      onAdvance({
        selected_solution: {
          name: solution.name,
          category: solution.category || 'Custom',
          description: solution.description,
          impact: solution.impact || 8,
          feasibility: solution.feasibility || 8,
          confidence: solution.confidence || 8,
          time_to_value: solution.time_to_value || 6
        }
      });
    }
  };

  const extractSolutions = (text) => {
    if (!text) {
      console.log('SolutionSelector: No convergeOutput text provided');
      return [];
    }

    console.log('SolutionSelector: Parsing convergeOutput, length:', text.length);
    console.log('SolutionSelector: First 500 chars:', text.substring(0, 500));

    const solutions = [];

    // More flexible category patterns (handle variations in GPT output)
    const categories = [
      { 
        name: 'Process & Workflow', 
        emoji: '🔧', 
        patterns: [
          /##\s*🔧?\s*PROCESS\s*[&and]+\s*WORKFLOW\s*OPTIONS?([\s\S]*?)(?=##\s*📊|##\s*🤖|##\s*⭐|$)/i,
          /##\s*Process\s*[&and]+\s*Workflow\s*Options?([\s\S]*?)(?=##\s*Analytics|##\s*Automation|##\s*⭐|$)/i
        ]
      },
      { 
        name: 'Analytics & ML', 
        emoji: '📊', 
        patterns: [
          /##\s*📊?\s*ANALYTICS\s*[&and]+\s*ML\s*OPTIONS?([\s\S]*?)(?=##\s*🤖|##\s*⭐|$)/i,
          /##\s*Analytics\s*[&and]+\s*ML\s*Options?([\s\S]*?)(?=##\s*Automation|##\s*⭐|$)/i
        ]
      },
      { 
        name: 'Automation & AI', 
        emoji: '🤖', 
        patterns: [
          /##\s*🤖?\s*AUTOMATION\s*[&and]+\s*AI\s*OPTIONS?([\s\S]*?)(?=##\s*⭐|$)/i,
          /##\s*Automation\s*[&and]+\s*AI\s*Options?([\s\S]*?)(?=##\s*⭐|##\s*Recommended|$)/i
        ]
      }
    ];

    categories.forEach(({ name: catName, emoji, patterns }) => {
      let categoryText = null;
      
      // Try each pattern until one matches
      for (const pattern of patterns) {
        const match = text.match(pattern);
        if (match) {
          categoryText = match[1];
          console.log(`SolutionSelector: Found ${catName} section, length:`, categoryText.length);
          break;
        }
      }
      
      if (categoryText) {
        // Fixed: Use $ instead of \Z (Python regex) for end of string in JavaScript
        // Also made pattern more flexible to handle variations
        const optionPattern = /###\s*Option\s*\d+[:\.]?\s*([^\n]+)\s*\n([\s\S]*?)(?=###\s*Option|$)/gi;
        let optionMatch;

        while ((optionMatch = optionPattern.exec(categoryText)) !== null) {
          const name = optionMatch[1].trim();
          const content = optionMatch[2];

          // More flexible description extraction
          let description = '';
          const descMatch = content.match(/\*\*Description:?\*\*\s*([^\n]+(?:\n(?!\*\*)[^\n]+)*)/i);
          if (descMatch) {
            description = descMatch[1].trim();
          } else {
            // Fallback: take first paragraph after the name
            const firstParagraph = content.split('\n').find(line => line.trim() && !line.startsWith('**') && !line.startsWith('*'));
            if (firstParagraph) description = firstParagraph.trim();
          }

          // More flexible scores extraction - handle various formats
          let impact = 5, feasibility = 5, confidence = 5, time_to_value = 6;
          
          // Try standard format first
          const scoresMatch = content.match(
            /\*\*Scores:?\*\*[:\s]*Impact:?\s*(\d+)\/10\s*\|?\s*Feasibility:?\s*(\d+)\/10\s*\|?\s*Confidence:?\s*(\d+)\/10\s*\|?\s*Time[- ]?to[- ]?Value:?\s*(\d+)\s*months?/i
          );
          
          if (scoresMatch) {
            impact = parseInt(scoresMatch[1]);
            feasibility = parseInt(scoresMatch[2]);
            confidence = parseInt(scoresMatch[3]);
            time_to_value = parseInt(scoresMatch[4]);
          } else {
            // Fallback: try to extract individual scores
            const impactMatch = content.match(/Impact:?\s*(\d+)(?:\/10)?/i);
            const feasibilityMatch = content.match(/Feasibility:?\s*(\d+)(?:\/10)?/i);
            const confidenceMatch = content.match(/Confidence:?\s*(\d+)(?:\/10)?/i);
            const timeMatch = content.match(/Time[- ]?to[- ]?Value:?\s*(\d+)\s*months?/i);
            
            if (impactMatch) impact = parseInt(impactMatch[1]);
            if (feasibilityMatch) feasibility = parseInt(feasibilityMatch[1]);
            if (confidenceMatch) confidence = parseInt(confidenceMatch[1]);
            if (timeMatch) time_to_value = parseInt(timeMatch[1]);
          }

          const compositeScore = impact * 0.4 + feasibility * 0.3 + confidence * 0.2 + Math.max(0, 12 - time_to_value) * 0.1;

          solutions.push({
            name,
            category: catName,
            categoryEmoji: emoji,
            description,
            impact,
            feasibility,
            confidence,
            time_to_value,
            compositeScore
          });
          
          console.log(`SolutionSelector: Extracted option "${name}" from ${catName}`);
        }
      }
    });

    console.log(`SolutionSelector: Total solutions extracted from categories: ${solutions.length}`);

    // Extract recommended pilot - more flexible pattern
    const recommendedPatterns = [
      /##\s*⭐?\s*RECOMMENDED\s*PILOT\s*PROJECT([\s\S]*?)(?=##\s*|$)/i,
      /##\s*Recommended\s*(?:Pilot\s*)?(?:Project)?([\s\S]*?)(?=##\s*|$)/i
    ];
    
    let recommendedMatch = null;
    for (const pattern of recommendedPatterns) {
      recommendedMatch = text.match(pattern);
      if (recommendedMatch) break;
    }

    if (recommendedMatch) {
      const recommendedText = recommendedMatch[1];
      const nameMatch = recommendedText.match(/\*\*Selected\s*Option:?\*\*\s*([^\n]+)/i);

      if (nameMatch) {
        const nameAndCategory = nameMatch[1].trim();
        const name = nameAndCategory.replace(/\s*\([^)]+\)\s*$/, '').trim();

        const whyMatch = recommendedText.match(/\*\*Why\s*This\s*Option:?\*\*([\s\S]*?)(?=\*\*Implementation|$)/i);
        const description = whyMatch ? whyMatch[1].trim() : '';

        // Mark as recommended in existing solutions or add it
        const existingIndex = solutions.findIndex(s => s.name.toLowerCase() === name.toLowerCase());
        if (existingIndex >= 0) {
          solutions[existingIndex].isRecommended = true;
          console.log(`SolutionSelector: Marked "${name}" as recommended`);
        } else {
          solutions.push({
            name,
            category: 'Recommended',
            categoryEmoji: '⭐',
            description,
            impact: 9,
            feasibility: 8,
            confidence: 9,
            time_to_value: 2,
            compositeScore: 9.5,
            isRecommended: true
          });
          console.log(`SolutionSelector: Added recommended solution "${name}"`);
        }
      }
    }

    console.log(`SolutionSelector: Final solution count: ${solutions.length}`);

    // Sort by composite score and return top 6 (including recommended)
    solutions.sort((a, b) => b.compositeScore - a.compositeScore);
    const top = solutions.slice(0, 6);

    // Ensure recommended is included if it exists
    const recommendedSolution = solutions.find(s => s.isRecommended);
    if (recommendedSolution && !top.includes(recommendedSolution)) {
      top[top.length - 1] = recommendedSolution;
    }

    return top;
  };

  return (
    <div className="solution-selector">
      <div className="selector-header">
        <h3>📋 Select a Solution to Prototype</h3>
        <p>Choose which solution you'd like to develop into a detailed Product Requirements Document</p>
      </div>

      {solutions.length > 0 && !useCustom && (
        <div className="solutions-grid">
          {solutions.map((solution, idx) => (
            <div
              key={idx}
              className={`solution-card ${selectedSolution === solution ? 'selected' : ''} ${solution.isRecommended ? 'recommended' : ''}`}
              onClick={() => setSelectedSolution(solution)}
            >
              {solution.isRecommended && <div className="recommended-badge">⭐ Recommended</div>}
              <div className="solution-header">
                <div className="solution-category">
                  <span className="category-emoji">{solution.categoryEmoji}</span>
                  <span className="category-name">{solution.category}</span>
                </div>
                <div className="solution-score">{solution.compositeScore.toFixed(1)}</div>
              </div>
              <div className="solution-name">{solution.name}</div>
              <div className="solution-description">{solution.description}</div>
              <div className="solution-metrics">
                <div className="metric">
                  <span className="metric-label">Impact:</span>
                  <span className="metric-value">{solution.impact}/10</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Feasibility:</span>
                  <span className="metric-value">{solution.feasibility}/10</span>
                </div>
                <div className="metric">
                  <span className="metric-label">Time:</span>
                  <span className="metric-value">{solution.time_to_value}mo</span>
                </div>
              </div>
              {selectedSolution === solution && <div className="selected-badge">✓ Selected</div>}
            </div>
          ))}
        </div>
      )}

      <div className="custom-solution-section">
        <button
          className="toggle-custom-button"
          onClick={() => {
            setUseCustom(!useCustom);
            if (!useCustom) setSelectedSolution(null);
          }}
        >
          {useCustom ? '← Back to suggested solutions' : '✍️ Enter custom solution'}
        </button>

        {useCustom && (
          <div className="custom-solution-inputs">
            <input
              type="text"
              className="custom-solution-name"
              placeholder="Solution name..."
              value={customSolution.name}
              onChange={(e) => setCustomSolution({ ...customSolution, name: e.target.value })}
            />
            <textarea
              className="custom-solution-description"
              placeholder="Solution description..."
              value={customSolution.description}
              onChange={(e) => setCustomSolution({ ...customSolution, description: e.target.value })}
              rows={4}
            />
          </div>
        )}
      </div>

      <div className="advance-actions">
        <button
          className="advance-button"
          onClick={handleAdvance}
          disabled={useCustom ? (!customSolution.name || !customSolution.description) : !selectedSolution}
        >
          Proceed to Generate PRD →
        </button>
        {(selectedSolution || (customSolution.name && customSolution.description)) && (
          <p className="advance-hint">
            We'll create a PRD for: <strong>{useCustom ? customSolution.name : selectedSolution.name}</strong>
          </p>
        )}
      </div>
    </div>
  );
}
