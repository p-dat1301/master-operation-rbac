import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { firstValueFrom } from 'rxjs';

import { PermissionResponse } from '../../models/rbac.models';
import { RbacApiService } from '../../services/rbac-api.service';

@Component({
	selector: 'app-permissions-page',
	standalone: true,
	imports: [CommonModule, NzCardModule, NzTableModule, NzTagModule],
	template: `
		<section class="page-root" data-testid="permissions-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">RBAC Management</p>
					<h2>Permissions</h2>
					<p class="subtitle">Danh sách tất cả permission trong hệ thống (read-only).</p>
				</div>
			</div>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table
					#permTable
					[nzData]="permissions()"
					[nzLoading]="loading()"
					[nzPageSize]="20"
					nzSize="middle"
					data-testid="permissions-table"
				>
					<thead>
						<tr>
							<th nzWidth="60px">#</th>
							<th>Permission key</th>
							<th>Mô tả</th>
							<th nzWidth="140px">Module</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let p of permTable.data; let i = index">
							<td><span class="idx">{{ i + 1 }}</span></td>
							<td><code class="perm-code">{{ p.code }}</code></td>
							<td><span class="desc">{{ p.description || '—' }}</span></td>
							<td><nz-tag [nzColor]="getModuleColor(p.code)">{{ getModule(p.code) }}</nz-tag></td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [`
		.page-root { display:grid; gap:1.5rem }
		.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem }
		h2 { margin:.2rem 0 0; font-size:clamp(1.4rem,2.5vw,2rem); color:#f8fafc }
		.eyebrow { margin:0; font-size:.76rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#7dd3fc }
		.subtitle { margin:.4rem 0 0; color:rgba(226,232,240,.65); font-size:.9rem }
		.table-card { background:rgba(15,23,42,.72); border-radius:1.2rem }

		.idx { color:#334155; font-size:.82rem; font-weight:600 }
		.perm-code {
			background:rgba(139,92,246,.12); color:#581c87;
			padding:.2rem .55rem; border-radius:.4rem; font-size:.84rem; font-weight:600;
		}
		.desc { color:#111827; font-size:.9rem; font-weight:500 }

		:host ::ng-deep .ant-table-thead > tr > th {
			background:#f1f5f9 !important; color:#1e293b !important;
			font-weight:700; font-size:.84rem;
		}
		:host ::ng-deep .ant-table,
		:host ::ng-deep .ant-table-container,
		:host ::ng-deep .ant-table-content,
		:host ::ng-deep .ant-table-tbody,
		:host ::ng-deep .ant-table-cell { color:#111827 !important; }
		:host ::ng-deep .ant-table-tbody > tr > td { color:#111827 !important; }
		:host ::ng-deep .ant-table-tbody > tr:hover > td { background:#f1f5f9 !important; }
		:host ::ng-deep .ant-empty-description { color:#334155 !important; }
	`]
})
export class PermissionsPageComponent implements OnInit {
	private readonly rbacApi = inject(RbacApiService);
	private readonly message = inject(NzMessageService);

	readonly permissions = signal<PermissionResponse[]>([]);
	readonly loading = signal(false);

	ngOnInit(): void { this.loadPermissions(); }

	private async loadPermissions(): Promise<void> {
		this.loading.set(true);
		try {
			const result = await firstValueFrom(this.rbacApi.listPermissions());
			this.permissions.set(result);
		} catch { this.message.error('Không thể tải danh sách permissions.'); }
		finally { this.loading.set(false); }
	}

	getModule(code: string | undefined | null): string {
		if (!code || typeof code !== 'string') return 'system';
		const parts = code.replace(':', '.').split('.');
		return parts[0] ?? 'system';
	}

	getModuleColor(code: string | undefined | null): string {
		const mod = this.getModule(code);
		const palette: Record<string, string> = {
			manage_org: 'blue', create_task: 'green', assign_task: 'cyan',
			approve_leave: 'orange', view_attendance: 'geekblue',
			audit: 'red', system: 'purple', postman: 'default'
		};
		return palette[mod] ?? 'default';
	}
}
