import { Component, inject } from '@angular/core';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NZ_MODAL_DATA, NzModalRef } from 'ng-zorro-antd/modal';

@Component({
	selector: 'app-sync-confirm-dialog',
	standalone: true,
	imports: [NzButtonModule],
	template: `
		<div class="dialog-shell" data-testid="sync-confirm-modal">
			<p class="eyebrow">Confirm sync</p>
			<h3>Run {{ resourceLabel }} sync?</h3>
			<p>
				This action will call the backend seed synchronization endpoint and refresh
				its persisted records.
			</p>
			<div class="actions">
				<button nz-button nzType="default" (click)="close(false)">Cancel</button>
				<button nz-button nzType="primary" (click)="close(true)">Confirm sync</button>
			</div>
		</div>
	`,
	styles: [
		`
			.dialog-shell {
				display: grid;
				gap: 0.9rem;
			}

			h3,
			p {
				margin: 0;
			}

			.eyebrow {
				font-size: 0.78rem;
				font-weight: 700;
				letter-spacing: 0.16em;
				text-transform: uppercase;
				color: #7dd3fc;
			}

			p {
				line-height: 1.65;
				color: rgba(226, 232, 240, 0.8);
			}

			.actions {
				display: flex;
				justify-content: flex-end;
				gap: 0.75rem;
				margin-top: 0.5rem;
			}
		`
	]
})
export class SyncConfirmDialogComponent {
	private readonly modalData = inject<{ resourceLabel: string }>(NZ_MODAL_DATA, { optional: true });
	readonly resourceLabel = this.modalData?.resourceLabel ?? 'resource';

	constructor(private readonly modalRef: NzModalRef<SyncConfirmDialogComponent, boolean>) {}

	close(result: boolean): void {
		this.modalRef.close(result);
	}
}
