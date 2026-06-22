export interface AgenticConversationCreateRequest {
	title?: string | null;
}

export interface AgenticConversation {
	conversation_id: string;
	thread_id: string;
	user_id: number;
	status: string;
	title: string | null;
}

export interface AgenticConversationResponse extends AgenticConversation {}

export interface AgenticConversationListResponse {
	conversations: AgenticConversation[];
}

export interface AgenticMessage {
	turn_id: string;
	conversation_id: string;
	turn_index: number;
	user_message: string;
	assistant_message: string | null;
	assistant_status: string;
	langfuse_trace_id: string | null;
}

export interface AgenticMessageListResponse {
	messages: AgenticMessage[];
}

export interface AgenticChatRequest {
	message: string;
	top_k?: number;
}

export interface AgenticChatResponse {
	conversation_id: string;
	thread_id: string;
	answer: string;
	status: string;
	cited_chunk_ids: string[];
	cited_document_ids: string[];
	citations: Record<string, unknown>[];
}

export interface AgenticDocumentUploadRequest {
	classification?: string;
	visibility_scope?: string;
	allowed_roles?: string[];
	department_id?: number | null;
}

export interface AgenticDocumentUploadResponse {
	ingestion_id: string;
	document_id: string;
	status: string;
	parser_target: string;
	checksum: string;
	filename: string | null;
	mime_type: string;
}

export interface AgenticDocument {
	document_id: string;
	status: string;
	filename: string | null;
	mime_type: string | null;
}

export interface AgenticDocumentListResponse {
	documents: AgenticDocument[];
}

export interface AgenticDocumentUploadPolicy {
	classification?: string;
	visibility_scope?: string;
	allowed_roles?: string[];
	department_id?: number;
}
