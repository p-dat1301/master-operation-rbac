import pytest
from pydantic import ValidationError

from app.agentic.contracts import (
    AccessPolicyMetadata,
    BlockKind,
    CitationMetadata,
    Classification,
    ContentBlock,
    NormalizedDocument,
    SourceMetadata,
    SourceType,
    VisibilityScope,
)


def _pdf_source() -> SourceMetadata:
    return SourceMetadata(
        source_type=SourceType.UPLOADED_FILE,
        mime_type="application/pdf",
        source_uri="/tmp/policy.pdf",
        filename="policy.pdf",
        size_bytes=1024,
        checksum="sha256:demo",
    )


def test_normalized_document_contract_accepts_minimal_source_agnostic_pdf():
    policy = AccessPolicyMetadata(
        classification=Classification.INTERNAL,
        visibility_scope=VisibilityScope.DEPARTMENT,
        allowed_roles=("employee", "manager"),
        department_id=10,
    )
    citation = CitationMetadata(page_number=1, section_path=("HR Policy",), block_anchor="p1")
    block = ContentBlock(
        kind=BlockKind.PARAGRAPH,
        text="Employees may request annual leave with manager approval.",
        order=0,
        citation=citation,
    )

    document = NormalizedDocument(
        document_id="doc-hr-policy",
        source=_pdf_source(),
        access_policy=policy,
        parser_name="text-pdf-parser",
        parser_version="pdf-parser-v1",
        title="HR Policy",
        blocks=(block,),
    )

    assert document.document_id == "doc-hr-policy"
    assert document.source.source_type == SourceType.UPLOADED_FILE
    assert document.source.mime_type == "application/pdf"
    assert document.access_policy.classification == Classification.INTERNAL
    assert document.access_policy.visibility_scope == VisibilityScope.DEPARTMENT
    assert document.blocks[0].citation.page_number == 1
    assert "parser_runtime" not in document.blocks[0].model_dump()


def test_access_policy_fails_closed_when_required_scope_metadata_is_missing():
    with pytest.raises(ValidationError, match="department-scoped policy requires department_id"):
        AccessPolicyMetadata(
            classification=Classification.RESTRICTED,
            visibility_scope=VisibilityScope.DEPARTMENT,
            allowed_roles=("manager",),
        )

    with pytest.raises(ValidationError, match="role-scoped policy requires allowed_roles"):
        AccessPolicyMetadata(
            classification=Classification.RESTRICTED,
            visibility_scope=VisibilityScope.ROLE,
        )


def test_normalized_document_requires_access_metadata():
    with pytest.raises(ValidationError, match="access_policy"):
        NormalizedDocument(
            document_id="doc-missing-policy",
            source=_pdf_source(),
            parser_name="text-pdf-parser",
            parser_version="pdf-parser-v1",
            blocks=(
                ContentBlock(
                    kind=BlockKind.PARAGRAPH,
                    text="Restricted content must not be retrievable without policy metadata.",
                    order=0,
                    citation=CitationMetadata(page_number=1),
                ),
            ),
        )
