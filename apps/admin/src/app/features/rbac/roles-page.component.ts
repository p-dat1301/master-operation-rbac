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

import { PermissionResponse, RoleCreateRequest, RoleResponse } from '../../models/rbac.models';
import { RbacApiService } from '../../services/rbac-api.service';

@Component({
	selector: 'app-roles-page',
	standalone: true,
	imports: [
		CommonModule, FormsModule,
		NzButtonModule, NzCardModule, NzCheckboxModule, NzDividerModule,
		NzIconModule, NzInputModule, NzModalModule, NzSpinModule,
		NzTableModule, NzTagModule, NzTooltipModule
	],
	template: `
		<section class="page-root" data-testid="roles-page">
			<!-- Header -->
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

			<!-- Roles table -->
			<nz-card class="table-card" [nzBordered]="false">
				<nz-table
					#roleTable
					[nzData]="roles()"
					[nzLoading]="loading()"
					[nzPageSize]="15"
					nzSize="middle"
					data-testid="roles-table"
				>
					<thead>
						<tr>
							<th nzWidth="60px">#</th>
							<th>Tên role</th>
							<th>Display name</th>
							<th nzWidth="180px">Permissions</th>
							<th nzWidth="140px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let role of roleTable.data; let i = index">
							<td><span class="idx-col">{{ i + 1 }}</span></td>
							<td><code class="role-code">{{ role.name }}</code></td>
							<td><span class="display-name">{{ role.display_name }}</span></td>
							<td>
								<button
									nz-button nzType="dashed" nzSize="small"
									(click)="openPermModal(role)"
									nz-tooltip="Xem & quản lý permissions"
									[attr.data-testid]="'perms-btn-'+role.id"
								>
									<span nz-icon nzType="key"></span> Permissions
								</button>
							</td>
							<td nzAlign="right">
								<button
									nz-button nzDanger nzType="text" nzSize="small"
									(click)="deleteRole(role)"
									nz-tooltip="Xóa role"
									[attr.data-testid]="'delete-role-'+role.id"
								>
									<span nz-icon nzType="delete"></span>
								</button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>

			<!-- ── Create Role Modal ─────────────────────────────────── -->
			<nz-modal
				[(nzVisible)]="showCreateModal"
				nzTitle="Tạo role mới"
				(nzOnOk)="submitCreate()"
				(nzOnCancel)="showCreateModal = false"
				[nzOkLoading]="saving()"
				nzOkText="Tạo"
				id="create-role-modal"
			>
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

			<!-- ── Permissions Modal ─────────────────────────────────── -->
			<nz-modal
				[(nzVisible)]="showPermModal"
				[nzTitle]="'Permissions — ' + (selectedRole()?.display_name ?? '')"
				(nzOnCancel)="showPermModal = false"
				nzOkText="Lưu thay đổi"
				(nzOnOk)="savePermissions()"
				[nzOkLoading]="permSaving()"
				nzWidth="600px"
				id="role-permissions-modal"
			>
				<ng-container *nzModalContent>
					<nz-spin [nzSpinning]="permLoading()">
						<p class="perm-modal-hint">Chọn các quyền cho role <strong>{{ selectedRole()?.display_name }}</strong>:</p>
						<div class="perm-grid">
							<label
								*ngFor="let p of allPermissions()"
								class="perm-item"
								[class.perm-item--checked]="hasPermission(p.id)"
							>
								<input
									type="checkbox"
									[checked]="hasPermission(p.id)"
									(change)="togglePerm(p.id)"
									class="perm-checkbox"
								/>
								<div class="perm-info">
									<code class="perm-code">{{ p.code }}</code>
									<span class="perm-desc">{{ p.description }}</span>
								</div>
							</label>
						</div>
						<p *ngIf="allPermissions().length === 0 && !permLoading()" class="empty-hint">
							Không có permissions nào trong hệ thống.
						</p>
					</nz-spin>
				</ng-container>
			</nz-modal>
		</section>
	`,
	styles: [`
		.page-root { display:grid; gap:1.5rem }
		.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap }
		h2 { margin:.2rem 0 0; font-size:clamp(1.4rem,2.5vw,2rem); color:#f8fafc }
		.eyebrow { margin:0; font-size:.76rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#7dd3fc }
		.subtitle { margin:.4rem 0 0; color:rgba(226,232,240,.65); font-size:.9rem }
		.table-card { background:rgba(15,23,42,.72); border-radius:1.2rem }

		/* ── Force readable dark text inside NZ Zorro white table ── */
		.idx-col { color:#64748b; font-size:.82rem }

		.role-code {
			background:rgba(14,165,233,.1); color:#0369a1;
			padding:.2rem .55rem; border-radius:.4rem; font-size:.86rem; font-weight:700;
		}
		.display-name { color:#0f172a; font-weight:700; font-size:.92rem }

		:host ::ng-deep .ant-table-thead > tr > th {
			background:#f1f5f9 !important; color:#1e293b !important;
			font-weight:700; font-size:.84rem; letter-spacing:.02em;
		}
		:host ::ng-deep .ant-table,
		:host ::ng-deep .ant-table-container,
		:host ::ng-deep .ant-table-content,
		:host ::ng-deep .ant-table-tbody,
		:host ::ng-deep .ant-table-cell { color:#0f172a !important; }
		:host ::ng-deep .ant-table-tbody > tr > td { color:#0f172a !important; }
		:host ::ng-deep .ant-table-tbody > tr:hover > td { background:#f8fafc !important; }
		:host ::ng-deep .ant-empty-description { color:#334155 !important; }

		/* ── Create modal form ── */
		.modal-form { display:grid; gap:1.2rem }
		.form-field { display:grid; gap:.4rem }
		.field-label { font-size:.9rem; font-weight:600; color:#1e293b }
		.required { color:#ef4444 }

		/* ── Permission modal ── */
		.perm-modal-hint { color:#475569; margin-bottom:1rem; font-size:.9rem }
		.perm-modal-hint strong { color:#1e293b }
		.perm-grid { display:grid; gap:.5rem; max-height:420px; overflow-y:auto; padding-right:.25rem }
		.perm-item {
			display:flex; align-items:flex-start; gap:.75rem; padding:.65rem .85rem;
			border:1.5px solid #e2e8f0; border-radius:.6rem; cursor:pointer;
			transition: all .15s ease; background:#fff;
		}
		.perm-item:hover { border-color:#93c5fd; background:#eff6ff }
		.perm-item--checked { border-color:#3b82f6; background:#eff6ff }
		.perm-checkbox { margin-top:.15rem; accent-color:#3b82f6; width:16px; height:16px; flex-shrink:0 }
		.perm-info { display:grid; gap:.15rem }
		.perm-code { font-size:.83rem; font-weight:700; color:#1d4ed8; font-family:monospace }
		.perm-desc { font-size:.8rem; color:#64748b }
		.empty-hint { color:#94a3b8; text-align:center; padding:1rem 0; margin:0 }
	`]
})
export class RolesPageComponent implements OnInit {
	private readonly rbacApi = inject(RbacApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly roles = signal<RoleResponse[]>([]);
	readonly loading = signal(false);
	readonly saving = signal(false);
	readonly selectedRole = signal<RoleResponse | null>(null);
	readonly rolePermissions = signal<PermissionResponse[]>([]);
	readonly allPermissions = signal<PermissionResponse[]>([]);
	readonly permLoading = signal(false);
	readonly permSaving = signal(false);

	// Track checkbox state as Set of permission IDs
	selectedPermIds = new Set<number>();

	showCreateModal = false;
	showPermModal = false;
	createForm: RoleCreateRequest = { name: '', display_name: '' };

	ngOnInit(): void {
		this.loadRoles();
		this.loadAllPermissions();
	}

	private async loadRoles(): Promise<void> {
		this.loading.set(true);
		try {
			const result = await firstValueFrom(this.rbacApi.listRoles());
			this.roles.set(result);
		} catch { this.message.error('Không thể tải danh sách roles.'); }
		finally { this.loading.set(false); }
	}

	private async loadAllPermissions(): Promise<void> {
		try {
			const perms = await firstValueFrom(this.rbacApi.listPermissions());
			this.allPermissions.set(perms);
		} catch { /* ignore */ }
	}

	openCreateModal(): void {
		this.createForm = { name: '', display_name: '' };
		this.showCreateModal = true;
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
		} catch { this.message.error('Tạo role thất bại.'); }
		finally { this.saving.set(false); }
	}

