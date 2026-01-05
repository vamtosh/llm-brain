"""Repository layer for database operations."""

from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
from .client import db


class ConversationRepository:
    """Repository for conversation operations."""

    @staticmethod
    async def create(user_id: str = "00000000-0000-0000-0000-000000000000") -> Dict[str, Any]:
        """Create a new conversation."""
        conversation_id = str(uuid.uuid4())

        await db.execute(
            """
            INSERT INTO conversations (id, user_id, title, current_stage)
            VALUES ($1, $2, $3, $4)
            """,
            uuid.UUID(conversation_id),
            uuid.UUID(user_id),
            "New Brainstorm",
            "widen"
        )

        return {
            "id": conversation_id,
            "user_id": user_id,
            "title": "New Brainstorm",
            "current_stage": "widen",
            "created_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    async def get(conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get a conversation by ID."""
        row = await db.fetchrow(
            """
            SELECT id, user_id, title, current_stage, created_at, updated_at
            FROM conversations
            WHERE id = $1
            """,
            uuid.UUID(conversation_id)
        )

        if row is None:
            return None

        return dict(row)

    @staticmethod
    async def list(user_id: str = "00000000-0000-0000-0000-000000000000", limit: int = 50) -> List[Dict[str, Any]]:
        """List conversations for a user."""
        rows = await db.fetch(
            """
            SELECT
                c.id,
                c.title,
                c.current_stage,
                c.created_at,
                COUNT(m.id) as message_count
            FROM conversations c
            LEFT JOIN messages m ON c.id = m.conversation_id
            WHERE c.user_id = $1
            GROUP BY c.id, c.title, c.current_stage, c.created_at
            ORDER BY c.created_at DESC
            LIMIT $2
            """,
            uuid.UUID(user_id),
            limit
        )

        return [dict(row) for row in rows]

    @staticmethod
    async def update_title(conversation_id: str, title: str):
        """Update conversation title."""
        await db.execute(
            """
            UPDATE conversations
            SET title = $2
            WHERE id = $1
            """,
            uuid.UUID(conversation_id),
            title
        )

    @staticmethod
    async def update_stage(conversation_id: str, stage: str):
        """Update current stage."""
        await db.execute(
            """
            UPDATE conversations
            SET current_stage = $2
            WHERE id = $1
            """,
            uuid.UUID(conversation_id),
            stage
        )

    @staticmethod
    async def get_current_stage(conversation_id: str) -> Optional[str]:
        """Get current stage of a conversation."""
        return await db.fetchval(
            """
            SELECT current_stage
            FROM conversations
            WHERE id = $1
            """,
            uuid.UUID(conversation_id)
        )


class MessageRepository:
    """Repository for message operations."""

    @staticmethod
    async def create(
        conversation_id: str,
        role: str,
        content: str,
        stage: Optional[str] = None,
        reasoning: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new message (auto-save)."""
        message_id = str(uuid.uuid4())

        await db.execute(
            """
            INSERT INTO messages (id, conversation_id, role, content, stage, reasoning, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            """,
            uuid.UUID(message_id),
            uuid.UUID(conversation_id),
            role,
            content,
            stage,
            reasoning,
            metadata or {}
        )

        return {
            "id": message_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": content,
            "stage": stage,
            "reasoning": reasoning,
            "metadata": metadata,
            "created_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    async def list(conversation_id: str) -> List[Dict[str, Any]]:
        """Get all messages for a conversation."""
        rows = await db.fetch(
            """
            SELECT id, conversation_id, role, content, stage, reasoning, metadata, created_at
            FROM messages
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            """,
            uuid.UUID(conversation_id)
        )

        return [dict(row) for row in rows]

    @staticmethod
    async def list_by_stage(conversation_id: str, stage: str) -> List[Dict[str, Any]]:
        """Get messages for a specific stage."""
        rows = await db.fetch(
            """
            SELECT id, conversation_id, role, content, stage, reasoning, metadata, created_at
            FROM messages
            WHERE conversation_id = $1 AND stage = $2
            ORDER BY created_at ASC
            """,
            uuid.UUID(conversation_id),
            stage
        )

        return [dict(row) for row in rows]


class StageContextRepository:
    """Repository for stage context operations."""

    @staticmethod
    async def create_or_update(
        conversation_id: str,
        stage: str,
        context_data: Dict[str, Any],
        output: Optional[str] = None,
        completed_at: Optional[datetime] = None
    ):
        """Create or update stage context."""
        await db.execute(
            """
            INSERT INTO stage_contexts (conversation_id, stage, context_data, output, completed_at)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (conversation_id, stage)
            DO UPDATE SET
                context_data = $3,
                output = $4,
                completed_at = $5,
                updated_at = CURRENT_TIMESTAMP
            """,
            uuid.UUID(conversation_id),
            stage,
            context_data,
            output,
            completed_at
        )

    @staticmethod
    async def get(conversation_id: str, stage: str) -> Optional[Dict[str, Any]]:
        """Get stage context."""
        row = await db.fetchrow(
            """
            SELECT conversation_id, stage, context_data, output, completed_at, created_at, updated_at
            FROM stage_contexts
            WHERE conversation_id = $1 AND stage = $2
            """,
            uuid.UUID(conversation_id),
            stage
        )

        if row is None:
            return None

        return dict(row)

    @staticmethod
    async def get_all(conversation_id: str) -> List[Dict[str, Any]]:
        """Get all stage contexts for a conversation."""
        rows = await db.fetch(
            """
            SELECT conversation_id, stage, context_data, output, completed_at, created_at, updated_at
            FROM stage_contexts
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            """,
            uuid.UUID(conversation_id)
        )

        return [dict(row) for row in rows]

    @staticmethod
    async def mark_complete(conversation_id: str, stage: str, output: str):
        """Mark a stage as complete."""
        await db.execute(
            """
            UPDATE stage_contexts
            SET output = $3, completed_at = CURRENT_TIMESTAMP
            WHERE conversation_id = $1 AND stage = $2
            """,
            uuid.UUID(conversation_id),
            stage,
            output
        )


class DocumentRepository:
    """Repository for document operations."""

    @staticmethod
    async def create(
        conversation_id: str,
        filename: str,
        file_size: int,
        file_type: str,
        extracted_text: str,
        chunks: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new document."""
        document_id = str(uuid.uuid4())

        await db.execute(
            """
            INSERT INTO documents (id, conversation_id, filename, file_size, file_type, extracted_text, chunks, metadata)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """,
            uuid.UUID(document_id),
            uuid.UUID(conversation_id),
            filename,
            file_size,
            file_type,
            extracted_text,
            chunks or [],
            metadata or {}
        )

        return {
            "id": document_id,
            "conversation_id": conversation_id,
            "filename": filename,
            "file_size": file_size,
            "file_type": file_type,
            "created_at": datetime.utcnow().isoformat(),
        }

    @staticmethod
    async def list(conversation_id: str) -> List[Dict[str, Any]]:
        """List all documents for a conversation."""
        rows = await db.fetch(
            """
            SELECT id, conversation_id, filename, file_size, file_type, metadata, created_at
            FROM documents
            WHERE conversation_id = $1
            ORDER BY created_at ASC
            """,
            uuid.UUID(conversation_id)
        )

        return [dict(row) for row in rows]

    @staticmethod
    async def get(document_id: str) -> Optional[Dict[str, Any]]:
        """Get a document by ID."""
        row = await db.fetchrow(
            """
            SELECT id, conversation_id, filename, file_size, file_type, extracted_text, chunks, metadata, created_at
            FROM documents
            WHERE id = $1
            """,
            uuid.UUID(document_id)
        )

        if row is None:
            return None

        return dict(row)

    @staticmethod
    async def delete(document_id: str):
        """Delete a document."""
        await db.execute(
            """
            DELETE FROM documents
            WHERE id = $1
            """,
            uuid.UUID(document_id)
        )
