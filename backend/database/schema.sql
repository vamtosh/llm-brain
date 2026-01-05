-- Brainstorming Partner Database Schema
-- Optimized for multi-user concurrent access (3000+ users)

-- Enable UUID extension for better distributed IDs
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table (for future multi-user support)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Conversations table
CREATE TABLE conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title VARCHAR(500) DEFAULT 'New Brainstorm',
    current_stage VARCHAR(20) DEFAULT 'widen' CHECK (current_stage IN ('widen', 'diagnose', 'converge', 'complete')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast user conversation lookups
CREATE INDEX idx_conversations_user_id ON conversations(user_id);
CREATE INDEX idx_conversations_created_at ON conversations(created_at DESC);

-- Messages table (stores all conversation messages)
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    stage VARCHAR(20) CHECK (stage IN ('widen', 'diagnose', 'converge')),
    reasoning TEXT,  -- GPT-5 reasoning process
    metadata JSONB DEFAULT '{}',  -- Flexible storage for additional data
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for fast message retrieval
CREATE INDEX idx_messages_conversation_id ON messages(conversation_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_messages_stage ON messages(stage);

-- Stage contexts table (stores accumulated context per stage)
CREATE TABLE stage_contexts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
    stage VARCHAR(20) NOT NULL CHECK (stage IN ('widen', 'diagnose', 'converge')),
    context_data JSONB NOT NULL DEFAULT '{}',  -- Stores pain points, selections, etc.
    output TEXT,  -- Final output when stage is completed
    completed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(conversation_id, stage)
);

-- Index for fast stage context lookups
CREATE INDEX idx_stage_contexts_conversation_id ON stage_contexts(conversation_id);

-- Documents table (for context document uploads)
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE NOT NULL,
    filename VARCHAR(500) NOT NULL,
    file_size BIGINT NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    extracted_text TEXT,  -- Extracted text content
    chunks JSONB,  -- Text chunks for large documents
    metadata JSONB DEFAULT '{}',  -- File metadata (pages, etc.)
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Index for fast document lookups
CREATE INDEX idx_documents_conversation_id ON documents(conversation_id);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers for auto-updating updated_at
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_stage_contexts_updated_at BEFORE UPDATE ON stage_contexts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create default anonymous user for MVP (can be removed when adding auth)
INSERT INTO users (id, email) VALUES
    ('00000000-0000-0000-0000-000000000000', 'anonymous@brainstorm.local')
ON CONFLICT (email) DO NOTHING;

-- Performance optimization: Analyze tables for query planner
ANALYZE users;
ANALYZE conversations;
ANALYZE messages;
ANALYZE stage_contexts;
ANALYZE documents;
