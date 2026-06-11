import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzBadgeModule } from 'ng-zorro-antd/badge';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalModule, NzModalService } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { UserFilters, UserListItem } from '../../models/user.models';
import { UserApiService } from '../../services/user-api.service';

@Component({
	selector: 'app-users-page',
	standalone: true,
	imports: [
		CommonModule, FormsModule,
		NzBadgeModule, NzButtonModule, NzCardModule, NzIconModule,
		NzModalModule, NzSelectModule, NzTableModule, NzTagModule, NzTooltipModule
	],
	template: `
		<section class="page-root" data-testid="users-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">HR Management</p>
					<h2>Quản lý người dùng</h2>
					<p class="subtitle">Danh sách tài khoản nhân viên trong hệ thống.</p>
				</div>
				<div class="header-stats">
					<div class="stat-chip active"><span class="stat-value">{{ activeCount() }}</span><span class="stat-label">Active</span></div>
					<div class="stat-chip inactive"><span class="stat-value">{{ inactiveCount() }}</span><span class="stat-label">Inactive</span></div>
				</div>
			</div>

			<nz-card class="filter-card" [nzBordered]="false">
				<div class="filter-row">
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
			</nz-card>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #userTable [nzData]="filteredUsers()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="users-table">
					<thead>
						<tr>
							<th nzWidth="50px">#</th>
							<th>Nhân viên</th>
							<th>Email</th>
							<th>Vai trò</th>
							<th>Chức danh</th>
							<th nzWidth="120px" nzAlign="center">Trạng thái</th>
							<th nzWidth="140px" nzAlign="right">Hành động</th>
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
							<td nzAlign="center">
								<nz-badge [nzStatus]="user.is_active ? 'success' : 'default'" [nzText]="user.is_active ? 'Active' : 'Inactive'"></nz-badge>
							</td>
							<td nzAlign="right">
								<button *ngIf="user.is_active" nz-button nzDanger nzType="text" nzSize="small" (click)="toggleUser(user)" nz-tooltip="Vô hiệu hóa" [attr.data-testid]="'deactivate-'+user.id"><span nz-icon nzType="stop"></span></button>
								<button *ngIf="!user.is_active" nz-button nzType="text" nzSize="small" (click)="toggleUser(user)" nz-tooltip="Kích hoạt" style="color:#34d399" [attr.data-testid]="'activate-'+user.id"><span nz-icon nzType="check-circle"></span></button>
								<button nz-button nzType="text" nzSize="small" (click)="openResetPassword(user)" nz-tooltip="Reset mật khẩu" style="color:#fbbf24" [attr.data-testid]="'reset-pwd-'+user.id"><span nz-icon nzType="lock"></span></button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>

			<nz-modal [(nzVisible)]="showResetModal" nzTitle="Reset mật khẩu" (nzOnOk)="submitResetPassword()" (nzOnCancel)="showResetModal=false" [nzOkLoading]="saving()" nzOkText="Đặt lại" id="reset-password-modal">
				<ng-container *nzModalContent>
					<p class="muted" style="margin-bottom:1rem">Đặt mật khẩu mới cho <strong style="color:#f1f5f9">{{ selectedUser()?.full_name }}</strong></p>
					<input nz-input type="password" [(ngModel)]="newPassword" placeholder="Mật khẩu mới" id="new-password-input"/>
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
		.header-stats { display:flex; gap:.75rem; flex-wrap:wrap }
		.stat-chip { display:flex; flex-direction:column; align-items:center; padding:.6rem 1.2rem; border-radius:1rem; min-width:90px }
		.stat-chip.active { background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.25) }
		.stat-chip.inactive { background:rgba(148,163,184,.08); border:1px solid rgba(148,163,184,.15) }
		.stat-value { font-size:1.4rem; font-weight:700; color:#f8fafc }
		.stat-label { font-size:.74rem; color:rgba(148,163,184,.7); margin-top:.1rem }
		.filter-card, .table-card { background:rgba(15,23,42,.72); border-radius:1.2rem }
		.filter-row { display:flex; align-items:flex-end; gap:1rem; flex-wrap:wrap }
		.filter-item { display:grid; gap:.35rem; font-size:.85rem; color:rgba(226,232,240,.75) }
		.idx-col { color:rgba(148,163,184,.6); font-size:.82rem }
		.user-cell { display:flex; align-items:center; gap:.75rem }
		.avatar { width:2.2rem; height:2.2rem; border-radius:50%; background:linear-gradient(135deg,#0ea5e9,#2563eb); display:grid; place-items:center; font-size:.75rem; font-weight:700; color:#fff; flex-shrink:0 }
		.user-name { font-weight:600; color:#f1f5f9 }
		.user-code { font-size:.78rem; color:rgba(148,163,184,.65) }
		.muted { color:rgba(226,232,240,.65); font-size:.88rem }
	`]
})
export class UsersPageComponent implements OnInit {
	private readonly userApi = inject(UserApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly allUsers = signal<UserListItem[]>([]);
	readonly filteredUsers = signal<UserListItem[]>([]);
	readonly loading = signal(false);
	readonly saving = signal(false);
	readonly selectedUser = signal<UserListItem | null>(null);

	showResetModal = false;
	newPassword = '';
	filters: UserFilters = {};

	activeCount = () => this.allUsers().filter(u => u.is_active).length;
	inactiveCount = () => this.allUsers().filter(u => !u.is_active).length;

	ngOnInit(): void { this.loadUsers(); }

	private async loadUsers(): Promise<void> {
		this.loading.set(true);
		try {
			const result = await firstValueFrom(this.userApi.listUsers());
			this.allUsers.set(result);
			this.applyFilters();
		} catch { this.message.error('Không thể tải danh sách người dùng.'); }
		finally { this.loading.set(false); }
	}

	applyFilters(): void {
		let list = this.allUsers();
		if (this.filters.is_active != null) list = list.filter(u => u.is_active === this.filters.is_active);
		this.filteredUsers.set(list);
	}

	resetFilters(): void { this.filters = {}; this.applyFilters(); }

	toggleUser(user: UserListItem): void {
		const action = user.is_active ? 'vô hiệu hóa' : 'kích hoạt';
		this.modal.confirm({
			nzTitle: `${action.charAt(0).toUpperCase() + action.slice(1)} "${user.full_name}"?`,
			nzOkDanger: user.is_active, nzOkText: action.charAt(0).toUpperCase() + action.slice(1),
			nzOnOk: async () => {
				try {
					const updated = user.is_active
						? await firstValueFrom(this.userApi.deactivateUser(user.id))
						: await firstValueFrom(this.userApi.activateUser(user.id));
					this.allUsers.update(list => list.map(u => u.id === updated.id ? updated : u));
					this.applyFilters();
					this.message.success(`Đã ${action} tài khoản.`);
				} catch { this.message.error('Thao tác thất bại.'); }
			}
		});
	}

	openResetPassword(user: UserListItem): void {
		this.selectedUser.set(user); this.newPassword = ''; this.showResetModal = true;
	}

	async submitResetPassword(): Promise<void> {
		const user = this.selectedUser();
		if (!user || !this.newPassword) return;
		this.saving.set(true);
		try {
			await firstValueFrom(this.userApi.resetPassword(user.id, this.newPassword));
			this.showResetModal = false;
			this.message.success('Đã đặt lại mật khẩu.');
		} catch { this.message.error('Đặt lại mật khẩu thất bại.'); }
		finally { this.saving.set(false); }
	}

	getInitials(name: string): string {
		return name.split(' ').slice(-2).map(n => n[0]).join('').toUpperCase();
	}
}
