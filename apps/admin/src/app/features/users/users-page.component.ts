import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzBadgeModule } from 'ng-zorro-antd/badge';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalService } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { DepartmentResponse, RoleResponse } from '../../models/rbac.models';
import { UserCreateRequest, UserFilters, UserListItem, UserUpdateRequest } from '../../models/user.models';
import { RbacApiService } from '../../services/rbac-api.service';
import { UserApiService } from '../../services/user-api.service';
import { runAdminAsync } from '../../shared/async-state';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';
import { UserPageModalsComponent } from './user-page-modals.component';

export type UserFormMode = 'create' | 'edit';

export type UserFormState = {
	employee_code: string;
	email: string;
	full_name: string;
	password: string;
	role_name: string;
	phone: string;
	job_title: string;
	department_id: number | null;
	manager_id: number | null;
};

export const EMPTY_USER_FORM: UserFormState = {
	employee_code: '',
	email: '',
	full_name: '',
	password: '',
	role_name: '',
	phone: '',
	job_title: '',
	department_id: null,
	manager_id: null
};

@Component({
	selector: 'app-users-page',
	standalone: true,
	imports: [
		CommonModule,
		FormsModule,
		NzBadgeModule,
		NzButtonModule,
		NzCardModule,
		NzIconModule,
		NzSelectModule,
		NzTableModule,
		NzTagModule,
		NzTooltipModule,
		UserPageModalsComponent
	],
	template: `
		<section class="page-root" data-testid="users-page">
			<div class="page-header surface-card">
				<div class="page-header-copy">
					<p class="eyebrow">HR Management</p>
					<h2>Quản lý người dùng</h2>
					<p class="subtitle">Danh sách tài khoản nhân viên trong hệ thống.</p>
				</div>
				<div class="header-actions">
					<div class="header-stats">
						<div class="stat-chip active"><span class="stat-value">{{ activeCount() }}</span><span class="stat-label">Active</span></div>
						<div class="stat-chip inactive"><span class="stat-value">{{ inactiveCount() }}</span><span class="stat-label">Inactive</span></div>
					</div>
					<button nz-button nzType="primary" (click)="openCreateUser()" data-testid="create-user-btn"><span nz-icon nzType="plus"></span> Tạo người dùng</button>
				</div>
			</div>

			<nz-card class="filter-card surface-card content-panel" [nzBordered]="false">
				<div class="filter-row">
					<div class="filter-copy">
						<p class="filter-kicker">Validation view</p>
						<div>
							<h3>Bộ lọc trạng thái</h3>
							<p>Tập trung rà soát nhanh trạng thái kích hoạt trước khi chỉnh sửa hoặc thu hồi quyền.</p>
						</div>
					</div>
					<div class="filter-controls">
						<label class="filter-item"><span>Trạng thái</span>
							<nz-select [(ngModel)]="filters.is_active" (ngModelChange)="applyFilters()" nzPlaceHolder="Tất cả" nzAllowClear style="width:160px">
								<nz-option [nzValue]="true" nzLabel="Đang hoạt động"></nz-option>
								<nz-option [nzValue]="false" nzLabel="Vô hiệu hóa"></nz-option>
							</nz-select>
						</label>
						<button nz-button nzType="dashed" (click)="resetFilters()" id="reset-filters-btn">
							<span nz-icon nzType="reload"></span> Đặt lại
						</button>
					</div>
				</div>
			</nz-card>

			<nz-card class="table-card surface-card content-panel" [nzBordered]="false">
				<div class="table-shell">
					<div class="table-toolbar">
						<div>
							<p class="table-kicker">Directory ledger</p>
							<h3>Danh sách người dùng</h3>
						</div>
						<div class="table-meta">
							<span class="meta-pill">{{ filteredUsers().length }} hồ sơ</span>
							<span class="meta-pill muted-pill">Phân trang 15 bản ghi</span>
						</div>
					</div>
					<nz-table #userTable [nzData]="filteredUsers()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="users-table">
					<thead>
						<tr>
							<th nzWidth="50px">#</th>
							<th>Nhân viên</th>
							<th>Email</th>
							<th>Vai trò</th>
							<th>Chức danh</th>
							<th nzWidth="120px" nzAlign="center">Trạng thái</th>
							<th nzWidth="220px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let user of userTable.data; let i = index">
							<td class="idx-col">{{ i + 1 }}</td>
							<td>
								<div class="user-cell">
									<div class="avatar">{{ getInitials(user.full_name) }}</div>
									<div><div class="user-name">{{ user.full_name }}</div><div class="user-code">{{ user.employee_code }}</div></div>
								</div>
							</td>
							<td class="muted">{{ user.email }}</td>
							<td><nz-tag nzColor="blue">{{ user.role_name }}</nz-tag></td>
							<td class="muted">{{ user.job_title || '—' }}</td>
							<td nzAlign="center"><nz-badge [nzStatus]="user.is_active ? 'success' : 'default'" [nzText]="user.is_active ? 'Active' : 'Inactive'"></nz-badge></td>
							<td nzAlign="right">
								<button nz-button nzType="text" nzSize="small" (click)="openUserDetail(user)" nz-tooltip="Chi tiết" [attr.data-testid]="'detail-user-'+user.id"><span nz-icon nzType="eye"></span></button>
								<button nz-button nzType="text" nzSize="small" class="action-primary" (click)="openEditUser(user)" nz-tooltip="Chỉnh sửa" [attr.data-testid]="'edit-user-'+user.id"><span nz-icon nzType="edit"></span></button>
								<button *ngIf="user.is_active" nz-button nzDanger nzType="text" nzSize="small" class="action-danger" (click)="toggleUser(user)" nz-tooltip="Vô hiệu hóa" [attr.data-testid]="'deactivate-'+user.id"><span nz-icon nzType="stop"></span></button>
								<button *ngIf="!user.is_active" nz-button nzType="text" nzSize="small" class="action-success" (click)="toggleUser(user)" nz-tooltip="Kích hoạt" [attr.data-testid]="'activate-'+user.id"><span nz-icon nzType="check-circle"></span></button>
								<button nz-button nzType="text" nzSize="small" class="action-warning" (click)="openResetPassword(user)" nz-tooltip="Reset mật khẩu" [attr.data-testid]="'reset-pwd-'+user.id"><span nz-icon nzType="lock"></span></button>
								<button nz-button nzDanger nzType="text" nzSize="small" (click)="confirmDeleteUser(user)" nz-tooltip="Xóa" [attr.data-testid]="'delete-user-'+user.id"><span nz-icon nzType="delete"></span></button>
							</td>
						</tr>
					</tbody>
					</nz-table>
				</div>
			</nz-card>

			<app-user-page-modals
				[formMode]="formMode"
				[userForm]="userForm"
				[saving]="saving()"
				[selectedUser]="selectedUser()"
				[newPassword]="newPassword"
				[roles]="roles()"
				[departments]="departments()"
				[allUsers]="allUsers()"
				[formVisible]="showFormModal"
				[detailVisible]="showDetailModal"
				[resetVisible]="showResetModal"
				(submitForm)="submitUserForm()"
				(cancelForm)="closeFormModal()"
				(detailVisibleChange)="showDetailModal = $event"
				(resetVisibleChange)="showResetModal = $event"
				(newPasswordChange)="newPassword = $event"
				(submitReset)="submitResetPassword()"
			></app-user-page-modals>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.page-header { padding: 1.2rem 1.25rem; align-items:flex-start; }
		.page-header-copy { display:grid; gap:.2rem }
		.header-actions { display:flex; align-items:center; gap:1rem; flex-wrap:wrap; justify-content:flex-end }
		.header-stats { display:flex; gap:.75rem; flex-wrap:wrap }
		.stat-chip { display:grid; gap:.12rem; align-content:start; min-width:108px; padding:.75rem .95rem; border-radius:1rem; background:linear-gradient(180deg, rgba(16, 24, 38, .82), rgba(10, 15, 25, .7)); border:1px solid var(--admin-border-subtle); box-shadow: inset 0 1px 0 rgba(255,255,255,.03) }
		.stat-chip.active { border-color: rgba(129, 140, 248, .22); box-shadow: inset 0 1px 0 rgba(255,255,255,.03), 0 0 0 1px rgba(129, 140, 248, .05) }
		.stat-chip.inactive { border-color: rgba(148, 163, 184, .16) }
		.stat-value { font-size:1.35rem; line-height:1; font-weight:750; letter-spacing:-.03em; color:var(--admin-text-primary) }
		.stat-label { font-size:.74rem; color:var(--admin-text-muted); text-transform:uppercase; letter-spacing:.12em }
		.filter-card { padding:1rem 1.1rem; }
		.filter-row { align-items:stretch; justify-content:space-between }
		.filter-copy { display:grid; gap:.45rem; min-width:min(420px, 100%) }
		.filter-kicker, .table-kicker { margin:0; font-size:.72rem; letter-spacing:.18em; text-transform:uppercase; color:var(--admin-action-primary) }
		.filter-copy h3, .table-toolbar h3 { margin:0; font-size:1.03rem; font-weight:700; color:var(--admin-text-primary) }
		.filter-copy p { margin:0; color:var(--admin-text-secondary); font-size:.88rem; max-width:54ch }
		.filter-controls { display:flex; align-items:flex-end; gap:.85rem; flex-wrap:wrap }
		.table-card { padding:1rem 1.1rem 1.1rem }
		.table-shell { display:grid; gap:.85rem }
		.table-toolbar { display:flex; align-items:flex-end; justify-content:space-between; gap:1rem; flex-wrap:wrap }
		.table-meta { display:flex; gap:.55rem; flex-wrap:wrap; justify-content:flex-end }
		.meta-pill { display:inline-flex; align-items:center; padding:.36rem .7rem; border-radius:999px; background:rgba(129, 140, 248, .12); border:1px solid rgba(129, 140, 248, .14); color:#c7d2fe; font-size:.74rem; font-weight:700; letter-spacing:.02em }
		.muted-pill { background:rgba(148, 163, 184, .08); border-color:rgba(148, 163, 184, .12); color:var(--admin-text-secondary) }
		.user-cell { display:flex; align-items:center; gap:.85rem; min-width:0 }
		.avatar { width:2.35rem; height:2.35rem; border-radius:50%; background:linear-gradient(135deg,var(--admin-action-primary),var(--admin-action-primary-strong)); display:grid; place-items:center; font-size:.74rem; font-weight:800; letter-spacing:.04em; color:#fff; flex-shrink:0; box-shadow:0 10px 22px rgba(129,140,248,.22) }
		.user-name { font-weight:700; color:var(--admin-text-primary); line-height:1.1 }
		.user-code { font-size:.76rem; color:var(--admin-text-muted); margin-top:.12rem }
		:host ::ng-deep .ant-table-thead > tr > th { background:rgba(9, 15, 27, .7); color:var(--admin-text-strong); letter-spacing:.03em }
		:host ::ng-deep .ant-badge-status-text { color:var(--admin-text-secondary) }
		:host ::ng-deep .ant-tag { margin-inline-end:0; border-radius:.7rem; border-color:rgba(129,140,248,.18); background:rgba(129,140,248,.12); color:#c7d2fe; font-weight:600 }
		:host ::ng-deep .ant-table-tbody > tr > td { vertical-align:middle }
	`]

})
export class UsersPageComponent implements OnInit {
	private readonly userApi = inject(UserApiService);
	private readonly rbacApi = inject(RbacApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly allUsers = signal<UserListItem[]>([]);
	readonly roles = signal<RoleResponse[]>([]);
	readonly departments = signal<DepartmentResponse[]>([]);
	readonly filteredUsers = signal<UserListItem[]>([]);
	readonly loading = signal(false);
	readonly saving = signal(false);
	readonly selectedUser = signal<UserListItem | null>(null);

	showResetModal = false;
	showFormModal = false;
	showDetailModal = false;
	formMode: UserFormMode = 'create';
	userForm: UserFormState = { ...EMPTY_USER_FORM };
	newPassword = '';
	filters: UserFilters = {};

	activeCount = () => this.allUsers().filter((u) => u.is_active).length;
	inactiveCount = () => this.allUsers().filter((u) => !u.is_active).length;

	ngOnInit(): void {
		this.loadUsers();
		this.loadFormOptions();
	}

	private async loadUsers(): Promise<void> {
		await runAdminAsync(this.userApi.listUsers(), {
			pending: this.loading,
			fallbackMessage: 'Không thể tải danh sách người dùng.',
			onSuccess: (result) => {
				this.allUsers.set(result);
				this.applyFilters();
			},
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	private async loadFormOptions(): Promise<void> {
		await Promise.all([
			runAdminAsync(this.rbacApi.listRoles(), {
				fallbackMessage: 'Không thể tải danh sách vai trò.',
				onSuccess: (roles) => this.roles.set(roles),
				onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
			}),
			runAdminAsync(this.rbacApi.listDepartments(), {
				fallbackMessage: 'Không thể tải danh sách phòng ban.',
				onSuccess: (departments) => this.departments.set(departments),
				onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
			})
		]);
	}

	applyFilters(): void {
		let list = this.allUsers();
		if (this.filters.is_active != null) {
			list = list.filter((u) => u.is_active === this.filters.is_active);
		}
		this.filteredUsers.set(list);
	}

	resetFilters(): void {
		this.filters = {};
		this.applyFilters();
	}

	openCreateUser(): void {
		this.formMode = 'create';
		this.selectedUser.set(null);
		this.userForm = { ...EMPTY_USER_FORM };
		this.showFormModal = true;
	}

	openEditUser(user: UserListItem): void {
		this.formMode = 'edit';
		this.selectedUser.set(user);
		this.userForm = {
			employee_code: user.employee_code,
			email: user.email,
			full_name: user.full_name,
			password: '',
			role_name: user.role_name,
			phone: user.phone ?? '',
			job_title: user.job_title ?? '',
			department_id: user.department_id,
			manager_id: user.manager_id
		};
		this.showFormModal = true;
	}

	closeFormModal(): void {
		this.showFormModal = false;
		this.saving.set(false);
	}

	async submitUserForm(): Promise<void> {
		if (this.formMode === 'create' && (!this.userForm.email.trim() || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.userForm.email.trim()))) {
			this.message.warning('Vui lòng nhập email hợp lệ.');
			return;
		}
		if (!this.isUserFormValid()) {
			this.message.warning('Vui lòng nhập đủ thông tin bắt buộc.');
			return;
		}
		const fallbackMessage = this.formMode === 'create' ? 'Tạo người dùng thất bại.' : 'Cập nhật người dùng thất bại.';
		const successMessage = this.formMode === 'create' ? 'Đã tạo người dùng.' : 'Đã cập nhật người dùng.';
		const request = this.formMode === 'create'
			? this.userApi.createUser(this.toCreatePayload())
			: this.userApi.updateUser(this.selectedUser()!.id, this.toUpdatePayload());

		await runAdminAsync(request, {
			pending: this.saving,
			fallbackMessage,
			onSuccess: (saved) => {
				this.allUsers.update((list) => this.formMode === 'create' ? [saved, ...list] : list.map((u) => u.id === saved.id ? saved : u));
				this.applyFilters();
				this.showFormModal = false;
				this.message.success(successMessage);
			},
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	openUserDetail(user: UserListItem): void {
		this.selectedUser.set(user);
		this.showDetailModal = true;
	}

	confirmDeleteUser(user: UserListItem): void {
		this.modal.confirm({
			nzTitle: `Xóa "${user.full_name}"?`,
			nzContent: 'Thao tác này sẽ xóa tài khoản người dùng. Hãy chắc chắn backend cho phép xóa bản ghi này.',
			nzOkDanger: true,
			nzOkText: 'Xóa',
			nzOnOk: async () => {
				await runAdminAsync(this.userApi.deleteUser(user.id), {
					fallbackMessage: 'Xóa người dùng thất bại.',
					onSuccess: () => {
						this.allUsers.update((list) => list.filter((u) => u.id !== user.id));
						this.applyFilters();
						this.message.success('Đã xóa người dùng.');
					},
					onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
				});
			}
		});
	}

	toggleUser(user: UserListItem): void {
		const action = user.is_active ? 'vô hiệu hóa' : 'kích hoạt';
		this.modal.confirm({
			nzTitle: `${action.charAt(0).toUpperCase() + action.slice(1)} "${user.full_name}"?`,
			nzOkDanger: user.is_active,
			nzOkText: action.charAt(0).toUpperCase() + action.slice(1),
			nzOnOk: async () => {
				const request = user.is_active
					? this.userApi.deactivateUser(user.id)
					: this.userApi.activateUser(user.id);
				await runAdminAsync(request, {
					fallbackMessage: 'Thao tác thất bại.',
					onSuccess: (updated) => {
						this.allUsers.update((list) => list.map((u) => u.id === updated.id ? updated : u));
						this.applyFilters();
						this.message.success(`Đã ${action} tài khoản.`);
					},
					onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
				});
			}
		});
	}

	openResetPassword(user: UserListItem): void {
		this.selectedUser.set(user);
		this.newPassword = '';
		this.showResetModal = true;
	}

	async submitResetPassword(): Promise<void> {
		const user = this.selectedUser();
		if (!user || !this.newPassword) {
			return;
		}
		await runAdminAsync(this.userApi.resetPassword(user.id, this.newPassword), {
			pending: this.saving,
			fallbackMessage: 'Đặt lại mật khẩu thất bại.',
			onSuccess: () => {
				this.showResetModal = false;
				this.message.success('Đã đặt lại mật khẩu.');
			},
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	getInitials(name: string): string {
		return name.split(' ').slice(-2).map((n) => n[0]).join('').toUpperCase();
	}

	private isUserFormValid(): boolean {
		if (this.formMode === 'edit') {
			return Boolean(this.userForm.full_name.trim() && this.userForm.role_name.trim() && this.selectedUser());
		}
		return Boolean(
			this.userForm.employee_code.trim() &&
			this.userForm.email.trim() &&
			this.userForm.full_name.trim() &&
			this.userForm.password &&
			this.userForm.role_name.trim()
		);
	}

	private toCreatePayload(): UserCreateRequest {
		return {
			employee_code: this.userForm.employee_code.trim(),
			email: this.userForm.email.trim(),
			full_name: this.userForm.full_name.trim(),
			password: this.userForm.password,
			role_name: this.userForm.role_name.trim(),
			phone: this.optionalText(this.userForm.phone),
			job_title: this.optionalText(this.userForm.job_title),
			department_id: this.optionalNumber(this.userForm.department_id),
			manager_id: this.optionalNumber(this.userForm.manager_id)
		};
	}

	private toUpdatePayload(): UserUpdateRequest {
		return {
			full_name: this.userForm.full_name.trim(),
			role_name: this.userForm.role_name.trim(),
			phone: this.optionalText(this.userForm.phone),
			job_title: this.optionalText(this.userForm.job_title),
			department_id: this.optionalNumber(this.userForm.department_id),
			manager_id: this.optionalNumber(this.userForm.manager_id)
		};
	}

	private optionalText(value: string): string | undefined {
		const trimmed = value.trim();
		return trimmed ? trimmed : undefined;
	}

	private optionalNumber(value: number | null): number | undefined {
		return value == null ? undefined : Number(value);
	}

}
