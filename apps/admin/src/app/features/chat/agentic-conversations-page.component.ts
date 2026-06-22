import { CommonModule } from '@angular/common';
import { ChangeDetectionStrategy, Component, OnInit, computed, inject, signal } from '@angular/core';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDescriptionsModule } from 'ng-zorro-antd/descriptions';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzTagModule } from 'ng-zorro-antd/tag';

import { AgenticConversation, AgenticMessage } from '../../models/agentic.models';
import { AgenticApiService } from '../../services/agentic-api.service';
import { runAdminAsync } from '../../shared/async-state';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

const STATUS_COLOR: Record<string, string> = {
	active: 'processing',
	open: 'processing',
	completed: 'success',
	closed: 'default',
	failed: 'error',
	error: 'error'
};

@Component({
	selector: 'app-agentic-conversations-page',
	standalone: true,
	imports: [CommonModule, NzButtonModule, NzCardModule, NzDescriptionsModule, NzIconModule, NzSpinModule, NzTagModule],
	changeDetection: ChangeDetectionStrategy.OnPush,
	template: `
		<section class="page-root" data-testid="agentic-conversations-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Agentic workspace</p>
					<h2>Conversations</h2>
					<p class="subtitle">Persisted agent threads, metadata, and message history.</p>
				</div>
				<button nz-button nzType="default" (click)="loadConversations()" [disabled]="listLoading()" data-testid="reload-conversations-btn">
					<span nz-icon nzType="sync"></span> Reload
				</button>
			</div>

			<div class="conversation-layout">
				<nz-card class="surface-card list-card" [nzBordered]="false">
					<div class="section-heading">
						<div>
							<p class="text-action">Conversation list</p>
							<p class="text-secondary">{{ conversations().length }} persisted thread{{ conversations().length === 1 ? '' : 's' }}</p>
						</div>
					</div>

					<nz-spin [nzSpinning]="listLoading()">
						<div *ngIf="listError()" class="state-panel error-state" data-testid="conversation-list-error">
							<span nz-icon nzType="warning"></span>
							<div><strong>Could not load conversations.</strong><p>{{ listError() }}</p></div>
							<button nz-button nzSize="small" nzType="primary" (click)="loadConversations()">Try again</button>
						</div>

						<div *ngIf="!listError() && !listLoading() && conversations().length === 0" class="state-panel" data-testid="conversation-list-empty">
							<span nz-icon nzType="inbox"></span>
							<div><strong>No conversations yet.</strong><p>Persisted agent conversations will appear here after users start chatting.</p></div>
						</div>

						<div *ngIf="!listError() && !listLoading() && selectedConversationId() && !selectedExistsInList()" class="state-panel error-state" data-testid="conversation-list-not-found">
							<span nz-icon nzType="disconnect"></span>
							<div><strong>Conversation not found.</strong><p>The selected thread is missing or was removed. Reload the list and choose another conversation.</p></div>
						</div>

						<div *ngIf="!listError() && conversations().length > 0" class="conversation-list" data-testid="conversation-list">
							<button
								*ngFor="let conversation of conversations(); trackBy: trackConversation"
								class="conversation-row"
								[class.selected]="selectedConversationId() === conversation.conversation_id"
								(click)="selectConversation(conversation.conversation_id)"
								[attr.data-testid]="'conversation-row-' + conversation.conversation_id"
							>
								<span class="conversation-title">{{ conversation.title || 'Untitled conversation' }}</span>
								<span class="conversation-meta">{{ shortId(conversation.conversation_id) }} · thread {{ shortId(conversation.thread_id) }}</span>
								<nz-tag class="status-tag" [nzColor]="statusColor(conversation.status)">{{ conversation.status || 'unknown' }}</nz-tag>
							</button>
						</div>
					</nz-spin>
				</nz-card>

				<nz-card class="surface-card detail-card" [nzBordered]="false">
					<div class="section-heading">
						<div>
							<p class="text-action">Detail</p>
							<p class="text-secondary">Conversation metadata and persisted turns.</p>
						</div>
					</div>

					<div *ngIf="!selectedConversationId()" class="state-panel" data-testid="conversation-detail-empty">
						<span nz-icon nzType="message"></span>
						<div><strong>Select a conversation.</strong><p>Choose a persisted thread from the list to inspect its messages.</p></div>
					</div>

					<ng-container *ngIf="selectedConversationId()">
						<div *ngIf="detailLoading()" class="loading-block" data-testid="conversation-detail-loading"><nz-spin nzSimple></nz-spin><span>Loading conversation detail…</span></div>

						<div *ngIf="notFound()" class="state-panel error-state" data-testid="conversation-not-found">
							<span nz-icon nzType="disconnect"></span>
							<div><strong>Conversation not found.</strong><p>The selected conversation may have been removed or is no longer accessible.</p></div>
						</div>

						<div *ngIf="detailError() && !notFound()" class="state-panel error-state" data-testid="conversation-detail-error">
							<span nz-icon nzType="warning"></span>
							<div><strong>Could not load detail.</strong><p>{{ detailError() }}</p></div>
							<button nz-button nzSize="small" nzType="primary" (click)="reloadSelected()">Try again</button>
						</div>

						<ng-container *ngIf="selectedConversation() as conversation">
							<nz-descriptions nzSize="small" [nzColumn]="1" nzBordered data-testid="conversation-detail">
								<nz-descriptions-item nzTitle="Title">{{ conversation.title || 'Untitled conversation' }}</nz-descriptions-item>
								<nz-descriptions-item nzTitle="Conversation ID">{{ conversation.conversation_id }}</nz-descriptions-item>
								<nz-descriptions-item nzTitle="Thread ID">{{ conversation.thread_id || '—' }}</nz-descriptions-item>
								<nz-descriptions-item nzTitle="User ID">{{ conversation.user_id }}</nz-descriptions-item>
								<nz-descriptions-item nzTitle="Status"><nz-tag [nzColor]="statusColor(conversation.status)">{{ conversation.status || 'unknown' }}</nz-tag></nz-descriptions-item>
							</nz-descriptions>
						</ng-container>

						<div class="messages-heading"><p class="text-action">Message history</p><p class="text-secondary">{{ messages().length }} persisted turn{{ messages().length === 1 ? '' : 's' }}</p></div>

						<div *ngIf="messagesLoading()" class="loading-block" data-testid="conversation-messages-loading"><nz-spin nzSimple></nz-spin><span>Loading message history…</span></div>

						<div *ngIf="messagesError()" class="state-panel error-state" data-testid="conversation-messages-error">
							<span nz-icon nzType="warning"></span>
							<div><strong>Could not load messages.</strong><p>{{ messagesError() }}</p></div>
							<button nz-button nzSize="small" nzType="primary" (click)="reloadSelected()">Try again</button>
						</div>

						<div *ngIf="!messagesLoading() && !messagesError() && selectedConversation() && messages().length === 0" class="state-panel" data-testid="conversation-messages-empty">
							<span nz-icon nzType="comment"></span>
							<div><strong>No persisted messages.</strong><p>This conversation exists, but no user or assistant turns have been saved yet.</p></div>
						</div>

						<div *ngIf="!messagesError() && !messagesLoading() && messages().length > 0" class="message-history" data-testid="conversation-message-history">
							<article *ngFor="let message of messages(); trackBy: trackMessage" class="turn-card">
								<div class="turn-header"><span>Turn {{ message.turn_index }}</span><span class="text-muted">{{ message.turn_id }}</span></div>
								<div class="bubble user"><span>User</span><p>{{ message.user_message }}</p></div>
								<div class="bubble assistant"><span>Assistant · {{ message.assistant_status || 'unknown' }}</span><p>{{ message.assistant_message || 'No assistant response persisted.' }}</p></div>
								<p *ngIf="message.langfuse_trace_id" class="trace text-muted">Trace: {{ message.langfuse_trace_id }}</p>
							</article>
						</div>
					</ng-container>
				</nz-card>
			</div>
		</section>
	`,
	styles: [
		ADMIN_PAGE_COMMON_STYLES,
		`
			.conversation-layout { display:grid; grid-template-columns:minmax(280px, .8fr) minmax(0, 1.35fr); gap:1.25rem; align-items:start }
			.section-heading { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; margin-bottom:1rem }
			.list-card, .detail-card { min-height:28rem }
			.conversation-list { display:grid; gap:.7rem }
			.conversation-row { width:100%; text-align:left; border:1px solid var(--admin-border-subtle); border-radius:1rem; padding:.9rem; display:grid; gap:.35rem; background:var(--admin-surface-table); cursor:pointer; transition:border-color .18s ease, transform .18s ease, background .18s ease }
			.conversation-row:hover, .conversation-row.selected { border-color:rgba(125,211,252,.55); background:rgba(14,165,233,.12); transform:translateY(-1px) }
			.conversation-title { color:var(--admin-text-primary); font-weight:700; line-height:1.25 }
			.conversation-meta { color:var(--admin-text-muted); font-size:.78rem; overflow-wrap:anywhere }
			.status-tag { width:max-content; margin-top:.25rem }
			.state-panel { border:1px dashed var(--admin-border-subtle); border-radius:1rem; padding:1rem; display:flex; align-items:flex-start; gap:.8rem; color:var(--admin-text-secondary); background:var(--admin-surface-table) }
			.state-panel strong { color:var(--admin-text-primary) }
			.state-panel p { margin:.15rem 0 0 }
			.state-panel [nz-icon] { color:var(--admin-action-primary); font-size:1.25rem; margin-top:.15rem }
			.error-state { border-color:rgba(248,113,113,.3); background:rgba(127,29,29,.12) }
			.error-state [nz-icon] { color:var(--admin-action-danger) }
			.loading-block { min-height:5rem; display:flex; align-items:center; justify-content:center; gap:.75rem; color:var(--admin-text-secondary) }
			.messages-heading { margin:1.25rem 0 .85rem; padding-top:1rem; border-top:1px solid var(--admin-border-subtle) }
			.message-history { display:grid; gap:1rem }
			.turn-card { border:1px solid var(--admin-border-subtle); border-radius:1.1rem; padding:1rem; background:var(--admin-surface-table) }
			.turn-header { display:flex; justify-content:space-between; gap:1rem; flex-wrap:wrap; margin-bottom:.8rem; color:var(--admin-action-primary); font-size:.78rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase }
			.bubble { border-radius:1rem; padding:.8rem .9rem; margin-top:.65rem }
			.bubble span { display:block; margin-bottom:.35rem; font-size:.72rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase }
			.bubble p { margin:0; white-space:pre-wrap; overflow-wrap:anywhere; color:var(--admin-text-strong) }
			.bubble.user { background:rgba(56,189,248,.12); border:1px solid rgba(56,189,248,.18) }
			.bubble.user span { color:var(--admin-action-primary) }
			.bubble.assistant { background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.16) }
			.bubble.assistant span { color:var(--admin-action-success) }
			.trace { margin:.7rem 0 0; font-size:.78rem; overflow-wrap:anywhere }
			@media (max-width: 980px) { .conversation-layout { grid-template-columns:1fr } }
		`
	]
})
export class AgenticConversationsPageComponent implements OnInit {
	private readonly agenticApi = inject(AgenticApiService);
	private readonly message = inject(NzMessageService);

