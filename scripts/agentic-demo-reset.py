#!/usr/bin/env python3
"""Reset demo data for internal support bot demo."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import delete, select

from app.agentic.adapters.storage.models.agentic_chunk_model import AgenticChunkModel
from app.agentic.adapters.storage.models.agentic_document_model import AgenticDocumentModel
from app.infrastructure.database.session import AsyncSessionLocal


async def reset_demo_data() -> None:
    """Delete all demo documents and their chunks from the database."""
    async with AsyncSessionLocal() as session:
        docs_result = await session.execute(
            select(AgenticDocumentModel).where(
                AgenticDocumentModel.document_metadata["demo"].astext == "true"
            )
        )
        demo_docs = docs_result.scalars().all()
        
        if not demo_docs:
            print("No demo data found. Nothing to reset.")
            return

        doc_ids = [doc.document_id for doc in demo_docs]
        
        chunks_deleted = await session.execute(
            delete(AgenticChunkModel).where(AgenticChunkModel.document_id.in_(doc_ids))
        )
        
        docs_deleted = await session.execute(
            delete(AgenticDocumentModel).where(
                AgenticDocumentModel.document_metadata["demo"].astext == "true"
            )
        )
        
        await session.commit()

        print("✅ Demo data reset complete!")
        print(f"   Deleted {docs_deleted.rowcount} documents and {chunks_deleted.rowcount} chunks")
        print("\n   Document IDs removed:")
        for doc_id in doc_ids:
            print(f"     • {doc_id}")


async def main() -> None:
    try:
        await reset_demo_data()
    except Exception as e:
        print(f"❌ Error resetting demo data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
