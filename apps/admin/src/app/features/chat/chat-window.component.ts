import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnInit, computed, inject, signal, viewChild } from '@angular/core';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';

import { NzModalModule } from 'ng-zorro-antd/modal';
import { AgenticApiService } from '../../services/agentic-api.service';
import { runAdminAsync } from '../../shared/async-state';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';
import { AgenticChatResponse, AgenticConversation } from '../../models/agentic.models';

interface ChatMessage {
	role: 'user' | 'assistant';
	content: string;
	meta?: ChatResponseMeta;
}

interface ChatResponseMeta {
	status: string;
	conversationId: string;
	threadId: string;
	citedChunkIds: string[];
	citedDocumentIds: string[];
	citations: Record<string, unknown>[];
}

const TOP_K_MIN = 1;
const TOP_K_MAX = 10;

@Component({
	selector: 'app-chat-window',
	standalone: true,
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzIconModule, NzInputModule, NzSpinModule, NzTagModule, NzTooltipModule, NzModalModule],
	templateUrl: './chat-window.component.html',
	styleUrls: ['../../shared/admin-page-styles.css', './chat-window.component.css']
})
export class ChatWindowComponent implements OnInit {
	private readonly agenticApi = inject(AgenticApiService);
	private readonly message = inject(NzMessageService);

	readonly topKMin = TOP_K_MIN;
	readonly topKMax = TOP_K_MAX;
	readonly conversations = signal<AgenticConversation[]>([]);
	readonly selectedConversationId = signal('');
	readonly loadingConversations = signal(false);
	readonly conversationError = signal('');
	readonly chatError = signal('');
	readonly permissionError = signal('');
	readonly messages = signal<ChatMessage[]>([]);
	readonly loading = signal(false);
	readonly filteredConversations = signal<AgenticConversation[]>([]);
	topKInput: number | null = 5;
	searchQuery = '';
	readonly selectedConversation = computed(() => this.conversations().find(conversation => conversation.conversation_id === this.selectedConversationId()) ?? null);
	readonly conversationLoadFailed = computed(() => !this.loadingConversations() && this.conversationError().length > 0);
	inputMessage = '';
	messagesContainer = viewChild<ElementRef>('messagesContainer');
	showCreateModal = false;
	newConversationTitle = '';

	ngOnInit(): void {
		void this.loadConversations();
	}

	trackConversation = (_: number, conversation: AgenticConversation): string => conversation.conversation_id;

	shortId(value: string | null | undefined): string {
		if (!value) return '—';
		return value.length > 12 ? `${value.slice(0, 8)}…${value.slice(-4)}` : value;
	}

	statusColor(status: string): string {
		const colors: Record<string, string> = { active: 'processing', open: 'processing', completed: 'success', closed: 'default', failed: 'error', error: 'error' };
		return colors[status?.toLowerCase()] ?? 'blue';
	}

	newQuickChat(): void {
		this.selectedConversationId.set('');
		this.inputMessage = '';
		this.chatError.set('');
		this.permissionError.set('');
		this.messages.set([]);
	}

	createNewConversation(): void {
		this.newConversationTitle = 'Cuộc hội thoại mới';
		this.showCreateModal = true;
	}

	closeCreateModal(): void {
		this.showCreateModal = false;
	}

