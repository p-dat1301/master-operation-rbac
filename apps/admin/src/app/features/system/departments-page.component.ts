import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTableModule } from 'ng-zorro-antd/table';
import { firstValueFrom } from 'rxjs';

import { DepartmentResponse } from '../../models/rbac.models';
import { RbacApiService } from '../../services/rbac-api.service';
import { mapAdminHttpError } from '../../shared/http-error-mapper';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

@Component({
	selector: 'app-departments-page',
	standalone: true,
	imports: [CommonModule, NzCardModule, NzTableModule, NzTagModule],
	template: `
		<section class="page-root" data-testid="departments-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Organization Reference</p>
					<h2>Phòng ban</h2>
					<p class="subtitle">Danh sách phòng ban trong tổ chức (chỉ đọc).</p>
				</div>
			</div>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #deptTable [nzData]="departments()" [nzLoading]="loading()" [nzPageSize]="20" nzSize="middle" data-testid="departments-table">
					<thead>
						<tr>
							<th nzWidth="70px">#</th>
							<th>Tên phòng ban</th>
							<th nzWidth="120px">Cấp</th>
							<th nzWidth="140px">Phòng ban cha</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let department of deptTable.data; let i = index">
							<td><span class="idx">{{ i + 1 }}</span></td>
							<td><strong class="dept-name">{{ department.name }}</strong></td>
							<td><nz-tag [nzColor]="levelColor(department.level)">Cấp {{ department.level }}</nz-tag></td>
							<td><span class="parent">{{ department.parent_id ?? '—' }}</span></td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.dept-name { color:var(--admin-text-primary); font-size:.92rem }
		.parent { color:var(--admin-text-primary) }
		:host ::ng-deep .ant-table-thead > tr > th { background:rgba(8,15,28,.78) !important; color:var(--admin-text-strong) !important; font-weight:700; font-size:.84rem; }
		:host ::ng-deep .ant-table, :host ::ng-deep .ant-table-container, :host ::ng-deep .ant-table-content, :host ::ng-deep .ant-table-tbody, :host ::ng-deep .ant-table-cell { color:var(--admin-text-primary) !important; }
		:host ::ng-deep .ant-table-tbody > tr > td { color:var(--admin-text-primary) !important; }
		:host ::ng-deep .ant-table-tbody > tr:hover > td { background:rgba(8,15,28,.68) !important; }
		:host ::ng-deep .ant-empty-description { color:var(--admin-text-muted) !important; }
	`]
})
export class DepartmentsPageComponent implements OnInit {
	private readonly rbacApi = inject(RbacApiService);
	private readonly message = inject(NzMessageService);

	readonly departments = signal<DepartmentResponse[]>([]);
	readonly loading = signal(false);

	ngOnInit(): void { this.loadDepartments(); }

	private async loadDepartments(): Promise<void> {
		this.loading.set(true);
		try {
			this.departments.set(await firstValueFrom(this.rbacApi.listDepartments()));
		} catch (error) { this.showApiError(error, 'Không thể tải danh sách departments.'); }
		finally { this.loading.set(false); }
	}

	levelColor(level: number): string {
		return level <= 1 ? 'blue' : level === 2 ? 'geekblue' : 'default';
	}

	private showApiError(error: unknown, fallback: string): void {
		const feedback = mapAdminHttpError(error);
		this.message.error(feedback.action === 'toast-only' ? feedback.message : fallback);
	}
}
