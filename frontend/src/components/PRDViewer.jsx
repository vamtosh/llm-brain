import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './PRDViewer.css';

export default function PRDViewer({ prdContent, solutionName }) {
  const [isDownloading, setIsDownloading] = useState(false);

  const handleDownload = () => {
    setIsDownloading(true);
    try {
      // Create filename from solution name
      const filename = `PRD_${solutionName.replace(/[^a-z0-9]/gi, '_')}_${new Date().toISOString().split('T')[0]}.md`;

      // Create blob and download
      const blob = new Blob([prdContent], { type: 'text/markdown' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download PRD:', error);
      alert('Failed to download PRD. Please try again.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="prd-viewer">
      <div className="prd-header">
        <div className="prd-header-content">
          <h2>📄 Product Requirements Document</h2>
          <p className="prd-subtitle">Generated for: <strong>{solutionName}</strong></p>
        </div>
        <button
          className="download-button"
          onClick={handleDownload}
          disabled={isDownloading}
        >
          {isDownloading ? '⏳ Downloading...' : '💾 Download PRD.md'}
        </button>
      </div>

      <div className="prd-content markdown-content">
        <ReactMarkdown>{prdContent}</ReactMarkdown>
      </div>

      <div className="prd-footer">
        <div className="completion-message">
          <span className="check-icon">✅</span>
          <span>PRD Generated Successfully!</span>
        </div>
        <button className="download-button secondary" onClick={handleDownload}>
          💾 Download PRD.md
        </button>
      </div>
    </div>
  );
}