	readonly conversations = signal<AgenticConversation[]>([]);
	readonly selectedConversation = signal<AgenticConversation | null>(null);
	readonly selectedConversationId = signal<string | null>(null);
	readonly messages = signal<AgenticMessage[]>([]);

	readonly listLoading = signal(false);
	readonly detailLoading = signal(false);
	readonly messagesLoading = signal(false);
	readonly listError = signal<string | null>(null);
	readonly detailError = signal<string | null>(null);
	readonly messagesError = signal<string | null>(null);
	readonly notFound = signal(false);

	readonly selectedExistsInList = computed(() => this.conversations().some((item) => item.conversation_id === this.selectedConversationId()));

	ngOnInit(): void {
		this.loadConversations();
	}

	async loadConversations(): Promise<void> {
		this.listError.set(null);
		await runAdminAsync(this.agenticApi.getConversations(), {
			pending: this.listLoading,
			fallbackMessage: 'Could not load agentic conversations.',
			onSuccess: (response) => {
				this.conversations.set(response.conversations ?? []);
				if (this.selectedConversationId() && !this.selectedExistsInList()) {
					this.notFound.set(true);
					this.detailError.set('The selected conversation is no longer available in the refreshed list.');
					this.messagesError.set('The selected conversation is no longer available in the refreshed list.');
					this.selectedConversation.set(null);
					this.messages.set([]);
				}
			},
			onError: (feedback, fallbackMessage) => {
				const errorMessage = feedback.action === 'toast-only' ? feedback.message : fallbackMessage;
				this.listError.set(errorMessage);
				this.message.error(errorMessage);
			}
		});
	}

