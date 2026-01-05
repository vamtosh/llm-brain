import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import ChatInterface from './components/ChatInterface';
import { api } from './api';
import './App.css';

function App() {
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [currentConversation, setCurrentConversation] = useState(null);
  const [stageStatus, setStageStatus] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isAdvancing, setIsAdvancing] = useState(false);

  // Load conversations on mount
  useEffect(() => {
    loadConversations();
  }, []);

  // Load conversation details and stage status when selected
  useEffect(() => {
    if (currentConversationId) {
      loadConversation(currentConversationId);
      loadStageStatus(currentConversationId);
    }
  }, [currentConversationId]);

  const loadConversations = async () => {
    try {
      const convs = await api.listConversations();
      setConversations(convs);
    } catch (error) {
      console.error('Failed to load conversations:', error);
    }
  };

  const loadConversation = async (id) => {
    try {
      const conv = await api.getConversation(id);
      setCurrentConversation(conv);
    } catch (error) {
      console.error('Failed to load conversation:', error);
    }
  };

  const loadStageStatus = async (id) => {
    try {
      const status = await api.getStageStatus(id);
      setStageStatus(status);
    } catch (error) {
      console.error('Failed to load stage status:', error);
    }
  };

  const handleNewConversation = async () => {
    try {
      const newConv = await api.createConversation();
      setConversations([
        { id: newConv.id, created_at: newConv.created_at, message_count: 0 },
        ...conversations,
      ]);
      setCurrentConversationId(newConv.id);
    } catch (error) {
      console.error('Failed to create conversation:', error);
    }
  };

  const handleSelectConversation = (id) => {
    setCurrentConversationId(id);
  };

  const handleSendMessage = async (content) => {
    if (!currentConversationId) return;

    setIsLoading(true);
    try {
      // Optimistically add user message to UI
      const userMessage = { role: 'user', content };
      setCurrentConversation((prev) => ({
        ...prev,
        messages: [...prev.messages, userMessage],
      }));

      // Send message and get response
      const response = await api.sendMessage(currentConversationId, content);

      // Add assistant message to UI
      const assistantMessage = {
        role: 'assistant',
        content: response.content,
        reasoning: response.reasoning,
        metadata: response.metadata,
      };

      setCurrentConversation((prev) => ({
        ...prev,
        messages: [...prev.messages, assistantMessage],
      }));

      // Reload conversations list to update title and message count
      loadConversations();

      // Reload stage status to check if stage can be advanced
      await loadStageStatus(currentConversationId);
    } catch (error) {
      console.error('Failed to send message:', error);
      // Remove optimistic user message on error
      setCurrentConversation((prev) => ({
        ...prev,
        messages: prev.messages.slice(0, -1),
      }));
    } finally {
      setIsLoading(false);
    }
  };

  const handleAdvanceStage = async (userInput = null) => {
    if (!currentConversationId) return;

    setIsAdvancing(true);
    try {
      await api.advanceStage(currentConversationId, userInput);

      // Reload conversation to get updated stage
      await loadConversation(currentConversationId);

      // Reload stage status
      await loadStageStatus(currentConversationId);

      // Reload conversations list to update title
      loadConversations();
    } catch (error) {
      console.error('Failed to advance stage:', error);
      alert('Failed to advance to next stage. Please try again.');
    } finally {
      setIsAdvancing(false);
    }
  };

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
      />
      <ChatInterface
        conversation={currentConversation}
        stageStatus={stageStatus}
        onSendMessage={handleSendMessage}
        onAdvanceStage={handleAdvanceStage}
        isLoading={isLoading}
        isAdvancing={isAdvancing}
      />
    </div>
  );
}

export default App;
