"""Resolve access policy from normalized document or chunk contracts."""
from __future__ import annotations

from app.agentic.contracts.access_policy import AccessPolicyMetadata
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import DocumentRecord, NormalizedDocument


class AccessPolicyResolutionError(ValueError):
    pass


def resolve_policy(subject: NormalizedDocument | DocumentChunk | DocumentRecord) -> AccessPolicyMetadata:
    policy = getattr(subject, "access_policy", None)
    if not isinstance(policy, AccessPolicyMetadata):
        raise AccessPolicyResolutionError("missing_access_policy")
    return policy
