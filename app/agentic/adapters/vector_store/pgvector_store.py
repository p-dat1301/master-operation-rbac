"""pgvector-backed vector store adapter for indexed agentic chunks."""
from __future__ import annotations

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.indexing.index_document import VectorStoreAdapter
from app.infrastructure.database.models.agentic_chunk_embedding_model import AgenticChunkEmbeddingModel, EMBEDDING_DIMENSION


class PGVectorStoreAdapter(VectorStoreAdapter):
    """Persist embeddings in PostgreSQL/pgvector without owning transaction commit."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert(self, chunks: tuple[DocumentChunk, ...], embeddings: list[list[float]], metadata: dict[str, object]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings length mismatch")
        if not chunks:
            return

        embedding_model = _metadata_string(metadata, "embedding_model", default="unknown")
        index_version = _metadata_string(metadata, "index_version", default="index-v1")
        rows: list[dict[str, object]] = []
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            if len(embedding) != EMBEDDING_DIMENSION:
                raise ValueError(
                    f"embedding dimension mismatch for chunk {chunk.chunk_id}: expected {EMBEDDING_DIMENSION}, got {len(embedding)}"
                )
            rows.append(
                {
                    "chunk_id": chunk.chunk_id,
                    "document_id": chunk.document_id,
                    "embedding": embedding,
                    "embedding_model": embedding_model,
                    "index_version": index_version,
                    "metadata": metadata,
                }
            )

        stmt = insert(AgenticChunkEmbeddingModel.__table__).values(rows)
        update_values = {key: stmt.excluded[key] for key in rows[0] if key != "chunk_id"}
        await self._session.execute(stmt.on_conflict_do_update(index_elements=["chunk_id"], set_=update_values))
        await self._session.flush()

    async def delete_by_document(self, document_id: str) -> None:
        await self._session.execute(
            delete(AgenticChunkEmbeddingModel).where(AgenticChunkEmbeddingModel.document_id == document_id)
        )
        await self._session.flush()


def _metadata_string(metadata: dict[str, object], key: str, *, default: str) -> str:
    value = metadata.get(key)
    return value if isinstance(value, str) and value else default
