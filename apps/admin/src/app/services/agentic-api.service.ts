import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import {
	AgenticChatRequest,
	AgenticChatResponse,
	AgenticConversation,
	AgenticConversationCreateRequest,
	AgenticConversationListResponse,
	AgenticDocument,
	AgenticDocumentListResponse,
	AgenticDocumentUploadPolicy,
	AgenticDocumentUploadResponse,
	AgenticMessageListResponse
} from '../models/agentic.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class AgenticApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	getConversations(): Observable<AgenticConversationListResponse> {
		return this.http.get<AgenticConversationListResponse>(this.buildUrl('/api/v1/agentic/conversations'));
	}

	createConversation(title?: string): Observable<AgenticConversation> {
		const payload: AgenticConversationCreateRequest = title === undefined ? {} : { title };
		return this.http.post<AgenticConversation>(this.buildUrl('/api/v1/agentic/conversations'), payload);
	}

	getConversationMessages(conversationId: string): Observable<AgenticMessageListResponse> {
		return this.http.get<AgenticMessageListResponse>(this.buildUrl(`/api/v1/agentic/conversations/${conversationId}/messages`));
	}

	quickChat(message: string, topK?: number): Observable<AgenticChatResponse> {
		return this.http.post<AgenticChatResponse>(this.buildUrl('/api/v1/agentic/chat'), this.buildChatPayload(message, topK));
	}

	chatInConversation(conversationId: string, message: string, topK?: number): Observable<AgenticChatResponse> {
		return this.http.post<AgenticChatResponse>(
			this.buildUrl(`/api/v1/agentic/conversations/${conversationId}/messages`),
			this.buildChatPayload(message, topK)
		);
	}

	getConversation(conversationId: string): Observable<AgenticConversation> {
		return this.http.get<AgenticConversation>(this.buildUrl(`/api/v1/agentic/conversations/${conversationId}`));
	}

	uploadDocument(file: File, policy?: AgenticDocumentUploadPolicy): Observable<AgenticDocumentUploadResponse> {
		const formData = new FormData();
		formData.append('file', file);
		this.appendUploadPolicy(formData, policy);
		return this.http.post<AgenticDocumentUploadResponse>(this.buildUrl('/api/v1/agentic/documents'), formData);
	}

	getDocuments(): Observable<AgenticDocumentListResponse> {
		return this.http.get<AgenticDocumentListResponse>(this.buildUrl('/api/v1/agentic/documents'));
	}

	getDocument(documentId: string): Observable<AgenticDocument> {
		return this.http.get<AgenticDocument>(this.buildUrl(`/api/v1/agentic/documents/${documentId}`));
	}

	private buildChatPayload(message: string, topK?: number): AgenticChatRequest {
		return topK === undefined ? { message } : { message, top_k: topK };
	}

	private appendUploadPolicy(formData: FormData, policy?: AgenticDocumentUploadPolicy): void {
		if (!policy) {
			return;
		}

		if (policy.classification !== undefined) {
			formData.append('classification', policy.classification);
		}

		if (policy.visibility_scope !== undefined) {
			formData.append('visibility_scope', policy.visibility_scope);
		}

		for (const role of policy.allowed_roles ?? []) {
			formData.append('allowed_roles', role);
		}

		if (policy.department_id !== undefined) {
			formData.append('department_id', String(policy.department_id));
		}
	}
}