	selectConversation(conversationId: string): void {
		if (this.selectedConversationId() === conversationId && (this.detailLoading() || this.messagesLoading())) {
			return;
		}
		this.selectedConversationId.set(conversationId);
		this.reloadSelected();
	}

	reloadSelected(): void {
		const conversationId = this.selectedConversationId();
		if (!conversationId) {
			return;
		}
		void this.loadConversationDetail(conversationId);
		void this.loadConversationMessages(conversationId);
	}

	trackConversation(_: number, conversation: AgenticConversation): string {
		return conversation.conversation_id;
	}

	trackMessage(_: number, messageItem: AgenticMessage): string {
		return messageItem.turn_id;
	}

	statusColor(status: string): string {
		return STATUS_COLOR[status?.toLowerCase()] ?? 'blue';
	}

	shortId(value: string | null | undefined): string {
		if (!value) {
			return '—';
		}
		return value.length > 12 ? `${value.slice(0, 8)}…${value.slice(-4)}` : value;
	}

	private async loadConversationDetail(conversationId: string): Promise<void> {
		this.detailError.set(null);
		this.notFound.set(false);
		this.selectedConversation.set(null);
		this.messages.set([]);
		await runAdminAsync(this.agenticApi.getConversation(conversationId), {
			pending: this.detailLoading,
			fallbackMessage: 'Could not load conversation detail.',
			onSuccess: (conversation) => this.selectedConversation.set(conversation),
			onError: (feedback, fallbackMessage) => {
				const errorMessage = feedback.action === 'toast-only' ? feedback.message : fallbackMessage;
				this.detailError.set(errorMessage);
				this.notFound.set(this.isNotFoundMessage(errorMessage));
				this.message.error(errorMessage);
			}
		});
	}

	private async loadConversationMessages(conversationId: string): Promise<void> {
		this.messagesError.set(null);
		this.messages.set([]);
		await runAdminAsync(this.agenticApi.getConversationMessages(conversationId), {
			pending: this.messagesLoading,
			fallbackMessage: 'Could not load conversation messages.',
			onSuccess: (response) => this.messages.set(response.messages ?? []),
			onError: (feedback, fallbackMessage) => {
				const errorMessage = feedback.action === 'toast-only' ? feedback.message : fallbackMessage;
				this.messagesError.set(errorMessage);
				this.message.error(errorMessage);
			}
		});
	}

	private isNotFoundMessage(errorMessage: string): boolean {
		return /404|not found|không tìm thấy/i.test(errorMessage);
	}
}
