import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { AuditLogResponse } from '../../models/audit.models';
import { AuditApiService } from '../../services/audit-api.service';
import { ADMIN_DATETIME_SECONDS_FORMAT } from '../../shared/date-formats';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

@Component({
	selector: 'app-audit-logs-page',
	standalone: true,
	imports: [CommonModule, NzCardModule, NzIconModule, NzTableModule, NzTagModule, NzTooltipModule],
	template: `
		<section class="page-root" data-testid="audit-logs-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Security & Compliance</p>
					<h2>Audit Logs</h2>
					<p class="subtitle">Lịch sử toàn bộ hoạt động trong hệ thống.</p>
				</div>
				<div class="total-chip">
					<span nz-icon nzType="database"></span>
					<span>{{ logs().length }} bản ghi</span>
				</div>
			</div>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #logTable [nzData]="logs()" [nzLoading]="loading()" [nzPageSize]="20" nzSize="small" data-testid="audit-logs-table">
					<thead>
						<tr>
							<th nzWidth="50px">#</th>
							<th nzWidth="160px">Thời gian</th>
							<th>Actor</th>
							<th nzWidth="140px">Hành động</th>
							<th nzWidth="130px">Resource type</th>
							<th nzWidth="100px">Resource ID</th>
							<th>IP</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let log of logTable.data; let i = index">
							<td class="idx-col">{{ i + 1 }}</td>
							<td class="time-col">{{ log.created_at | date:ADMIN_DATETIME_SECONDS_FORMAT }}</td>
							<td>
								<span class="actor-name">{{ log.actor_name || '—' }}</span>
								<span *ngIf="log.actor_id" class="actor-id">(ID:{{ log.actor_id }})</span>
							</td>
							<td>
								<nz-tag [nzColor]="actionColor(log.action)">{{ log.action }}</nz-tag>
							</td>
							<td class="muted">{{ log.resource_type }}</td>
							<td class="muted">{{ log.resource_id || '—' }}</td>
							<td class="muted">{{ log.ip_address || '—' }}</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.total-chip { display:flex; align-items:center; gap:.5rem; padding:.6rem 1rem; border-radius:1rem; background:var(--admin-surface-field); border:1px solid var(--admin-border-subtle); color:var(--admin-text-secondary); font-size:.9rem }
		.time-col { font-family:monospace; font-size:.82rem; color:var(--admin-text-muted) }
		.actor-name { color:var(--admin-text-primary); font-weight:600 }
		.actor-id { font-size:.78rem; color:var(--admin-text-muted); margin-left:.3rem }
	`]
})
export class AuditLogsPageComponent implements OnInit {
	protected readonly ADMIN_DATETIME_SECONDS_FORMAT = ADMIN_DATETIME_SECONDS_FORMAT;
	private readonly auditApi = inject(AuditApiService);
	private readonly message = inject(NzMessageService);

	readonly logs = signal<AuditLogResponse[]>([]);
	readonly loading = signal(false);

	ngOnInit(): void { this.load(); }

	async load(): Promise<void> {
		this.loading.set(true);
		try {
			const data = await firstValueFrom(this.auditApi.listAuditLogs());
			this.logs.set(data);
		} catch { this.message.error('Không thể tải audit logs.'); }
		finally { this.loading.set(false); }
	}

	actionColor(action: string): string {
		if (action.includes('create') || action.includes('add')) return 'green';
		if (action.includes('delete') || action.includes('remove')) return 'red';
		if (action.includes('update') || action.includes('edit')) return 'blue';
		if (action.includes('login') || action.includes('logout')) return 'purple';
		return 'default';
	}
}
