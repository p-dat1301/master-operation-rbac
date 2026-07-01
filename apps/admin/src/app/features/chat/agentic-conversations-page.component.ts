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
	templateUrl: './agentic-conversations-page.component.html',
	styleUrls: ['../../shared/admin-page-styles.css', './agentic-conversations-page.component.css']
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