	async submitNewConversation(): Promise<void> {
		const cleanTitle = this.newConversationTitle.trim() || 'Cuộc hội thoại mới';
		this.closeCreateModal();
		
		await runAdminAsync(this.agenticApi.createConversation(cleanTitle), {
			pending: this.loadingConversations,
			fallbackMessage: 'Không thể tạo cuộc hội thoại mới.',
			onSuccess: async (conversation) => {
				this.message.success('Tạo cuộc hội thoại mới thành công.');
				await this.loadConversations();
				await this.selectConversation(conversation.conversation_id);
			},
			onError: (feedback, fallback) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallback;
				this.message.error(message);
			}
		});
	}

	filterConversations(): void {
		const query = this.searchQuery.trim().toLowerCase();
		this.filteredConversations.set(!query
			? this.conversations()
			: this.conversations().filter(conversation => {
				const haystack = `${conversation.title ?? ''} ${conversation.conversation_id}`.toLowerCase();
				return haystack.includes(query);
			})
		);
	}

	async selectConversation(conversationId: string): Promise<void> {
		this.conversationError.set('');
		this.chatError.set('');
		this.permissionError.set('');
		this.selectedConversationId.set(conversationId || '');
		
		if (conversationId) {
			await this.loadConversationMessages(conversationId);
		} else {
			this.messages.set([]);
		}
	}

	async loadConversationMessages(conversationId: string): Promise<void> {
		this.messages.set([]);
		await runAdminAsync(this.agenticApi.getConversationMessages(conversationId), {
			pending: this.loading,
			fallbackMessage: 'Không thể tải lịch sử cuộc hội thoại.',
			onSuccess: (response) => {
				const history: ChatMessage[] = [];
				for (const msg of response.messages ?? []) {
					if (msg.user_message) {
						history.push({ role: 'user', content: msg.user_message });
					}
					if (msg.assistant_message) {
						history.push({
							role: 'assistant',
							content: msg.assistant_message,
							meta: {
								status: msg.assistant_status || 'unknown',
								conversationId: conversationId,
								threadId: '',
								citedChunkIds: [],
								citedDocumentIds: [],
								citations: []
							}
						});
					}
				}
				this.messages.set(history);
				this.scrollToBottom();
			},
			onError: (feedback, fallback) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallback;
				this.message.error(message);
			}
		});
	}

	validateTopK(): void {
		const value = this.topKInput;
		if (value == null || Number.isNaN(value)) {
			this.topKInput = null;
			return;
		}
		const next = Math.trunc(value);
		if (next < this.topKMin || next > this.topKMax) {
			this.topKInput = Math.min(this.topKMax, Math.max(this.topKMin, next));
		}
	}


	canSend(): boolean {
		return this.inputMessage.trim().length > 0 && !this.loading() && this.isTopKValid();
	}

	onEnterPress(event: Event): void {
		const keyboardEvent = event as KeyboardEvent;
		if (!keyboardEvent.shiftKey && this.canSend()) {
			keyboardEvent.preventDefault();
			void this.sendMessage();
		}
	}

	async sendMessage(): Promise<void> {
		if (!this.canSend()) return;
		const userMessage = this.inputMessage.trim();
		const topK = this.topKInput ?? undefined;
		this.inputMessage = '';
		this.messages.update(msgs => [...msgs, { role: 'user', content: userMessage }]);
		this.scrollToBottom();
		const selected = this.selectedConversationId();
		const request = selected ? this.agenticApi.chatInConversation(selected, userMessage, topK) : this.agenticApi.quickChat(userMessage, topK);
		const response = await runAdminAsync(request, {
			pending: this.loading,
			fallbackMessage: 'Failed to send message',
			onSuccess: (value) => {
				this.chatError.set('');
				this.permissionError.set('');
				this.appendResponse(value);
			},
			onError: (feedback, fallback) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallback;
				this.chatError.set(message);
				this.messages.update(msgs => [...msgs, { role: 'assistant', content: `Error: ${message}` }]);
				this.message.error(message);
			}
		});
		if (!response) {
			this.inputMessage = userMessage;
		}
	}


	private appendResponse(response: AgenticChatResponse): void {
		this.messages.update(msgs => [...msgs, { role: 'assistant', content: response.answer, meta: { status: response.status, conversationId: response.conversation_id, threadId: response.thread_id, citedChunkIds: response.cited_chunk_ids ?? [], citedDocumentIds: response.cited_document_ids ?? [], citations: response.citations ?? [] } }]);
		this.scrollToBottom();
	}

	private isTopKValid(): boolean {
		const value = this.topKInput;
		return value !== null && Number.isInteger(value) && value >= this.topKMin && value <= this.topKMax;
	}

	async loadConversations(): Promise<void> {
		await runAdminAsync(this.agenticApi.getConversations(), {
			pending: this.loadingConversations,
			fallbackMessage: 'Failed to load conversations.',
				onSuccess: data => {
					this.conversations.set(data.conversations ?? []);
					this.filterConversations();
					if (this.selectedConversationId() && !this.selectedConversation()) {
					this.permissionError.set('The selected conversation is no longer available or you do not have access.');
				}
			},
			onError: (feedback, fallback) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallback;
				this.conversationError.set(message);
				this.messages.set([]);
				this.message.error(message);
			}
		});
	}

	private scrollToBottom(): void {
		setTimeout(() => { const container = this.messagesContainer()?.nativeElement; if (container) container.scrollTop = container.scrollHeight; }, 100);
	}
}
