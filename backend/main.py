"""FastAPI backend for Brainstorming Partner with PostgreSQL."""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import json

from .database.client import init_db, close_db
from .database.repositories import (
    ConversationRepository,
    MessageRepository,
    StageContextRepository,
)
from .stage_manager import StageManager, Stage
from .brainstorm import generate_conversation_title, process_stage_message

app = FastAPI(title="Brainstorming Partner API")

# Enable CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Database lifecycle
@app.on_event("startup")
async def startup():
    """Initialize database connection pool on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown():
    """Close database connection pool on shutdown."""
    await close_db()


# Pydantic models
class CreateConversationRequest(BaseModel):
    """Request to create a new conversation."""
    pass


class SendMessageRequest(BaseModel):
    """Request to send a message in a conversation."""
    content: str


class AdvanceStageRequest(BaseModel):
    """Request to advance to the next stage."""
    user_input: Optional[Dict[str, Any]] = None


class ConversationMetadata(BaseModel):
    """Conversation metadata for list view."""
    id: str
    created_at: str
    title: str
    message_count: int
    current_stage: str


# Health check
@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Brainstorming Partner API"}


# Conversation endpoints
@app.get("/api/conversations")
async def list_conversations():
    """List all conversations (metadata only)."""
    conversations = await ConversationRepository.list()
    return conversations


@app.post("/api/conversations")
async def create_conversation(request: CreateConversationRequest):
    """Create a new conversation."""
    conversation = await ConversationRepository.create()
    return conversation


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get a specific conversation with all its messages."""
    conversation = await ConversationRepository.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get all messages
    messages = await MessageRepository.list(conversation_id)

    return {
        **conversation,
        "messages": messages
    }


# Stage management endpoints
@app.get("/api/conversations/{conversation_id}/stage-status")
async def get_stage_status(conversation_id: str):
    """Get current stage status and advancement info."""
    conversation = await ConversationRepository.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    current_stage = conversation.get("current_stage")
    next_stage = StageManager.get_next_stage(current_stage)

    # Get stage context if available
    stage_context = await StageContextRepository.get(conversation_id, current_stage)

    return {
        "current_stage": current_stage,
        "next_stage": next_stage,
        "can_advance": StageManager.can_advance(current_stage, stage_context),
        "requires_input": StageManager.requires_user_input(current_stage, next_stage) if next_stage else {}
    }


@app.post("/api/conversations/{conversation_id}/advance-stage")
async def advance_stage(conversation_id: str, request: AdvanceStageRequest):
    """Advance to the next stage."""
    conversation = await ConversationRepository.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    current_stage = conversation.get("current_stage")
    next_stage = StageManager.get_next_stage(current_stage)

    if next_stage is None:
        raise HTTPException(status_code=400, detail="Already at final stage")

    # Validate transition
    if not StageManager.validate_stage_transition(current_stage, next_stage):
        raise HTTPException(status_code=400, detail="Invalid stage transition")

    # Check if user input is required
    input_req = StageManager.requires_user_input(current_stage, next_stage)
    if input_req.get("required") and not request.user_input:
        raise HTTPException(
            status_code=400,
            detail=f"User input required: {input_req.get('description')}"
        )

    # Get messages from current stage to create context
    current_messages = await MessageRepository.list_by_stage(conversation_id, current_stage)

    # Compile output from current stage (last assistant message)
    current_output = ""
    for msg in reversed(current_messages):
        if msg["role"] == "assistant":
            current_output = msg["content"]
            break

    # Mark current stage as complete
    await StageContextRepository.mark_complete(
        conversation_id,
        current_stage,
        current_output
    )

    # Create or update context for new stage
    await StageContextRepository.create_or_update(
        conversation_id,
        next_stage,
        request.user_input or {},
        None,
        None
    )

    # Update conversation's current stage
    await ConversationRepository.update_stage(conversation_id, next_stage)

    return {
        "success": True,
        "previous_stage": current_stage,
        "current_stage": next_stage,
        "message": f"Advanced from {current_stage} to {next_stage}"
    }


# Message endpoints
@app.post("/api/conversations/{conversation_id}/message")
async def send_message(conversation_id: str, request: SendMessageRequest):
    """
    Send a message within the current stage.
    Auto-saves message and responds within stage context.
    """
    conversation = await ConversationRepository.get(conversation_id)
    if conversation is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    current_stage = conversation.get("current_stage")

    if current_stage == Stage.COMPLETE.value:
        raise HTTPException(status_code=400, detail="Brainstorming session is complete")

    # Check if this is the first user message
    messages = await MessageRepository.list(conversation_id)
    is_first_message = len(messages) == 0

    # Auto-save user message
    await MessageRepository.create(
        conversation_id=conversation_id,
        role="user",
        content=request.content,
        stage=current_stage
    )

    # Generate title if first message
    if is_first_message:
        title = await generate_conversation_title(request.content)
        await ConversationRepository.update_title(conversation_id, title)

    # Get context from previous stages
    all_stage_contexts = await StageContextRepository.get_all(conversation_id)
    previous_stages = {sc["stage"]: sc for sc in all_stage_contexts}

    # Get current stage context
    current_context = await StageContextRepository.get(conversation_id, current_stage)
    user_selections = current_context.get("context_data", {}) if current_context else {}

    # Build context for current stage
    context = StageManager.build_context_for_stage(
        current_stage,
        previous_stages,
        user_selections
    )

    # Process message within current stage
    response_data = await process_stage_message(
        stage=current_stage,
        user_message=request.content,
        context=context
    )

    # Auto-save assistant message
    await MessageRepository.create(
        conversation_id=conversation_id,
        role="assistant",
        content=response_data.get("content", ""),
        stage=current_stage,
        reasoning=response_data.get("reasoning"),
        metadata=response_data.get("metadata", {})
    )

    return {
        "stage": current_stage,
        "content": response_data.get("content", ""),
        "reasoning": response_data.get("reasoning"),
        "metadata": response_data.get("metadata", {}),
        "title": conversation.get("title") if is_first_message else None
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
