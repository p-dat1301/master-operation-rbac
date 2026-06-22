#!/usr/bin/env python3
"""Seed demo data for internal support bot demo."""
from __future__ import annotations

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select

from app.agentic.adapters.storage.models.agentic_chunk_model import AgenticChunkModel
from app.agentic.adapters.storage.models.agentic_document_model import AgenticDocumentModel
from app.infrastructure.database.session import AsyncSessionLocal


DEMO_DOCUMENTS = [
    {
        "document_id": "demo-doc-vacation-policy",
        "title": "Vacation Policy",
        "source": {
            "source_type": "uploaded_file",
            "mime_type": "text/plain",
            "source_uri": "vacation-policy.txt",
            "filename": "vacation-policy.txt",
            "size_bytes": 512,
            "metadata": {"demo": True},
        },
        "access_policy": {
            "classification": "internal",
            "visibility_scope": "organization",
            "owner_id": 1,
        },
        "status": "indexed",
        "metadata": {"demo": True, "category": "hr"},
        "chunks": [
            {
                "chunk_index": 0,
                "text": "Company Vacation Policy: All full-time employees receive 20 days of paid vacation per year. Vacation days accrue monthly at 1.67 days per month. Employees must request vacation at least 2 weeks in advance through the HR portal.",
            },
            {
                "chunk_index": 1,
                "text": "Vacation Carryover: Unused vacation days can be carried over to the next year, up to a maximum of 5 days. Days exceeding this limit will be forfeited. Vacation payout is available only upon termination.",
            },
            {
                "chunk_index": 2,
                "text": "Sick Leave Policy: Separate from vacation, employees receive 10 sick days per year. Sick leave requires notification to your manager within 2 hours of your shift start time. Medical documentation is required for absences exceeding 3 consecutive days.",
            },
        ],
    },
    {
        "document_id": "demo-doc-eng-onboarding",
        "title": "Engineering Onboarding Guide",
        "source": {
            "source_type": "uploaded_file",
            "mime_type": "text/plain",
            "source_uri": "eng-onboarding.txt",
            "filename": "eng-onboarding.txt",
            "size_bytes": 768,
            "metadata": {"demo": True},
        },
        "access_policy": {
            "classification": "internal",
            "visibility_scope": "organization",
            "owner_id": 1,
        },
        "status": "indexed",
        "metadata": {"demo": True, "category": "engineering"},
        "chunks": [
            {
                "chunk_index": 0,
                "text": "Engineering Onboarding Week 1: Set up your development environment by installing Docker, Node.js 18+, and Python 3.11+. Clone the main repository from GitHub and run 'make setup' to install dependencies. Request VPN access from IT within your first day.",
            },
            {
                "chunk_index": 1,
                "text": "Development Workflow: We follow trunk-based development. Create feature branches from main, keep them short-lived (2-3 days max), and submit pull requests for code review. All PRs require 2 approvals before merging. Run 'make test' before pushing.",
            },
            {
                "chunk_index": 2,
                "text": "Team Rituals: Daily standups at 9:30 AM via Zoom. Sprint planning every other Monday. Retros on alternating Fridays. Join the #engineering Slack channel for announcements. Your onboarding buddy will schedule 1-on-1s during your first month.",
            },
        ],
    },
    {
        "document_id": "demo-doc-security-policy",
        "title": "Security and Access Policy",
        "source": {
            "source_type": "uploaded_file",
            "mime_type": "text/plain",
            "source_uri": "security-policy.txt",
            "filename": "security-policy.txt",
            "size_bytes": 640,
            "metadata": {"demo": True},
        },
        "access_policy": {
            "classification": "internal",
            "visibility_scope": "organization",
            "owner_id": 1,
        },
        "status": "indexed",
        "metadata": {"demo": True, "category": "security"},
        "chunks": [
            {
                "chunk_index": 0,
                "text": "Password Requirements: All company accounts must use passwords with minimum 12 characters, including uppercase, lowercase, numbers, and special characters. Passwords expire every 90 days. Multi-factor authentication (MFA) is mandatory for all systems.",
            },
            {
                "chunk_index": 1,
                "text": "Data Classification: Confidential data (customer PII, financial records) must never be stored on local devices or personal cloud storage. Use company-approved encrypted storage only. Report any suspected data breach to security@company.com immediately.",
            },
        ],
    },
]


async def seed_demo_data() -> None:
    """Seed demo documents and chunks into the database."""
    async with AsyncSessionLocal() as session:
        existing = await session.execute(
            select(AgenticDocumentModel).where(
                AgenticDocumentModel.document_metadata["demo"].astext == "true"
            )
        )
        if existing.scalars().first():
            print("Demo data already exists. Run agentic-demo-reset.py first to clear existing data.")
            return

        created_doc_ids = []
        for doc_spec in DEMO_DOCUMENTS:
            doc = AgenticDocumentModel(
                document_id=doc_spec["document_id"],
                source=doc_spec["source"],
                access_policy=doc_spec["access_policy"],
                status=doc_spec["status"],
                title=doc_spec.get("title"),
                parser_name="demo-seeder",
                chunker_version="demo-v1",
                document_metadata=doc_spec["metadata"],
            )
            session.add(doc)

            for chunk_spec in doc_spec["chunks"]:
                chunk = AgenticChunkModel(
                    chunk_id=f"{doc_spec['document_id']}-chunk-{chunk_spec['chunk_index']}",
                    document_id=doc_spec["document_id"],
                    text=chunk_spec["text"],
                    token_count=len(chunk_spec["text"].split()),
                    chunk_index=chunk_spec["chunk_index"],
                    chunker_version="demo-v1",
                    source_type=doc_spec["source"]["source_type"],
                    mime_type=doc_spec["source"]["mime_type"],
                    citation={
                        "document_id": doc_spec["document_id"],
                        "title": doc_spec.get("title", "Untitled"),
                        "chunk_index": chunk_spec["chunk_index"],
                    },
                    access_policy=doc_spec["access_policy"],
                    chunk_metadata={"demo": True},
                )
                session.add(chunk)

            created_doc_ids.append(doc_spec["document_id"])

        await session.commit()

        print("✅ Demo data seeded successfully!")
        print(f"\nCreated {len(DEMO_DOCUMENTS)} documents:")
        for doc_id in created_doc_ids:
            doc_data = next(d for d in DEMO_DOCUMENTS if d["document_id"] == doc_id)
            chunk_count = len(doc_data["chunks"])
            print(f"  • {doc_id} ({doc_data['title']}) - {chunk_count} chunks")


async def main() -> None:
    try:
        await seed_demo_data()
    except Exception as e:
        print(f"❌ Error seeding demo data: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
