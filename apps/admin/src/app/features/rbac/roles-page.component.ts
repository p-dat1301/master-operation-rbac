import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzCheckboxModule } from 'ng-zorro-antd/checkbox';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalModule, NzModalService } from 'ng-zorro-antd/modal';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { PermissionResponse, RoleCreateRequest, RoleResponse, RoleUpdateRequest } from '../../models/rbac.models';
import { RbacApiService } from '../../services/rbac-api.service';
import { mapAdminHttpError } from '../../shared/http-error-mapper';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

@Component({
	selector: 'app-roles-page',
	standalone: true,
	imports: [
		CommonModule,
		FormsModule,
		NzButtonModule,
		NzCardModule,
		NzCheckboxModule,
		NzDividerModule,
		NzIconModule,
		NzInputModule,
		NzModalModule,
		NzSpinModule,
		NzTableModule,
		NzTagModule,
		NzTooltipModule
	],
	template: `
		<section class="page-root" data-testid="roles-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">RBAC Management</p>
					<h2>Roles</h2>
					<p class="subtitle">Quản lý vai trò và phân quyền trong hệ thống.</p>
				</div>
				<button nz-button nzType="primary" nzSize="large" (click)="openCreateModal()" id="create-role-btn">
					<span nz-icon nzType="plus"></span> Tạo role mới
				</button>
			</div>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #roleTable [nzData]="roles()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="roles-table">
					<thead>
						<tr>
							<th nzWidth="60px">#</th>
							<th>Tên role</th>
							<th>Display name</th>
							<th nzWidth="180px">Permissions</th>
							<th nzWidth="180px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let role of roleTable.data; let i = index">
							<td><span class="idx-col">{{ i + 1 }}</span></td>
							<td><code class="role-code">{{ role.name }}</code></td>
							<td><span class="display-name">{{ role.display_name }}</span></td>
							<td>
								<button nz-button nzType="dashed" nzSize="small" (click)="openPermModal(role)" nz-tooltip="Xem & quản lý permissions" [attr.data-testid]="'perms-btn-'+role.id">
									<span nz-icon nzType="key"></span> Permissions
								</button>
							</td>
							<td nzAlign="right" class="role-actions">
								<button nz-button nzType="text" nzSize="small" (click)="openEditModal(role)" nz-tooltip="Sửa role" [attr.data-testid]="'edit-role-'+role.id">
									<span nz-icon nzType="edit"></span>
								</button>
								<button nz-button nzDanger nzType="text" nzSize="small" (click)="deleteRole(role)" nz-tooltip="Xóa role" [attr.data-testid]="'delete-role-'+role.id">
									<span nz-icon nzType="delete"></span>
								</button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>

			<nz-modal [(nzVisible)]="showCreateModal" nzTitle="Tạo role mới" (nzOnOk)="submitCreate()" (nzOnCancel)="showCreateModal = false" [nzOkLoading]="saving()" nzOkText="Tạo" id="create-role-modal">
				<ng-container *nzModalContent>
					<div class="modal-form">
						<label class="form-field">
							<span class="field-label">Tên role <span class="required">*</span></span>
							<input nz-input [(ngModel)]="createForm.name" placeholder="e.g. hr_manager" id="role-name-input" />
						</label>
						<label class="form-field">
							<span class="field-label">Display name <span class="required">*</span></span>
							<input nz-input [(ngModel)]="createForm.display_name" placeholder="e.g. HR Manager" id="role-display-input" />
						</label>
					</div>
				</ng-container>
			</nz-modal>

			<nz-modal [(nzVisible)]="showEditModal" [nzTitle]="'Sửa role — ' + (editingRole()?.display_name ?? '')" (nzOnOk)="submitEdit()" (nzOnCancel)="closeEditModal()" [nzOkLoading]="saving()" nzOkText="Lưu" id="edit-role-modal">
				<ng-container *nzModalContent>
					<div class="modal-form">
						<label class="form-field">
							<span class="field-label">Tên role <span class="required">*</span></span>
							<input nz-input [(ngModel)]="editForm.name" placeholder="e.g. hr_manager" id="edit-role-name-input" />
						</label>
						<label class="form-field">
							<span class="field-label">Display name <span class="required">*</span></span>
							<input nz-input [(ngModel)]="editForm.display_name" placeholder="e.g. HR Manager" id="edit-role-display-input" />
						</label>
					</div>
				</ng-container>
			</nz-modal>

			<nz-modal [(nzVisible)]="showPermModal" [nzTitle]="permissionModalTitle" (nzOnCancel)="showPermModal = false" nzOkText="Lưu thay đổi" (nzOnOk)="savePermissions()" [nzOkLoading]="permSaving()" nzWidth="600px" id="role-permissions-modal">
				<ng-container *nzModalContent>
					<nz-spin [nzSpinning]="permLoading()">
						<p class="perm-modal-hint">Chọn các quyền cho role <strong>{{ selectedRole()?.display_name }}</strong>:</p>
						<div class="perm-grid">
							<label *ngFor="let permission of allPermissions()" class="perm-item" [class.perm-item--checked]="hasPermission(permission.id)">
								<input type="checkbox" [checked]="hasPermission(permission.id)" (change)="togglePerm(permission.id)" class="perm-checkbox"/>
								<div class="perm-info">
									<code class="perm-code">{{ permission.code }}</code>
									<span class="perm-desc">{{ permission.description }}</span>
								</div>
							</label>
						</div>
						<p *ngIf="showEmptyPermissions" class="empty-hint">Không có permissions nào trong hệ thống.</p>
					</nz-spin>
				</ng-container>
			</nz-modal>
		</section>
	`,
	styles: [
		ADMIN_PAGE_COMMON_STYLES,
		`
			.role-actions { white-space:nowrap }
			.role-code { background:rgba(125,211,252,.12); color:var(--admin-action-primary-strong); padding:.2rem .55rem; border-radius:.4rem; font-size:.86rem; font-weight:700 }
			.display-name { color:var(--admin-text-primary); font-weight:700; font-size:.92rem }
			:host ::ng-deep .ant-table-thead > tr > th { background:rgba(8,15,28,.78) !important; color:var(--admin-text-strong) !important; font-weight:700; font-size:.84rem; letter-spacing:.02em }
			:host ::ng-deep .ant-table, :host ::ng-deep .ant-table-container, :host ::ng-deep .ant-table-content, :host ::ng-deep .ant-table-tbody, :host ::ng-deep .ant-table-cell { color:var(--admin-text-primary) !important }
			:host ::ng-deep .ant-table-tbody > tr > td { color:var(--admin-text-primary) !important }
			:host ::ng-deep .ant-table-tbody > tr:hover > td { background:rgba(15,23,42,.82) !important }
			:host ::ng-deep .ant-empty-description { color:var(--admin-text-muted) !important }
			.modal-form { display:grid; gap:1.2rem }
			.field-label { font-size:.9rem; font-weight:600; color:var(--admin-text-strong) }
			.required { color:var(--admin-action-danger) }
			.perm-modal-hint { color:var(--admin-text-secondary); margin-bottom:1rem; font-size:.9rem }
			.perm-modal-hint strong { color:var(--admin-text-strong) }
			.perm-grid { display:grid; gap:.6rem; max-height:420px; overflow-y:auto; padding-right:.25rem; margin-top:.25rem }
			.perm-item { display:flex; align-items:flex-start; gap:.75rem; padding:.75rem .9rem; border:1.5px solid var(--admin-border-subtle); border-radius:.6rem; cursor:pointer; transition:all .15s ease; background:var(--admin-surface-field) }
			.perm-item:hover { border-color:rgba(125,211,252,.38); background:rgba(14,165,233,.12) }
			.perm-item--checked { border-color:rgba(125,211,252,.62); background:rgba(14,165,233,.14) }
			.perm-checkbox { margin-top:.15rem; accent-color:var(--admin-action-primary-strong); width:16px; height:16px; flex-shrink:0 }
			.perm-info { display:grid; gap:.15rem }
			.perm-code { font-size:.83rem; font-weight:700; color:var(--admin-action-primary-strong); font-family:monospace }
			.perm-desc { font-size:.8rem; color:var(--admin-text-muted) }
			.empty-hint { color:var(--admin-text-muted); text-align:center; padding:1rem 0; margin:0 }
		`
	]
})
export class RolesPageComponent implements OnInit {
	private readonly rbacApi = inject(RbacApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly roles = signal<RoleResponse[]>([]);
	readonly loading = signal(false);
	readonly saving = signal(false);
	readonly selectedRole = signal<RoleResponse | null>(null);
	readonly editingRole = signal<RoleResponse | null>(null);
	readonly rolePermissions = signal<PermissionResponse[]>([]);
	readonly allPermissions = signal<PermissionResponse[]>([]);
	readonly permLoading = signal(false);
	readonly permSaving = signal(false);

	selectedPermIds = new Set<number>();
	showCreateModal = false;
	showEditModal = false;
	showPermModal = false;
	createForm: RoleCreateRequest = { name: '', display_name: '' };
	editForm: RoleUpdateRequest = { name: '', display_name: '' };

	get permissionModalTitle(): string {
		return 'Permissions — ' + (this.selectedRole()?.display_name ?? '');
	}

	get showEmptyPermissions(): boolean {
		return this.allPermissions().length === 0 && !this.permLoading();
	}

	ngOnInit(): void {
		this.loadRoles();
		this.loadAllPermissions();
	}

	private async loadRoles(): Promise<void> {
		this.loading.set(true);
		try {
			const result = await firstValueFrom(this.rbacApi.listRoles());
			this.roles.set(result);
		} catch (error) {
			this.showApiError(error, 'Không thể tải danh sách roles.');
		} finally {
			this.loading.set(false);
		}
	}

	private async loadAllPermissions(): Promise<void> {
		try {
			const perms = await firstValueFrom(this.rbacApi.listPermissions());
			this.allPermissions.set(perms);
		} catch (error) {
			this.showApiError(error, 'Không thể tải permissions nền.');
		}
	}

	openCreateModal(): void {
		this.createForm = { name: '', display_name: '' };
		this.showCreateModal = true;
	}

	openEditModal(role: RoleResponse): void {
		this.editingRole.set(role);
		this.editForm = { name: role.name, display_name: role.display_name };
		this.showEditModal = true;
	}

	closeEditModal(): void {
		this.showEditModal = false;
		this.editingRole.set(null);
	}

	async submitCreate(): Promise<void> {
		if (!this.createForm.name || !this.createForm.display_name) {
			this.message.warning('Vui lòng điền đầy đủ thông tin.');
			return;
		}
		this.saving.set(true);
		try {
			const created = await firstValueFrom(this.rbacApi.createRole(this.createForm));
			this.roles.update((list) => [...list, created]);
			this.showCreateModal = false;
			this.message.success(`Role "${created.display_name}" đã được tạo.`);
		} catch (error) {
			this.showApiError(error, 'Tạo role thất bại.');
		} finally {
			this.saving.set(false);
		}
	}

	async submitEdit(): Promise<void> {
		const editing = this.editingRole();
		if (!editing) {
			return;
		}
		const payload: RoleUpdateRequest = {
			name: this.editForm.name.trim(),
			display_name: this.editForm.display_name.trim()
		};
		if (!payload.name || !payload.display_name) {
			this.message.warning('Vui lòng điền đầy đủ thông tin.');
			return;
		}
		this.saving.set(true);
		try {
			const updated = await firstValueFrom(this.rbacApi.updateRole(editing.id, payload));
			this.roles.update((list) => list.map((item) => item.id === updated.id ? updated : item));
			this.closeEditModal();
			this.message.success(`Role "${updated.display_name}" đã được cập nhật.`);
		} catch (error) {
			this.showApiError(error, 'Cập nhật role thất bại.');
		} finally {
			this.saving.set(false);
		}
	}

	async openPermModal(role: RoleResponse): Promise<void> {
		this.selectedRole.set(role);
		this.showPermModal = true;
		this.permLoading.set(true);
		try {
			const perms = await firstValueFrom(this.rbacApi.listRolePermissions(role.id));
			this.rolePermissions.set(perms);
			this.selectedPermIds = new Set(perms.map((permission) => permission.id));
		} catch (error) {
			this.showApiError(error, 'Không thể tải permissions của role.');
		} finally {
			this.permLoading.set(false);
		}
	}

	hasPermission(permId: number): boolean {
		return this.selectedPermIds.has(permId);
	}

	togglePerm(permId: number): void {
		if (this.selectedPermIds.has(permId)) {
			this.selectedPermIds.delete(permId);
			return;
		}
		this.selectedPermIds.add(permId);
	}

	async savePermissions(): Promise<void> {
		const role = this.selectedRole();
		if (!role) {
			return;
		}
		this.permSaving.set(true);
		try {
			const current = new Set(this.rolePermissions().map((permission) => permission.id));
			const toAdd = [...this.selectedPermIds].filter((id) => !current.has(id));
			const toRemove = [...current].filter((id) => !this.selectedPermIds.has(id));

			for (const id of toAdd) {
				await firstValueFrom(this.rbacApi.addPermissionToRole(role.id, id));
			}
			for (const id of toRemove) {
				await firstValueFrom(this.rbacApi.removePermissionFromRole(role.id, id));
			}

			this.message.success(`Đã cập nhật permissions cho role "${role.display_name}".`);
			this.showPermModal = false;
		} catch (error) {
			this.showApiError(error, 'Cập nhật permissions thất bại.');
		} finally {
			this.permSaving.set(false);
		}
	}

	deleteRole(role: RoleResponse): void {
		this.modal.confirm({
			nzTitle: `Xóa role "${role.display_name}"?`,
			nzContent: 'Hành động này không thể hoàn tác.',
			nzOkDanger: true,
			nzOkText: 'Xóa',
			nzOnOk: async () => {
				try {
					await firstValueFrom(this.rbacApi.deleteRole(role.id));
					this.roles.update((list) => list.filter((item) => item.id !== role.id));
					this.message.success('Đã xóa role.');
				} catch (error) {
					this.showApiError(error, 'Xóa role thất bại.');
				}
			}
		});
	}

	private showApiError(error: unknown, fallback: string): void {
		const feedback = mapAdminHttpError(error);
		this.message.error(feedback.action === 'toast-only' ? feedback.message : fallback);
	}
}