	async openPermModal(role: RoleResponse): Promise<void> {
		this.selectedRole.set(role);
		this.showPermModal = true;
		this.permLoading.set(true);
		try {
			const perms = await firstValueFrom(this.rbacApi.listRolePermissions(role.id));
			this.rolePermissions.set(perms);
			this.selectedPermIds = new Set(perms.map(p => p.id));
		} catch { this.message.error('Không thể tải permissions của role.'); }
		finally { this.permLoading.set(false); }
	}

	hasPermission(permId: number): boolean {
		return this.selectedPermIds.has(permId);
	}

	togglePerm(permId: number): void {
		if (this.selectedPermIds.has(permId)) {
			this.selectedPermIds.delete(permId);
		} else {
			this.selectedPermIds.add(permId);
		}
	}

	async savePermissions(): Promise<void> {
		const role = this.selectedRole();
		if (!role) return;
		this.permSaving.set(true);
		try {
			const current = new Set(this.rolePermissions().map(p => p.id));
			const desired = this.selectedPermIds;

			// Add new permissions
			const toAdd = [...desired].filter(id => !current.has(id));
			for (const id of toAdd) {
				await firstValueFrom(this.rbacApi.addPermissionToRole(role.id, id));
			}

			// Remove deselected permissions
			const toRemove = [...current].filter(id => !desired.has(id));
			for (const id of toRemove) {
				await firstValueFrom(this.rbacApi.removePermissionFromRole(role.id, id));
			}

			this.message.success(`Đã cập nhật permissions cho role "${role.display_name}".`);
			this.showPermModal = false;
		} catch { this.message.error('Cập nhật permissions thất bại.'); }
		finally { this.permSaving.set(false); }
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
					this.roles.update((list) => list.filter((r) => r.id !== role.id));
					this.message.success('Đã xóa role.');
				} catch { this.message.error('Xóa role thất bại.'); }
			}
		});
	}
}
