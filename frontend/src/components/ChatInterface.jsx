import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import StageProgress from './StageProgress';
import PainPointSelector from './PainPointSelector';
import SolutionSelector from './SolutionSelector';
import PRDViewer from './PRDViewer';
import './ChatInterface.css';

export default function ChatInterface({
  conversation,
  stageStatus,
  onSendMessage,
  onAdvanceStage,
  isLoading,
  isAdvancing,
  advancementContext,
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

  // Reset showAdvanceUI when conversation changes
  useEffect(() => {
    setShowAdvanceUI(false);
  }, [conversation?.id]);

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

  // Get last assistant message from a specific stage
  const getLastAssistantMessageFromStage = (stage) => {
    console.log(`ChatInterface: Looking for assistant message from stage '${stage}'`);
    console.log(`ChatInterface: Total messages: ${conversation.messages.length}`);
    
    for (let i = conversation.messages.length - 1; i >= 0; i--) {
      const msg = conversation.messages[i];
      console.log(`ChatInterface: Message ${i}: role=${msg.role}, stage=${msg.stage}`);
      if (msg.role === 'assistant' && msg.stage === stage) {
        console.log(`ChatInterface: Found ${stage} message, content length: ${msg.content?.length}`);
        return msg;
      }
    }
    console.log(`ChatInterface: No ${stage} message found`);
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

        {isAdvancing && (
          <div className="loading-indicator">
            <div className="spinner"></div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              <span>
                {currentStage === 'diagnose' && 'Running diagnosis for the selected pain point...'}
                {currentStage === 'converge' && 'Generating solution ideas based on the analysis...'}
                {currentStage === 'select_solution' && 'Preparing solution options for selection...'}
                {currentStage === 'generate_prd' && `Generating Product Requirements Document for: ${advancementContext?.selected_solution?.name || 'selected solution'}...`}
                {!['diagnose', 'converge', 'select_solution', 'generate_prd'].includes(currentStage) && 'Advancing to next stage...'}
              </span>
              {currentStage === 'diagnose' && advancementContext?.selected_pain_point && (
                <div style={{
                  fontSize: '0.9em',
                  color: '#666',
                  fontStyle: 'italic',
                  marginTop: '4px',
                  padding: '8px 12px',
                  background: '#f8f9fa',
                  borderRadius: '6px',
                  borderLeft: '3px solid #4a90e2'
                }}>
                  <strong>Pain Point:</strong> {advancementContext.selected_pain_point}
                </div>
              )}
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Stage Advancement UI */}
      {!isComplete && canAdvance && !showAdvanceUI && !isAdvancing && currentStage !== 'select_solution' && currentStage !== 'generate_prd' && (
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
      {showAdvanceUI && !isAdvancing && requiresInput.required && requiresInput.type === 'pain_point_selection' && (
        <PainPointSelector
          widenOutput={getLastAssistantMessage()?.content || ''}
          onAdvance={handleAdvance}
        />
      )}

      {/* Solution Selector (SELECT_SOLUTION stage) */}
      {currentStage === 'select_solution' && !isAdvancing && (
        <SolutionSelector
          convergeOutput={getLastAssistantMessageFromStage('converge')?.content || ''}
          onAdvance={handleAdvance}
        />
      )}

      {/* PRD Viewer (GENERATE_PRD stage) */}
      {currentStage === 'generate_prd' && !isAdvancing && (
        <PRDViewer
          prdContent={getLastAssistantMessage()?.content || ''}
          solutionName={advancementContext?.selected_solution?.name || 'Solution'}
        />
      )}

      {/* Simple Advance (DIAGNOSE → CONVERGE or other) */}
      {showAdvanceUI && !isAdvancing && !requiresInput.required && (
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
      {!isComplete && !showAdvanceUI && !isAdvancing && (
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
