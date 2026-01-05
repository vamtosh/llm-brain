import ReactMarkdown from 'react-markdown';
import './Stage2.css';

export default function Stage2({ diagnoseOutput }) {
  if (!diagnoseOutput || !diagnoseOutput.response) {
    return null;
  }

  return (
    <div className="stage stage2">
      <h3 className="stage-title">Stage 2: DIAGNOSE - Root Cause Analysis</h3>
      <p className="stage-description">
        5-Why analysis and root cause hypotheses with supporting/disproving evidence
      </p>

      <div className="response-text markdown-content">
        <ReactMarkdown>{diagnoseOutput.response}</ReactMarkdown>
      </div>
    </div>
  );
}
