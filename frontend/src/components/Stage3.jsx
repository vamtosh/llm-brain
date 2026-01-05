import ReactMarkdown from 'react-markdown';
import './Stage3.css';

export default function Stage3({ convergeOutput }) {
  if (!convergeOutput || !convergeOutput.response) {
    return null;
  }

  return (
    <div className="stage stage3">
      <h3 className="stage-title">Stage 3: CONVERGE - Solutions & Ideas</h3>
      <p className="stage-description">
        Clustered solution ideas in Process, Analytics, ML/Automation, and Other categories
      </p>
      <div className="final-response">
        <div className="final-text markdown-content">
          <ReactMarkdown>{convergeOutput.response}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
