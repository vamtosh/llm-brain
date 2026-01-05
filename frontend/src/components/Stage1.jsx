import ReactMarkdown from 'react-markdown';
import './Stage1.css';

export default function Stage1({ widenOutput }) {
  if (!widenOutput || !widenOutput.response) {
    return null;
  }

  return (
    <div className="stage stage1">
      <h3 className="stage-title">Stage 1: WIDEN - Explore the Problem Space</h3>
      <p className="stage-description">
        Surface personas, pains, workarounds, metrics, insights, and risks
      </p>

      <div className="response-text markdown-content">
        <ReactMarkdown>{widenOutput.response}</ReactMarkdown>
      </div>
    </div>
  );
}
