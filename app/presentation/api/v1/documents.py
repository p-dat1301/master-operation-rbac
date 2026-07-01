from typing import Optional

from fastapi import APIRouter, Depends, File, Path, Query, UploadFile, status

from app.di.document import (
    provide_create_document,
    provide_delete_document,
    provide_get_document_by_id,
    provide_list_documents,
    provide_search_documents,
    provide_update_document,
)
from app.presentation.dependencies.auth_deps import get_current_user
from app.presentation.dependencies.db_deps import get_db
from app.presentation.schemas.document_schema import (
    DocumentCreateRequest,
    DocumentDetailResponse,

    DocumentListResponse,
    DocumentSearchQuery,
    DocumentUpdateRequest,
    DocumentResponse,
)

router = APIRouter(prefix="/api/v1/documents", tags=["documents"])


@router.get("/", response_model=list[DocumentListResponse])
async def list_documents(
    q: Optional[str] = Query(None),
    db=Depends(get_db),
    actor=Depends(get_current_user),
):
    if q:
        use_case = provide_search_documents(db)
        query = DocumentSearchQuery(q=q)
        dtos = await use_case.execute(actor=actor, query=query)
    else:
        use_case = provide_list_documents(db)
        dtos = await use_case.execute(actor=actor)
    return [DocumentListResponse.model_validate(d) for d in dtos]


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int = Path(...),
    db=Depends(get_db),
    actor=Depends(get_current_user),
):
    use_case = provide_get_document_by_id(db)
    dto = await use_case.execute(actor=actor, document_id=document_id)
    return DocumentDetailResponse.model_validate(dto)


@router.patch("/{document_id}", response_model=DocumentDetailResponse)
async def update_document(
    data: DocumentUpdateRequest,
    document_id: int = Path(...),
    db=Depends(get_db),
    actor=Depends(get_current_user),
):
    use_case = provide_update_document(db)
    dto = await use_case.execute(actor=actor, document_id=document_id, payload=data)
    return DocumentDetailResponse.model_validate(dto)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int = Path(...),
    db=Depends(get_db),
    actor=Depends(get_current_user),
):
    use_case = provide_delete_document(db)
    await use_case.execute(actor=actor, document_id=document_id)


@router.post("/", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def create_document(
    file: UploadFile = File(...),
    request_data: DocumentCreateRequest = Depends(DocumentCreateRequest.as_form),
    db=Depends(get_db),
    actor=Depends(get_current_user),
):
    use_case = provide_create_document(db)
    file_bytes = await file.read()

    dto = await use_case.execute(
        actor=actor,
        data=request_data,
        file_bytes=file_bytes,
        filename=file.filename or "unnamed",
        mime_type=file.content_type or "application/octet-stream",
    )

    return dto
