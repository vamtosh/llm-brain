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
  const [advancementContext, setAdvancementContext] = useState(null); // Store user input during advancement

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
      let convs = await api.listConversations();

      // Auto-delete empty "New Brainstorm" conversations
      const emptyBrainstorms = convs.filter(
        c => (c.title === 'New Brainstorm' || !c.title) && c.message_count === 0
      );

      if (emptyBrainstorms.length > 0) {
        // Delete all empty brainstorms
        await Promise.all(
          emptyBrainstorms.map(c => api.deleteConversation(c.id).catch(err => {
            console.error('Failed to auto-delete conversation:', err);
          }))
        );

        // Reload conversations after cleanup
        convs = await api.listConversations();
      }

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

  const handleDeleteConversation = async (id) => {
    try {
      await api.deleteConversation(id);

      // If deleted conversation was currently selected, clear selection
      if (id === currentConversationId) {
        setCurrentConversationId(null);
        setCurrentConversation(null);
        setStageStatus(null);
      }

      // Reload conversations list
      await loadConversations();
    } catch (error) {
      console.error('Failed to delete conversation:', error);
      alert('Failed to delete conversation. Please try again.');
    }
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

      // Add assistant message to UI (include stage for proper filtering)
      const assistantMessage = {
        role: 'assistant',
        content: response.content,
        reasoning: response.reasoning,
        metadata: response.metadata,
        stage: response.stage || stageStatus?.current_stage,
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

    // Optimistically update to next stage immediately
    const currentStage = stageStatus?.current_stage;
    const nextStage = stageStatus?.next_stage;

    // Store the advancement context (e.g., selected pain point)
    setAdvancementContext(userInput);
    setIsAdvancing(true);

    // Immediately update stage status to show next stage
    if (nextStage) {
      setStageStatus((prev) => ({
        ...prev,
        current_stage: nextStage,
      }));

      // Update conversation's current_stage in local state
      setCurrentConversation((prev) => ({
        ...prev,
        current_stage: nextStage,
      }));
    }

    try {
      const response = await api.advanceStage(currentConversationId, userInput);

      // Add the automatic assistant message to UI (include stage for proper filtering)
      if (response.content) {
        const assistantMessage = {
          role: 'assistant',
          content: response.content,
          reasoning: response.reasoning,
          metadata: response.metadata,
          stage: response.current_stage,  // The stage this message belongs to
        };

        setCurrentConversation((prev) => ({
          ...prev,
          messages: [...prev.messages, assistantMessage],
        }));
      }

      // Reload stage status
      await loadStageStatus(currentConversationId);

      // Reload conversations list to update title
      loadConversations();
    } catch (error) {
      console.error('Failed to advance stage:', error);
      alert('Failed to advance to next stage. Please try again.');

      // Revert optimistic update on error
      if (currentStage) {
        setStageStatus((prev) => ({
          ...prev,
          current_stage: currentStage,
        }));

        setCurrentConversation((prev) => ({
          ...prev,
          current_stage: currentStage,
        }));
      }
    } finally {
      setIsAdvancing(false);
      setAdvancementContext(null); // Clear context after advancement completes
    }
  };

  return (
    <div className="app">
      <Sidebar
        conversations={conversations}
        currentConversationId={currentConversationId}
        onSelectConversation={handleSelectConversation}
        onNewConversation={handleNewConversation}
        onDeleteConversation={handleDeleteConversation}
      />
      <ChatInterface
        conversation={currentConversation}
        stageStatus={stageStatus}
        onSendMessage={handleSendMessage}
        onAdvanceStage={handleAdvanceStage}
        isLoading={isLoading}
        isAdvancing={isAdvancing}
        advancementContext={advancementContext}
      />
    </div>
  );
}

export default App;
