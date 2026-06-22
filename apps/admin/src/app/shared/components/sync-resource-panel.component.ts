import { CommonModule } from '@angular/common';
import { Component, Input, signal } from '@angular/core';
import { NzAlertModule } from 'ng-zorro-antd/alert';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzModalService } from 'ng-zorro-antd/modal';

import { SyncSummary } from '../../models/admin-config.models';
import { AdminConfigSyncService } from '../../services/admin-config-sync.service';
import { runAdminAsync } from '../async-state';
import { SyncConfirmDialogComponent } from './sync-confirm-dialog.component';

@Component({
	selector: 'app-sync-resource-panel',
	standalone: true,
	imports: [CommonModule, NzAlertModule, NzButtonModule, NzCardModule],
	template: `
		<section class="page-stack" [attr.data-testid]="pageTestId">
			<nz-card class="surface-card" [nzBordered]="false">
				<div class="panel-header">
					<div>
						<p class="eyebrow">Configuration</p>
						<h3>{{ title }}</h3>
						<p>{{ description }}</p>
					</div>
					<button
						nz-button
						nzType="primary"
						[nzLoading]="loading()"
						[attr.data-testid]="buttonTestId"
						(click)="openConfirm()"
					>
						Run sync
					</button>
				</div>
			</nz-card>

			<nz-card *ngIf="summary() as result" class="surface-card" [nzBordered]="false">
				<p class="eyebrow">Latest response</p>
				<div class="summary-grid">
					<div>
						<span>Created</span>
						<strong data-testid="sync-summary-created">{{ result.created }}</strong>
					</div>
					<div>
						<span>Updated</span>
						<strong data-testid="sync-summary-updated">{{ result.updated }}</strong>
					</div>
					<div>
						<span>Skipped</span>
						<strong data-testid="sync-summary-skipped">{{ result.skipped }}</strong>
					</div>
				</div>
				<nz-alert
					*ngIf="result.errors.length"
					nzType="error"
					[nzMessage]="result.errors.join(' • ')"
					class="mt-4"
				></nz-alert>
			</nz-card>

			<nz-alert
				*ngIf="feedbackMessage()"
				[nzType]="feedbackType()"
				[nzMessage]="feedbackMessage()"
			></nz-alert>

			<nz-alert *ngIf="errorMessage()" nzType="error" [nzMessage]="errorMessage()"></nz-alert>
		</section>
	`,
	styles: [
		`
			.page-stack {
				display: grid;
				gap: 1rem;
			}

			.panel-header {
				display: flex;
				justify-content: space-between;
				align-items: flex-start;
				gap: 1rem;
			}

			h3,
			p {
				margin: 0;
			}

			h3 {
				font-size: 1.7rem;
				color: #f8fafc;
			}

			p {
				line-height: 1.7;
				color: rgba(226, 232, 240, 0.78);
			}

			.eyebrow {
				margin: 0 0 0.8rem;
				font-size: 0.78rem;
				font-weight: 700;
				letter-spacing: 0.16em;
				text-transform: uppercase;
				color: #7dd3fc;
			}

			.surface-card {
				background: rgba(15, 23, 42, 0.78);
				border-radius: 1.4rem;
			}

			.summary-grid {
				display: grid;
				grid-template-columns: repeat(3, minmax(0, 1fr));
				gap: 1rem;
				margin-top: 1rem;
			}

			.summary-grid div {
				padding: 1rem;
				border-radius: 1rem;
				background: rgba(30, 41, 59, 0.72);
			}

			.summary-grid span {
				display: block;
				font-size: 0.85rem;
				color: rgba(186, 230, 253, 0.72);
			}

			.summary-grid strong {
				display: block;
				margin-top: 0.35rem;
				font-size: clamp(1.4rem, 3vw, 2rem);
				color: #f8fafc;
			}

			@media (max-width: 767px) {
				.panel-header {
					flex-direction: column;
				}

				.summary-grid {
					grid-template-columns: 1fr;
				}
			}
		`
	]
})
export class SyncResourcePanelComponent {
	@Input({ required: true }) resource!: 'menu' | 'i18n';
	@Input({ required: true }) title = '';
	@Input({ required: true }) description = '';
	@Input({ required: true }) pageTestId = '';
	@Input({ required: true }) buttonTestId = '';

	readonly summary = signal<SyncSummary | null>(null);
	readonly errorMessage = signal<string | null>(null);
	readonly feedbackMessage = signal<string | null>(null);
	readonly feedbackType = signal<'success' | 'error'>('success');
	readonly loading = signal(false);

	constructor(
		private readonly modal: NzModalService,
		private readonly syncService: AdminConfigSyncService
	) {}

	openConfirm(): void {
		const modalRef = this.modal.create<SyncConfirmDialogComponent, { resourceLabel: string }, boolean>({
			nzContent: SyncConfirmDialogComponent,
			nzData: { resourceLabel: this.title },
			nzFooter: null,
			nzClosable: false,
			nzMaskClosable: false
		});

		modalRef.afterClose.subscribe((confirmed) => {
			if (confirmed) {
				void this.runSync();
			}
		});
	}

	private async runSync(): Promise<void> {
		this.loading.set(true);
		this.errorMessage.set(null);
		this.feedbackMessage.set(null);

		await runAdminAsync(
			this.resource === 'menu' ? this.syncService.syncMenu(false) : this.syncService.syncI18n(false),
			{
				pending: this.loading,
				fallbackMessage: `${this.title} failed.`,
				onSuccess: (summary) => {
					this.summary.set(summary);
					this.feedbackType.set('success');
					this.feedbackMessage.set(`${this.title} completed: created ${summary.created}, updated ${summary.updated}, skipped ${summary.skipped}.`);
				},
				onError: (feedback, message) => {
					const text = feedback.action === 'toast-only' ? feedback.message : message;
					this.errorMessage.set(text);
					this.feedbackType.set('error');
					this.feedbackMessage.set(`${this.title} failed: ${text}`);
				}
			}
		);
	}

}
