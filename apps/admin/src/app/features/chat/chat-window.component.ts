import { CommonModule } from '@angular/common';
import { Component, ElementRef, OnInit, computed, inject, signal, viewChild } from '@angular/core';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzSelectModule } from 'ng-zorro-antd/select';

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
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzIconModule, NzInputModule, NzSelectModule, NzSpinModule],
	template: `
		<section class="page-root chat-window" data-testid="chat-window-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Agent / AI</p>
					<h2>Chat</h2>
					<p class="subtitle">Quick chat is the default. Select a conversation to continue a thread.</p>
				</div>
				<div class="header-meta text-secondary">
					<span class="text-muted">Mode</span>
					<strong class="text-strong">{{ selectedConversation() ? 'Conversation-aware' : 'Quick chat' }}</strong>
				</div>
			</div>

			<nz-card class="surface-card surface-card-strong chat-controls" [nzBordered]="false">
				<div *ngIf="conversationLoadFailed()" class="state-panel error-state" data-testid="chat-conversation-load-error">
					<span nz-icon nzType="warning"></span>
					<div><strong>Conversation loading failed.</strong><p>{{ conversationError() }}</p></div>
					<button nz-button nzSize="small" nzType="primary" (click)="loadConversations()">Try again</button>
				</div>
				<div class="control-grid">
					<label class="form-field">
						<span class="text-secondary">Conversation</span>
						<nz-select
							[(ngModel)]="selectedConversationId"
							(ngModelChange)="onConversationChange($event)"
							nzAllowClear
							nzPlaceHolder="Quick chat"
							[nzLoading]="loadingConversations()"
							data-testid="conversation-select"
						>
							<nz-option [nzValue]="''" nzLabel="Quick chat"></nz-option>
							<nz-option *ngFor="let conversation of conversations(); trackBy: trackConversation" [nzValue]="conversation.conversation_id" [nzLabel]="conversationLabel(conversation)"></nz-option>
						</nz-select>
					</label>

					<label class="form-field">
						<span class="text-secondary">top_k</span>
						<input
							nz-input
							type="number"
							[min]="topKMin"
							[max]="topKMax"
							step="1"
							[(ngModel)]="topKInput"
							(ngModelChange)="validateTopK()"
							data-testid="chat-top-k-input"
						/>
						<div class="field-help text-muted">Backend range {{ topKMin }}–{{ topKMax }}</div>
					</label>
				</div>

				<div class="status-row">
					<div class="status-pill text-secondary">
						<span class="text-muted">Selected conversation</span>
						<strong class="text-strong">{{ selectedConversation()?.title || selectedConversation()?.conversation_id || 'None' }}</strong>
					</div>
					@if (conversationError()) {
						<div class="inline-error">{{ conversationError() }}</div>
					}
				</div>
			</nz-card>

			<div class="chat-messages surface-card surface-card-strong" #messagesContainer>
				@if (chatError()) {
					<div class="state-panel error-state" data-testid="chat-send-error">
						<span nz-icon nzType="warning"></span>
						<div><strong>Message failed.</strong><p>{{ chatError() }}</p></div>
					</div>
				}
				@if (messages().length === 0 && !loadingConversations()) {
					<div class="empty-state">
						<p>Start a conversation by typing a message below.</p>
					</div>
				}
				@for (msg of messages(); track $index) {
					<div class="message" [class.user]="msg.role === 'user'" [class.assistant]="msg.role === 'assistant'">
						<div class="message-role">{{ msg.role === 'user' ? 'You' : 'Assistant' }}</div>
						<div class="message-content">{{ msg.content }}</div>
						@if (msg.meta) {
							<div class="response-meta text-muted">
								<div><span class="text-secondary">Status:</span> <span class="text-strong">{{ msg.meta.status }}</span></div>
								<div><span class="text-secondary">Conversation:</span> <span class="text-strong">{{ msg.meta.conversationId }}</span></div>
								<div><span class="text-secondary">Thread:</span> <span class="text-strong">{{ msg.meta.threadId }}</span></div>
								@if (msg.meta.citedChunkIds.length > 0) { <div><span class="text-secondary">Chunk IDs:</span> {{ msg.meta.citedChunkIds.join(', ') }}</div> }
								@if (msg.meta.citedDocumentIds.length > 0) { <div><span class="text-secondary">Document IDs:</span> {{ msg.meta.citedDocumentIds.join(', ') }}</div> }
								@if (msg.meta.citations.length > 0) {
									<div>
										<div class="text-secondary">Citations</div>
										<div class="citation-list">
											@for (citation of msg.meta.citations; track $index) {
												<pre class="citation-item">{{ citation | json }}</pre>
											}
										</div>
									</div>
								}
							</div>
						}
					</div>
				}
				@if (loadingConversations() && messages().length === 0) {
					<div class="loading-block" data-testid="chat-conversations-loading"><nz-spin nzSimple></nz-spin><span>Loading available conversations…</span></div>
				}
				@if (loading()) {
					<div class="message assistant loading" data-testid="chat-response-loading">
						<div class="message-role">Assistant</div>
						<div class="message-content">Thinking...</div>
					</div>
				}
			</div>

			<div *ngIf="permissionError()" class="state-panel error-state" data-testid="chat-permission-error">
				<span nz-icon nzType="lock"></span>
				<div><strong>Conversation unavailable.</strong><p>{{ permissionError() }}</p></div>
			</div>

			<div class="chat-input surface-card surface-card-strong">
				<label class="form-field message-field">
					<span class="text-secondary">Message</span>
					<textarea nz-input [(ngModel)]="inputMessage" placeholder="Type your message..." [disabled]="loading()" (keydown.enter)="onEnterPress($event)" rows="4"></textarea>
				</label>
				<div class="input-actions">
					<div class="text-muted">{{ selectedConversation() ? 'Sending to selected conversation.' : 'Sending as quick chat.' }}</div>
					<button nz-button nzType="primary" class="action-primary" [disabled]="!canSend()" (click)="sendMessage()" data-testid="chat-send-btn">Send</button>
				</div>
			</div>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.chat-window { height: 100%; max-height: calc(100vh - 8rem); gap: 1rem; }
		.chat-controls { padding: 1rem 1.1rem; }
		.control-grid { display:grid; grid-template-columns: 1fr 160px; gap: 1rem; align-items:end; }
		.status-row { display:flex; justify-content:space-between; gap:1rem; margin-top: .9rem; flex-wrap:wrap; }
		.status-pill { display:flex; gap:.5rem; align-items:center; }
		.inline-error { color: var(--admin-action-danger); }
		.field-help { font-size: .8rem; }
		.chat-messages { flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 1rem; padding: 1rem; min-height: 400px; }
		.empty-state { display:flex; align-items:center; justify-content:center; height:100%; color: var(--admin-text-muted); }
		.message { display:flex; flex-direction:column; gap:.5rem; padding:1rem; border-radius: .9rem; max-width: 85%; }
		.message.user { align-self:flex-end; background: rgba(56,189,248,.12); border:1px solid rgba(125,211,252,.2); }
		.message.assistant { align-self:flex-start; background: rgba(8,15,28,.78); border:1px solid var(--admin-border-subtle); }
		.message-role { font-size:.75rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; color: var(--admin-action-primary); }
		.message.assistant .message-role { color: var(--admin-text-muted); }
		.message-content { color: var(--admin-text-primary); line-height:1.6; white-space:pre-wrap; word-break:break-word; }
		.response-meta { display:grid; gap:.35rem; padding-top:.35rem; border-top:1px solid var(--admin-border-subtle); font-size:.84rem; }
		.citation-list { display:grid; gap:.5rem; margin-top:.35rem; }
		.citation-item { margin:0; padding:.65rem .75rem; border-radius:.7rem; background: rgba(15,23,42,.45); color: var(--admin-text-secondary); overflow:auto; }
		.chat-input { flex-shrink:0; display:grid; gap: .75rem; padding: 1rem 1.1rem; }
		.message-field textarea { resize:none; min-height: 6rem; }
		.input-actions { display:flex; align-items:center; justify-content:space-between; gap:1rem; flex-wrap:wrap; }
		@media (max-width: 960px) { .control-grid { grid-template-columns: 1fr; } }
	`]
})
export class ChatWindowComponent implements OnInit {
	private readonly agenticApi = inject(AgenticApiService);
	private readonly message = inject(NzMessageService);

