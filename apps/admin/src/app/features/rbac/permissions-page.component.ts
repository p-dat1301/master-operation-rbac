import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalModule, NzModalService } from 'ng-zorro-antd/modal';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { PermissionResponse, PermissionWriteRequest } from '../../models/rbac.models';
import { RbacApiService } from '../../services/rbac-api.service';
import { mapAdminHttpError } from '../../shared/http-error-mapper';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

@Component({
	selector: 'app-permissions-page',
	standalone: true,
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzIconModule, NzInputModule, NzModalModule, NzTableModule, NzTagModule, NzTooltipModule],
	template: `
		<section class="page-root" data-testid="permissions-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">RBAC Management</p>
					<h2>Permissions</h2>
					<p class="subtitle">Quản lý danh sách quyền trong hệ thống.</p>
				</div>
				<button nz-button nzType="primary" nzSize="large" (click)="openCreateModal()" data-testid="create-permission-btn">
					<span nz-icon nzType="plus"></span> Tạo permission
				</button>
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
						<th>Mã quyền</th>
						<th>Mô tả</th>
						<th nzWidth="140px">Nhóm</th>
						<th nzWidth="140px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let p of permTable.data; let i = index">
							<td><span class="idx">{{ i + 1 }}</span></td>
							<td><code class="perm-code">{{ p.code }}</code></td>
							<td><span class="desc">{{ p.description || '—' }}</span></td>
							<td><nz-tag [nzColor]="getModuleColor(p.code)">{{ getModule(p.code) }}</nz-tag></td>
							<td nzAlign="right" class="actions">
								<button nz-button nzType="text" nzSize="small" (click)="openEditModal(p)" nz-tooltip="Sửa permission" [attr.data-testid]="'edit-permission-'+p.id">
									<span nz-icon nzType="edit"></span>
								</button>
								<button nz-button nzDanger nzType="text" nzSize="small" (click)="deletePermission(p)" nz-tooltip="Xóa permission" [attr.data-testid]="'delete-permission-'+p.id">
									<span nz-icon nzType="delete"></span>
								</button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>

			<nz-modal
				[(nzVisible)]="showModal"
				[nzTitle]="editingPermission() ? 'Sửa permission' : 'Tạo permission'"
				(nzOnOk)="submitPermission()"
				(nzOnCancel)="closeModal()"
				[nzOkLoading]="saving()"
				[nzOkText]="editingPermission() ? 'Lưu' : 'Tạo'"
				data-testid="permission-modal"
			>
				<ng-container *nzModalContent>
					<div class="modal-form">
						<label class="form-field">
							<span class="field-label">Permission key <span class="required">*</span></span>
							<input nz-input [(ngModel)]="form.code" placeholder="e.g. audit:view" data-testid="permission-code-input" />
						</label>
						<label class="form-field">
							<span class="field-label">Mô tả</span>
							<textarea nz-input rows="3" [(ngModel)]="form.description" placeholder="Mô tả quyền" data-testid="permission-description-input"></textarea>
						</label>
					</div>
				</ng-container>
			</nz-modal>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.actions { white-space:nowrap }
		.modal-form { display:grid; gap:1rem }
		.field-label { font-size:.9rem; font-weight:600; color:var(--admin-text-strong) }
		.required { color:var(--admin-action-danger) }
		:host ::ng-deep .ant-table-thead > tr > th { background:rgba(8,15,28,.78) !important; color:var(--admin-text-strong) !important; font-weight:700; font-size:.84rem; }
		:host ::ng-deep .ant-table, :host ::ng-deep .ant-table-container, :host ::ng-deep .ant-table-content, :host ::ng-deep .ant-table-tbody, :host ::ng-deep .ant-table-cell { color:var(--admin-text-primary) !important; }
		:host ::ng-deep .ant-table-tbody > tr > td { color:var(--admin-text-primary) !important; }
		:host ::ng-deep .ant-table-tbody > tr:hover > td { background:rgba(8,15,28,.68) !important; }
		:host ::ng-deep .ant-empty-description { color:var(--admin-text-muted) !important; }
		.perm-code { background:rgba(125,211,252,.12); color:var(--admin-action-primary-strong); padding:.2rem .55rem; border-radius:.4rem; font-size:.84rem; font-weight:600; }
	`]
})
export class PermissionsPageComponent implements OnInit {
	private readonly rbacApi = inject(RbacApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly permissions = signal<PermissionResponse[]>([]);
	readonly editingPermission = signal<PermissionResponse | null>(null);
	readonly loading = signal(false);
	readonly saving = signal(false);

	showModal = false;
	form: PermissionWriteRequest = { code: '', description: null };

	ngOnInit(): void { this.loadPermissions(); }

	private async loadPermissions(): Promise<void> {
		this.loading.set(true);
		try {
			const result = await firstValueFrom(this.rbacApi.listPermissions());
			this.permissions.set(result);
		} catch (error) { this.showApiError(error, 'Không thể tải danh sách permissions.'); }
		finally { this.loading.set(false); }
	}

	openCreateModal(): void {
		this.editingPermission.set(null);
		this.form = { code: '', description: null };
		this.showModal = true;
	}

	openEditModal(permission: PermissionResponse): void {
		this.editingPermission.set(permission);
		this.form = { code: permission.code, description: permission.description };
		this.showModal = true;
	}

	closeModal(): void {
		this.showModal = false;
	}

	async submitPermission(): Promise<void> {
		const code = this.form.code.trim();
		if (!code) {
			this.message.warning('Vui lòng nhập permission key.');
			return;
		}
		if (!/^[a-z][a-z0-9:_.-]*$/.test(code)) {
			this.message.warning('Permission key chỉ nên dùng chữ thường, số, dấu : _ -.');
			return;
		}
		const payload: PermissionWriteRequest = { code, description: this.form.description?.trim() || null };
		const editing = this.editingPermission();
		this.saving.set(true);
		try {
			if (editing) {
				const updated = await firstValueFrom(this.rbacApi.updatePermission(editing.id, payload));
				this.permissions.update((list) => list.map((item) => item.id === updated.id ? updated : item));
				this.message.success('Đã cập nhật permission.');
			} else {
				const created = await firstValueFrom(this.rbacApi.createPermission(payload));
				this.permissions.update((list) => [...list, created]);
				this.message.success('Đã tạo permission.');
			}
			this.closeModal();
		} catch (error) { this.showApiError(error, editing ? 'Cập nhật permission thất bại.' : 'Tạo permission thất bại.'); }
		finally { this.saving.set(false); }
	}

	deletePermission(permission: PermissionResponse): void {
		this.modal.confirm({
			nzTitle: `Xóa permission "${permission.code}"?`,
			nzContent: 'Chỉ xóa khi backend cho phép và permission không còn được gán cho role.',
			nzOkDanger: true,
			nzOkText: 'Xóa',
			nzOnOk: async () => {
				try {
					await firstValueFrom(this.rbacApi.deletePermission(permission.id));
					this.permissions.update((list) => list.filter((item) => item.id !== permission.id));
					this.message.success('Đã xóa permission.');
				} catch (error) { this.showApiError(error, 'Xóa permission thất bại.'); }
			}
		});
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

	private showApiError(error: unknown, fallback: string): void {
		const feedback = mapAdminHttpError(error);
		this.message.error(feedback.action === 'toast-only' ? feedback.message : fallback);
	}
}
