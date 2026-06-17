"""Token-aware chunking for normalized documents."""
from __future__ import annotations

from typing import Any

from app.agentic.chunking.chunk_config import ChunkConfig
from app.agentic.chunking.tokenizer import MODEL_NAME, TokenizerAdapter, get_tokenizer_adapter
from app.agentic.contracts.chunk import DocumentChunk
from app.agentic.contracts.document import ContentBlock, NormalizedDocument


def _merge_metadata(
    document: NormalizedDocument,
    blocks: list[ContentBlock],
    token_count: int,
    tokenizer_policy: str,
) -> dict[str, Any]:
    parser_blocks = [block.block_id for block in blocks]
    section_paths = [list(block.citation.section_path) for block in blocks if block.citation.section_path]
    page_numbers = [block.citation.page_number for block in blocks if block.citation.page_number is not None]
    block_anchors = [block.citation.block_anchor for block in blocks if block.citation.block_anchor is not None]
    block_kinds = [block.kind.value for block in blocks]
    heading_levels = [block.heading_level for block in blocks if block.heading_level is not None]
    return {
        "title": document.title,
        "parser_name": document.parser_name,
        "parser_version": document.parser_version,
        "normalized_version": document.normalized_version,
        "tokenizer_policy": tokenizer_policy,
        "embedding_model": MODEL_NAME,
        "block_ids": parser_blocks,
        "block_orders": [block.order for block in blocks],
        "block_kinds": block_kinds,
        "heading_levels": heading_levels,
        "section_paths": section_paths,
        "page_numbers": page_numbers,
        "block_anchors": block_anchors,
        "token_count": token_count,
    }


class _ChunkAccumulator:
    def __init__(self, block: ContentBlock, tokenizer: TokenizerAdapter) -> None:
        self.blocks = [block]
        self.tokens = tokenizer.encode(block.text)

    def append_block(self, block: ContentBlock, tokenizer: TokenizerAdapter) -> None:
        self.blocks.append(block)
        self.tokens.extend(tokenizer.encode(block.text))

    @property
    def token_count(self) -> int:
        return len(self.tokens)


class DocumentChunker:
    def __init__(self, config: ChunkConfig | None = None, tokenizer: TokenizerAdapter | None = None) -> None:
        self.config = config or ChunkConfig()
        self.tokenizer = tokenizer or get_tokenizer_adapter()

    def chunk_document(self, document: NormalizedDocument) -> tuple[DocumentChunk, ...]:
        chunks: list[DocumentChunk] = []
        chunk_index = 0
        block_index = 0

        while block_index < len(document.blocks):
            block = document.blocks[block_index]
            accumulator = _ChunkAccumulator(block, self.tokenizer)
            block_index += 1

            while block_index < len(document.blocks):
                next_block = document.blocks[block_index]
                next_tokens = self.tokenizer.encode(next_block.text)
                if accumulator.token_count + len(next_tokens) > self.config.max_chunk_tokens:
                    break
                accumulator.append_block(next_block, self.tokenizer)
                block_index += 1

            chunks.extend(self._emit_chunks(document, accumulator, chunk_index))
            chunk_index = len(chunks)

        return tuple(chunks)

    def _emit_chunks(
        self,
        document: NormalizedDocument,
        accumulator: _ChunkAccumulator,
        start_chunk_index: int,
    ) -> list[DocumentChunk]:
        if accumulator.token_count <= self.config.max_chunk_tokens:
            return [self._build_chunk(document, accumulator.blocks, accumulator.tokens, start_chunk_index)]

        window = self.config.max_chunk_tokens
        step = window - self.config.overlap_tokens
        chunks: list[DocumentChunk] = []
        for local_index, start in enumerate(range(0, accumulator.token_count, step)):
            token_window = accumulator.tokens[start : start + window]
            if not token_window:
                continue
            chunks.append(
                self._build_chunk(
                    document,
                    accumulator.blocks,
                    token_window,
                    start_chunk_index + local_index,
                )
            )
            if start + window >= accumulator.token_count:
                break
        return chunks

    def _build_chunk(
        self,
        document: NormalizedDocument,
        blocks: list[ContentBlock],
        tokens: list[str],
        chunk_index: int,
    ) -> DocumentChunk:
        first_block = blocks[0]
        text = self.tokenizer.decode(tokens)
        token_count = len(tokens)
        return DocumentChunk(
            chunk_id=f"{document.document_id}-chunk-{chunk_index:04d}",
            document_id=document.document_id,
            text=text,
            token_count=token_count,
            chunk_index=chunk_index,
            chunker_version=self.config.chunker_version,
            source_type=document.source.source_type.value,
            mime_type=document.source.mime_type,
            citation=first_block.citation,
            access_policy=document.access_policy,
            metadata=_merge_metadata(document, blocks, token_count, self.tokenizer.policy),
        )


def chunk_document(document: NormalizedDocument, config: ChunkConfig | None = None) -> tuple[DocumentChunk, ...]:
    return DocumentChunker(config=config).chunk_document(document)
