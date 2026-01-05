/**
 * API client for the LLM Council backend.
 */

const API_BASE = 'http://localhost:8001';

export const api = {
  /**
   * List all conversations.
   */
  async listConversations() {
    const response = await fetch(`${API_BASE}/api/conversations`);
    if (!response.ok) {
      throw new Error('Failed to list conversations');
    }
    return response.json();
  },

  /**
   * Create a new conversation.
   */
  async createConversation() {
    const response = await fetch(`${API_BASE}/api/conversations`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({}),
    });
    if (!response.ok) {
      throw new Error('Failed to create conversation');
    }
    return response.json();
  },

  /**
   * Get a specific conversation.
   */
  async getConversation(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}`
    );
    if (!response.ok) {
      throw new Error('Failed to get conversation');
    }
    return response.json();
  },

  /**
   * Send a message in a conversation.
   */
  async sendMessage(conversationId, content) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/message`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      }
    );
    if (!response.ok) {
      throw new Error('Failed to send message');
    }
    return response.json();
  },

  /**
   * Get stage status for a conversation.
   */
  async getStageStatus(conversationId) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/stage-status`
    );
    if (!response.ok) {
      throw new Error('Failed to get stage status');
    }
    return response.json();
  },

  /**
   * Advance to the next stage.
   * @param {string} conversationId - The conversation ID
   * @param {object} userInput - Optional user input for stage transition
   */
  async advanceStage(conversationId, userInput = null) {
    const response = await fetch(
      `${API_BASE}/api/conversations/${conversationId}/advance-stage`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ user_input: userInput }),
      }
    );
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Failed to advance stage');
    }
    return response.json();
  },
};