	readonly topKMin = TOP_K_MIN;
	readonly topKMax = TOP_K_MAX;
	readonly conversations = signal<AgenticConversation[]>([]);
	selectedConversationId = '';
	readonly loadingConversations = signal(false);
	readonly conversationError = signal('');
	readonly chatError = signal('');
	readonly permissionError = signal('');
	readonly messages = signal<ChatMessage[]>([]);
	readonly loading = signal(false);
	topKInput: number | null = 5;
	readonly selectedConversation = computed(() => this.conversations().find(conversation => conversation.conversation_id === this.selectedConversationId) ?? null);
	readonly conversationLoadFailed = computed(() => !this.loadingConversations() && this.conversationError().length > 0);
	inputMessage = '';
	messagesContainer = viewChild<ElementRef>('messagesContainer');

	ngOnInit(): void {
		void this.loadConversations();
	}

	trackConversation = (_: number, conversation: AgenticConversation): string => conversation.conversation_id;

	conversationLabel(conversation: AgenticConversation): string {
		return conversation.title?.trim() ? `${conversation.title} · ${conversation.conversation_id}` : conversation.conversation_id;
	}

	onConversationChange(conversationId: string): void {
		this.conversationError.set('');
		this.chatError.set('');
		this.permissionError.set('');
		this.selectedConversationId = conversationId || '';
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
		const selected = this.selectedConversationId;
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
				if (this.selectedConversationId && !this.selectedConversation()) {
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
