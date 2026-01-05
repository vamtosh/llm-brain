import { useState } from 'react';
import './PainPointSelector.css';

export default function PainPointSelector({ widenOutput, onAdvance }) {
  const [selectedPainPoint, setSelectedPainPoint] = useState('');
  const [customPainPoint, setCustomPainPoint] = useState('');
  const [useCustom, setUseCustom] = useState(false);

  const handleAdvance = () => {
    const painPoint = useCustom ? customPainPoint : selectedPainPoint;
    if (painPoint.trim()) {
      onAdvance({ selected_pain_point: painPoint });
    }
  };

  // Extract pain points from WIDEN output (simple heuristic)
  const extractPainPoints = (text) => {
    if (!text) return [];

    // Look for PAINS section
    const painsMatch = text.match(/##?\s*(?:2\.\s*)?PAINS?\s*:?\s*([\s\S]*?)(?=##?\s*(?:3\.|WORKAROUNDS|$))/i);
    if (!painsMatch) return [];

    const painsSection = painsMatch[1];
    // Extract bulleted or numbered points
    const points = painsSection
      .split('\n')
      .filter(line => line.trim().match(/^[-*•\d]/))
      .map(line => line.replace(/^[-*•\d.)\s]+/, '').trim())
      .filter(line => line.length > 10 && line.length < 200);

    return points.slice(0, 8); // Max 8 pain points
  };

  const painPoints = extractPainPoints(widenOutput);

  return (
    <div className="pain-point-selector">
      <div className="selector-header">
        <h3>🎯 Select a Pain Point to Diagnose</h3>
        <p>Choose which pain point you'd like to analyze in depth using the 5-Why technique</p>
      </div>

      {painPoints.length > 0 && !useCustom && (
        <div className="pain-points-grid">
          {painPoints.map((pain, idx) => (
            <div
              key={idx}
              className={`pain-card ${selectedPainPoint === pain ? 'selected' : ''}`}
              onClick={() => setSelectedPainPoint(pain)}
            >
              <div className="pain-number">{idx + 1}</div>
              <div className="pain-text">{pain}</div>
              {selectedPainPoint === pain && <div className="selected-badge">✓ Selected</div>}
            </div>
          ))}
        </div>
      )}

      <div className="custom-pain-section">
        <button
          className="toggle-custom-button"
          onClick={() => {
            setUseCustom(!useCustom);
            if (!useCustom) setSelectedPainPoint('');
          }}
        >
          {useCustom ? '← Back to suggested pain points' : '✍️ Enter custom pain point'}
        </button>

        {useCustom && (
          <textarea
            className="custom-pain-input"
            placeholder="Describe the specific pain point you want to analyze..."
            value={customPainPoint}
            onChange={(e) => setCustomPainPoint(e.target.value)}
            rows={4}
          />
        )}
      </div>

      <div className="advance-actions">
        <button
          className="advance-button"
          onClick={handleAdvance}
          disabled={useCustom ? !customPainPoint.trim() : !selectedPainPoint}
        >
          Proceed to DIAGNOSE →
        </button>
        {(selectedPainPoint || customPainPoint) && (
          <p className="advance-hint">
            We'll analyze: <strong>{useCustom ? customPainPoint : selectedPainPoint}</strong>
          </p>
        )}
      </div>
    </div>
  );
}
