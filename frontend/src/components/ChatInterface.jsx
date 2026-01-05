import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import StageProgress from './StageProgress';
import PainPointSelector from './PainPointSelector';
import './ChatInterface.css';

export default function ChatInterface({
  conversation,
  stageStatus,
  onSendMessage,
  onAdvanceStage,
  isLoading,
  isAdvancing,
}) {
  const [input, setInput] = useState('');
  const [showAdvanceUI, setShowAdvanceUI] = useState(false);
  const [expandedReasoning, setExpandedReasoning] = useState(new Set());
  const messagesEndRef = useRef(null);

  const toggleReasoning = (index) => {
    const newExpanded = new Set(expandedReasoning);
    if (newExpanded.has(index)) {
      newExpanded.delete(index);
    } else {
      newExpanded.add(index);
    }
    setExpandedReasoning(newExpanded);
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversation]);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim() && !isLoading) {
      onSendMessage(input);
      setInput('');
    }
  };

  const handleKeyDown = (e) => {
    // Submit on Enter (without Shift)
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleAdvance = (userInput = null) => {
    onAdvanceStage(userInput);
    setShowAdvanceUI(false);
  };

  if (!conversation) {
    return (
      <div className="chat-interface">
        <div className="empty-state">
          <h2>Welcome to Brainstorming Partner</h2>
          <p>Create a new brainstorming session to get started</p>
        </div>
      </div>
    );
  }

  const currentStage = stageStatus?.current_stage || 'widen';
  const canAdvance = stageStatus?.can_advance && conversation.messages.length > 0;
  const requiresInput = stageStatus?.requires_input || {};
  const isComplete = currentStage === 'complete';

  // Get last assistant message for WIDEN output (needed for pain point selection)
  const getLastAssistantMessage = () => {
    for (let i = conversation.messages.length - 1; i >= 0; i--) {
      if (conversation.messages[i].role === 'assistant') {
        const msg = conversation.messages[i];
        console.log('ChatInterface: Last assistant message:', {
          hasContent: !!msg.content,
          contentLength: msg.content?.length,
          hasReasoning: !!msg.reasoning,
          reasoningLength: msg.reasoning?.length
        });
        return msg;
      }
    }
    return null;
  };

  return (
    <div className="chat-interface">
      {/* Stage Progress Indicator */}
      {conversation.messages.length > 0 && (
        <StageProgress currentStage={currentStage} />
      )}

      {/* Messages Container */}
      <div className="messages-container">
        {conversation.messages.length === 0 ? (
          <div className="empty-state">
            <h2>🔍 Stage 1: WIDEN</h2>
            <p>Describe your challenge to explore the problem space</p>
          </div>
        ) : (
          <>
            <div className="current-stage-badge">
              Current Stage: <strong>{currentStage.toUpperCase()}</strong>
            </div>

            {conversation.messages.map((msg, index) => (
              <div key={index} className="message-group">
                {msg.role === 'user' ? (
                  <div className="user-message">
                    <div className="message-label">You</div>
                    <div className="message-content markdown-content">
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                ) : (
                  <div className="assistant-message">
                    <div className="message-label">Brainstorming Partner</div>
                    <div className="message-content markdown-content">
                      {msg.reasoning && (
                        <div
                          className="reasoning-container"
                          onClick={() => toggleReasoning(index)}
                          style={{ cursor: 'pointer', marginBottom: '12px' }}
                        >
                          <div className="reasoning-header" style={{
                            color: '#666',
                            fontSize: '0.85em',
                            fontWeight: '500',
                            marginBottom: '4px',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '6px'
                          }}>
                            <span>{expandedReasoning.has(index) ? '▼' : '▶'}</span>
                            <span>💭 Reasoning</span>
                            <span style={{ fontSize: '0.9em', opacity: 0.7 }}>
                              (click to {expandedReasoning.has(index) ? 'collapse' : 'expand'})
                            </span>
                          </div>
                          <div style={{
                            color: '#666',
                            fontSize: '0.9em',
                            fontStyle: 'italic',
                            padding: '8px 12px',
                            background: '#f8f9fa',
                            borderRadius: '4px',
                            borderLeft: '3px solid #4a90e2'
                          }}>
                            {expandedReasoning.has(index)
                              ? msg.reasoning
                              : msg.reasoning.split('\n').slice(-3).join(' ') + '...'
                            }
                          </div>
                        </div>
                      )}
                      <ReactMarkdown>{msg.content}</ReactMarkdown>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </>
        )}

        {isLoading && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <span>Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Stage Advancement UI */}
      {!isComplete && canAdvance && !showAdvanceUI && (
        <div className="advance-prompt">
          <button
            className="show-advance-button"
            onClick={() => setShowAdvanceUI(true)}
          >
            ✓ Complete {currentStage.toUpperCase()} Stage & Continue →
          </button>
        </div>
      )}

      {/* Pain Point Selector (WIDEN → DIAGNOSE) */}
      {showAdvanceUI && requiresInput.required && requiresInput.type === 'pain_point_selection' && (
        <PainPointSelector
          widenOutput={getLastAssistantMessage()?.content || ''}
          onAdvance={handleAdvance}
        />
      )}

      {/* Simple Advance (DIAGNOSE → CONVERGE or other) */}
      {showAdvanceUI && !requiresInput.required && (
        <div className="simple-advance">
          <p>{requiresInput.description || 'Ready to advance to the next stage?'}</p>
          <div className="advance-actions">
            <button
              className="advance-button"
              onClick={() => handleAdvance()}
              disabled={isAdvancing}
            >
              {isAdvancing ? 'Advancing...' : `Proceed to ${stageStatus?.next_stage?.toUpperCase()} →`}
            </button>
            <button
              className="cancel-button"
              onClick={() => setShowAdvanceUI(false)}
              disabled={isAdvancing}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Message Input Form */}
      {!isComplete && !showAdvanceUI && (
        <form className="input-form" onSubmit={handleSubmit}>
          <textarea
            className="message-input"
            placeholder={
              conversation.messages.length === 0
                ? "Describe your challenge... (Shift+Enter for new line, Enter to send)"
                : "Continue the conversation... (Shift+Enter for new line, Enter to send)"
            }
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            rows={3}
          />
          <button
            type="submit"
            className="send-button"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </form>
      )}

      {/* Completion Message */}
      {isComplete && (
        <div className="completion-message">
          <h3>🎉 Brainstorming Complete!</h3>
          <p>All stages have been completed. Review the insights above.</p>
        </div>
      )}
    </div>
  );
}
