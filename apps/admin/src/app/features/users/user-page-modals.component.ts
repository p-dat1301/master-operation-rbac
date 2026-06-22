import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzDescriptionsModule } from 'ng-zorro-antd/descriptions';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzModalModule } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTagModule } from 'ng-zorro-antd/tag';

import { RoleResponse, DepartmentResponse } from '../../models/rbac.models';
import { UserListItem } from '../../models/user.models';
import { UserFormMode, UserFormState } from './users-page.component';

@Component({
	selector: 'app-user-page-modals',
	standalone: true,
	imports: [CommonModule, FormsModule, NzDescriptionsModule, NzInputModule, NzModalModule, NzSelectModule, NzTagModule],
	template: `
		<!-- Create / Edit modal -->
		<nz-modal
			[(nzVisible)]="formVisible"
			[nzTitle]="formMode === 'create' ? 'Tạo người dùng' : 'Chỉnh sửa người dùng'"
			(nzOnOk)="submitForm.emit()"
			(nzOnCancel)="cancelForm.emit()"
			[nzOkLoading]="saving"
			[nzOkText]="formMode === 'create' ? 'Tạo' : 'Lưu'"
			data-testid="user-form-modal"
		>
			<ng-container *nzModalContent>
				<div class="form-grid">
					<label *ngIf="formMode === 'create'" class="form-field">
						<span>Mã nhân viên *</span>
						<input nz-input [(ngModel)]="userForm.employee_code" data-testid="user-form-employee-code" />
					</label>
					<label *ngIf="formMode === 'create'" class="form-field">
						<span>Email *</span>
						<input nz-input type="email" [(ngModel)]="userForm.email" data-testid="user-form-email" />
					</label>
					<label class="form-field">
						<span>Họ tên *</span>
						<input nz-input [(ngModel)]="userForm.full_name" data-testid="user-form-full-name" />
					</label>
					<label *ngIf="formMode === 'create'" class="form-field">
						<span>Mật khẩu *</span>
						<input nz-input type="password" [(ngModel)]="userForm.password" data-testid="user-form-password" />
					</label>
					<label class="form-field">
						<span>Vai trò *</span>
				<nz-select
					[(ngModel)]="userForm.role_name"
					nzPlaceHolder="Chọn vai trò"
					nzShowSearch
					nzAllowClear
					data-testid="user-form-role"
				>
					<nz-option
						*ngFor="let r of roles"
						[nzValue]="r.name"
						[nzLabel]="r.display_name + ' (' + r.name + ')'"
					></nz-option>
				</nz-select>
					</label>
					<label class="form-field">
						<span>Điện thoại</span>
						<input nz-input [(ngModel)]="userForm.phone" data-testid="user-form-phone" />
					</label>
					<label class="form-field">
						<span>Chức danh</span>
						<input nz-input [(ngModel)]="userForm.job_title" data-testid="user-form-job-title" />
					</label>
					<label class="form-field">
						<span>Phòng ban</span>
				<nz-select
					[(ngModel)]="userForm.department_id"
					nzPlaceHolder="Chọn phòng ban"
					nzAllowClear
					nzShowSearch
					data-testid="user-form-department"
				>
					<nz-option
						*ngFor="let d of departments"
						[nzValue]="d.id"
						[nzLabel]="d.name"
					></nz-option>
				</nz-select>
					</label>
					<label class="form-field">
						<span>Quản lý trực tiếp</span>
						<nz-select
							[(ngModel)]="userForm.manager_id"
							nzPlaceHolder="Chọn quản lý"
							nzAllowClear
							nzShowSearch
							data-testid="user-form-manager"
						>
							<nz-option
								*ngFor="let u of allUsers"
								[nzValue]="u.id"
								[nzLabel]="u.full_name + ' (' + u.employee_code + ')'"
							></nz-option>
						</nz-select>
					</label>
				</div>
			</ng-container>
		</nz-modal>

		<!-- Detail modal -->
		<nz-modal
			[(nzVisible)]="detailVisible"
			nzTitle="Chi tiết người dùng"
			(nzOnCancel)="detailVisibleChange.emit(false)"
			[nzFooter]="null"
			data-testid="user-detail-modal"
		>
			<ng-container *nzModalContent>
				<nz-descriptions *ngIf="selectedUser as user" nzSize="small" [nzColumn]="1" nzBordered>
					<nz-descriptions-item nzTitle="Mã nhân viên">{{ user.employee_code }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Họ tên">{{ user.full_name }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Email">{{ user.email }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Vai trò"><nz-tag nzColor="blue">{{ user.role_name }}</nz-tag></nz-descriptions-item>
					<nz-descriptions-item nzTitle="Điện thoại">{{ user.phone || '—' }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Chức danh">{{ user.job_title || '—' }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Phòng ban">{{ deptName(user.department_id) }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Trạng thái">{{ user.is_active ? 'Active' : 'Inactive' }}</nz-descriptions-item>
				</nz-descriptions>
			</ng-container>
		</nz-modal>

		<!-- Reset password modal -->
		<nz-modal
			[(nzVisible)]="resetVisible"
			nzTitle="Reset mật khẩu"
			(nzOnOk)="submitReset.emit()"
			(nzOnCancel)="resetVisibleChange.emit(false)"
			[nzOkLoading]="saving"
			nzOkText="Đặt lại"
			id="reset-password-modal"
		>
			<ng-container *nzModalContent>
				<p class="muted" style="margin-bottom:1rem">Đặt mật khẩu mới cho <strong class="text-strong">{{ selectedUser?.full_name }}</strong></p>
				<input nz-input type="password" [(ngModel)]="newPassword" (ngModelChange)="newPasswordChange.emit($event)" placeholder="Mật khẩu mới" id="new-password-input"/>
			</ng-container>
		</nz-modal>
	`,
	styles: [`
		:host {
			--admin-text-secondary: rgba(226, 232, 240, .82);
			--admin-text-strong: #e2e8f0;
		}
		.form-grid { display:grid; gap:.85rem }
		.form-field { display:grid; gap:.35rem; color:var(--admin-text-secondary); font-size:.85rem }
		.muted { color:var(--admin-text-secondary); font-size:.88rem }
		.text-strong { color:var(--admin-text-strong) }
	`]
})
export class UserPageModalsComponent {
	@Input({ required: true }) formMode: UserFormMode = 'create';
	@Input({ required: true }) userForm!: UserFormState;
	@Input({ required: true }) saving = false;
	@Input() selectedUser: UserListItem | null = null;
	@Input() newPassword = '';
	@Input() formVisible = false;
	@Input() detailVisible = false;
	@Input() resetVisible = false;
	@Input() roles: RoleResponse[] = [];
	@Input() departments: DepartmentResponse[] = [];
	@Input() allUsers: UserListItem[] = [];

	@Output() submitForm = new EventEmitter<void>();
	@Output() cancelForm = new EventEmitter<void>();
	@Output() submitReset = new EventEmitter<void>();
	@Output() formVisibleChange = new EventEmitter<boolean>();
	@Output() detailVisibleChange = new EventEmitter<boolean>();
	@Output() resetVisibleChange = new EventEmitter<boolean>();
	@Output() newPasswordChange = new EventEmitter<string>();

	deptName(id: number | null): string {
		if (id == null) return '—';
		return this.departments.find(d => d.id === id)?.name ?? `ID:${id}`;
	}
}
