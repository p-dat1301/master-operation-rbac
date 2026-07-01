import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDatePickerModule } from 'ng-zorro-antd/date-picker';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { AttendanceResponse } from '../../models/attendance.models';
import { AuthStoreService } from '../../services/auth-store.service';
import { AttendanceApiService } from '../../services/attendance-api.service';
import { RbacApiService } from '../../services/rbac-api.service';
import { ADMIN_DATE_FORMAT, ADMIN_DATETIME_FORMAT } from '../../shared/date-formats';
import { mapAdminHttpError } from '../../shared/http-error-mapper';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

@Component({
	selector: 'app-attendance-page',
	standalone: true,
	imports: [
		CommonModule,
		FormsModule,
		NzButtonModule,
		NzCardModule,
		NzDatePickerModule,
		NzIconModule,
		NzTableModule,
		NzTagModule,
		NzTooltipModule,
		NzSelectModule,
		NzInputModule
	],
	template: `
		<section class="page-root" data-testid="attendance-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Operations</p>
					<h2>Chấm công</h2>
					<p class="subtitle">Dữ liệu chấm công nhân viên theo khoảng thời gian.</p>
				</div>
				<div class="header-stats">
					<div class="stat-chip"><span class="stat-value">{{ items().length }}</span><span class="stat-label">Bản ghi</span></div>
					<div class="stat-chip"><span class="stat-value">{{ currentStatusLabel() }}</span><span class="stat-label">Trạng thái hiện tại</span></div>
				</div>
			</div>

			<nz-card class="current-user-card" [nzBordered]="false">
				<div class="current-user-panel">
					<div>
						<p class="eyebrow">Tài khoản hiện tại</p>
						<h3>{{ currentUserName() }}</h3>
						<p class="subtitle">{{ currentUserRole() }}</p>
					</div>
					<div class="current-state">
						<nz-tag [nzColor]="currentStatusColor()">{{ currentStatusLabel() }}</nz-tag>
						<p class="subtitle">{{ currentStatusDetail() }}</p>
					</div>
					<div class="current-actions">
						<button nz-button nzType="primary" [nzLoading]="actionLoading()" [disabled]="!canCheckIn()" (click)="checkIn()"><span nz-icon nzType="login"></span> Chấm vào</button>
						<button nz-button nzType="default" [nzLoading]="actionLoading()" [disabled]="!canCheckOut()" (click)="checkOut()"><span nz-icon nzType="logout"></span> Chấm ra</button>
					</div>
				</div>
			</nz-card>

			<nz-card class="filter-card" [nzBordered]="false">
				<div class="filter-row">
					<label class="filter-item"><span>Từ ngày</span><nz-date-picker [(ngModel)]="startDate" (ngModelChange)="load()"></nz-date-picker></label>
					<label class="filter-item"><span>Đến ngày</span><nz-date-picker [(ngModel)]="endDate" (ngModelChange)="load()"></nz-date-picker></label>
					
					<label class="filter-item" *ngIf="isAdmin() || isManager()">
						<span>Phòng ban</span>
						<nz-select [ngModel]="selectedDepartmentId()" (ngModelChange)="selectedDepartmentId.set($event)" nzPlaceHolder="Tất cả phòng ban" nzAllowClear style="min-width: 180px;">
							<nz-option *ngFor="let dept of filteredDepartments()" [nzValue]="dept.id" [nzLabel]="dept.name"></nz-option>
						</nz-select>
					</label>

					<label class="filter-item" *ngIf="isAdmin() || isManager()">
						<span>Tìm nhân viên</span>
						<input nz-input [ngModel]="userSearchQuery()" (ngModelChange)="userSearchQuery.set($event)" placeholder="Nhập tên hoặc ID..." style="max-width: 180px;" />
					</label>

					<button nz-button nzType="default" (click)="load()" aria-label="Tải lại dữ liệu chấm công"><span nz-icon nzType="sync"></span> Tải lại</button>
				</div>
			</nz-card>

			<nz-card class="heatmap-card" [nzBordered]="false" data-testid="attendance-heatmap-card">
				<div class="heatmap-title-row">
					<span nz-icon nzType="calendar" class="heatmap-icon"></span>
					<h3>Bản đồ nhiệt chấm công {{ isAdmin() ? 'toàn công ty' : (isManager() ? 'phòng ban quản lý' : 'cá nhân') }}</h3>
				</div>
				<div class="heatmap-wrapper">
					<!-- Legend / Chú thích dạng ngang gọn gàng -->
					<div class="heatmap-legend-row">
						<span class="legend-title">Chú thích:</span>
						<div class="legend-items-horizontal">
							<div class="legend-item-chip" [nz-tooltip]="'Đạt từ 8 giờ làm việc trở lên trong ngày'">
								<span class="legend-dot" style="background-color: #16a34a"></span>
								<span>Đủ công (≥8h)</span>
							</div>
							<div class="legend-item-chip" [nz-tooltip]="'Làm việc từ 4 đến dưới 8 giờ'">
								<span class="legend-dot" style="background-color: #ca8a04"></span>
								<span>Đi muộn/Về sớm (4h-8h)</span>
							</div>
							<div class="legend-item-chip" [nz-tooltip]="'Không đi làm hoặc làm việc ít hơn 4 giờ'">
								<span class="legend-dot" style="background-color: #dc2626"></span>
								<span>Vắng mặt (<4h)</span>
							</div>
							<div class="legend-item-chip" [nz-tooltip]="'Đã chấm công vào nhưng chưa chấm ra'">
								<span class="legend-dot" style="background-color: #4f46e5"></span>
								<span>Đang làm việc</span>
							</div>
							<div class="legend-item-chip" [nz-tooltip]="'Cuối tuần, nghỉ phép hoặc không có dữ liệu'">
								<span class="legend-dot" style="background-color: rgba(255, 255, 255, 0.15)"></span>
								<span>Không có dữ liệu</span>
							</div>
						</div>
					</div>

					<!-- Heatmap Row per User -->
					<div class="heatmap-user-rows">
						<div class="heatmap-user-row" *ngFor="let group of attendanceByUser()">
							<div class="heatmap-user-label" [nz-tooltip]="'User ID: ' + group.userId">
								<div class="user-avatar-small">{{ getInitials(group.userName) }}</div>
								<div class="user-info-text">
									<span class="user-name">{{ group.userName }}</span>
									<span class="user-id" *ngIf="showUserIdLabel(group.userName, group.userId)">ID: {{ group.userId }}</span>
								</div>
							</div>
							<div class="heatmap-user-cells">
								<div
									*ngFor="let day of heatmapDays"
									class="heatmap-cell"
									[class.is-today]="isToday(day)"
									[ngStyle]="{'background-color': getHeatmapColorForUser(day, group.records)}"
									[nz-tooltip]="getHeatmapTooltipForUser(day, group.records, group.userName)"
								>
									<span class="day-number" [style.color]="getHeatmapTextColorForUser(day, group.records)">{{ day.getDate() }}</span>
								</div>
							</div>
						</div>
						<div *ngIf="attendanceByUser().length === 0" class="heatmap-empty">
							Không tìm thấy dữ liệu chấm công cho bộ lọc hiện tại.
						</div>
					</div>
				</div>
			</nz-card>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table [nzData]="items()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="attendance-table">
					<thead>
						<tr>
							<th>#</th>
							<th>Nhân viên</th>
							<th>Ngày</th>
							<th>Giờ vào</th>
							<th>Giờ ra</th>
							<th nzAlign="right">Số phút</th>
							<th>Trạng thái</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let row of items(); let i = index">
							<td class="idx-col">{{ i + 1 }}</td>
							<td class="muted">{{ personLabel(row) }}</td>
							<td class="muted">{{ row.date | date:ADMIN_DATE_FORMAT }}</td>
							<td class="muted">{{ row.check_in | date:ADMIN_DATETIME_FORMAT }}</td>
							<td class="muted">{{ row.check_out ? (row.check_out | date:ADMIN_DATETIME_FORMAT) : '—' }}</td>
							<td nzAlign="right" class="muted">{{ row.total_minutes ?? '—' }}</td>
							<td><nz-tag [nzColor]="statusColor(row)">{{ statusLabel(row) }}</nz-tag></td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.header-stats { display:flex; gap:.75rem; flex-wrap:wrap }
		.stat-chip { display:flex; flex-direction:column; align-items:center; padding:.6rem 1.2rem; border-radius:1rem; min-width:120px; background:var(--admin-surface-field); border:1px solid var(--admin-border-subtle) }
		.stat-value { font-size:1rem; font-weight:700; color:var(--admin-text-primary); text-align:center }
		.stat-label { font-size:.74rem; color:var(--admin-text-muted) }
		.current-user-card { margin-bottom: .5rem }
		.current-user-panel { display:flex; justify-content:space-between; gap:1rem; align-items:center; flex-wrap:wrap }
		.current-user-panel h3 { margin:.15rem 0 0; font-size:1.15rem; color:var(--admin-text-primary) }
		.current-state { display:grid; justify-items:start; gap:.35rem }
		.current-actions { display:flex; gap:.75rem; flex-wrap:wrap }
		
		.heatmap-card {
			background: var(--admin-surface-card);
			border: 1px solid var(--admin-border-subtle);
			border-radius: 1.2rem;
			margin-bottom: .5rem;
		}
		.heatmap-title-row { display:flex; align-items:center; gap:.5rem; margin-bottom:1.2rem }
		.heatmap-title-row h3 { margin:0; font-size:1.05rem; font-weight:700; color:var(--admin-text-primary) }
		.heatmap-icon { color:var(--admin-action-primary-strong); font-size:1.2rem }
		.heatmap-wrapper { display:flex; flex-direction:column; gap:1rem; align-items:center; padding:.3rem 0; width:100% }
		
		/* Horizontal Legend row */
		.heatmap-legend-row { display:flex; align-items:center; gap:1rem; flex-wrap:wrap; width:100%; border-bottom:1px solid var(--admin-border-subtle); padding-bottom:1rem; margin-bottom:0.5rem }
		.legend-title { font-size:.82rem; font-weight:700; color:var(--admin-text-primary); margin:0 }
		.legend-items-horizontal { display:flex; gap:0.75rem; flex-wrap:wrap }
		.legend-item-chip { display:flex; align-items:center; gap:0.4rem; padding:0.25rem 0.6rem; background:rgba(255,255,255,0.03); border:1px solid rgba(255,255,255,0.05); border-radius:99px; font-size:0.78rem; color:var(--admin-text-secondary); cursor:help }
		.legend-dot { width:8px; height:8px; border-radius:50%; flex-shrink:0 }

		.heatmap-user-rows { display:grid; gap:1rem; width:100%; max-height:450px; overflow-y:auto; padding-right:.5rem }
		.heatmap-user-row { display:flex; align-items:center; gap:1.2rem; border-bottom:1px solid var(--admin-border-subtle); padding-bottom:.8rem }
		.heatmap-user-row:last-child { border-bottom:none; padding-bottom:0 }
		
		/* User Label with Avatar styling */
		.heatmap-user-label { width:190px; display:flex; align-items:center; gap:0.6rem; flex-shrink:0 }
		.user-avatar-small { width:28px; height:28px; border-radius:50%; background:linear-gradient(135deg, var(--admin-action-primary) 0%, var(--admin-action-primary-strong) 100%); color:#ffffff; font-size:0.75rem; font-weight:700; display:grid; place-items:center; flex-shrink:0 }
		.user-info-text { display:flex; flex-direction:column; min-width:0 }
		.heatmap-user-label .user-name { font-weight:700; font-size:.85rem; color:var(--admin-text-primary); white-space:nowrap; overflow:hidden; text-overflow:ellipsis }
		.heatmap-user-label .user-id { font-size:.74rem; color:var(--admin-text-muted); margin-top:.15rem }
		
		.heatmap-user-cells { display:flex; flex-wrap:wrap; gap:4px; flex-grow:1 }

		/* Premium larger cells */
		.heatmap-cell { width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; cursor:pointer; position:relative; transition:all 0.15s ease; border:1px solid rgba(255,255,255,0.03); background-color:rgba(255,255,255,0.04) }
		.heatmap-cell:hover { transform:scale(1.15); box-shadow:0 0 10px rgba(167,139,250,.4); border-color:rgba(167,139,250,.3); z-index:2 }
		
		/* Today indicator highlight */
		.heatmap-cell.is-today { box-shadow:0 0 0 2px var(--admin-action-primary-strong) !important; z-index:1 }
		
		.day-number { font-size:.76rem; font-weight:700; transition:color 0.15s ease }
		.heatmap-empty { text-align:center; color:var(--admin-text-muted); padding:2rem 0; font-size:.9rem }
	`]
})
export class AttendancePageComponent implements OnInit {
	protected readonly ADMIN_DATE_FORMAT = ADMIN_DATE_FORMAT;
	protected readonly ADMIN_DATETIME_FORMAT = ADMIN_DATETIME_FORMAT;
	private readonly attendanceApi = inject(AttendanceApiService);
	private readonly rbacApi = inject(RbacApiService);
	private readonly authStore = inject(AuthStoreService);
	private readonly message = inject(NzMessageService);

	readonly items = signal<AttendanceResponse[]>([]);
	readonly loading = signal(false);
	readonly actionLoading = signal(false);
	readonly currentUser = this.authStore.currentUser;
	startDate = new Date();
	endDate = new Date();

	readonly allDepartments = signal<any[]>([]);
	readonly selectedDepartmentId = signal<number | null>(null);
	readonly userSearchQuery = signal<string>('');

	readonly filteredDepartments = computed(() => {
		const allDepts = this.allDepartments();
		const isAdmin = this.isAdmin();
		if (isAdmin) {
			return allDepts;
		}
		const presentDeptIds = new Set(this.items().map(item => item.department_id).filter(id => id != null) as number[]);
		return allDepts.filter(dept => presentDeptIds.has(dept.id));
	});

	readonly attendanceByUser = computed(() => {
		const groups = new Map<number, { userId: number, userName: string, records: Map<string, AttendanceResponse> }>();
		const actor = this.currentUser();
		if (!actor) return [];

		const isAdmin = this.isAdmin();
		const isManager = this.isManager();

		let filteredItems = this.items();

		// If regular user, only keep their own items
		if (!isAdmin && !isManager) {
			filteredItems = filteredItems.filter(item => item.user_id === actor.id);
		} else {
			const deptId = this.selectedDepartmentId();
			if (deptId != null) {
				filteredItems = filteredItems.filter(item => item.department_id === deptId);
			}
			const query = this.userSearchQuery().trim().toLowerCase();
			if (query) {
				filteredItems = filteredItems.filter(item => 
					item.user_id.toString().includes(query) ||
					this.personLabel(item).toLowerCase().includes(query)
				);
			}
		}

		// Group items
		for (const item of filteredItems) {
			if (!groups.has(item.user_id)) {
				groups.set(item.user_id, {
					userId: item.user_id,
					userName: this.personLabel(item),
					records: new Map<string, AttendanceResponse>()
				});
			}
			const dateStr = this.toIsoDateString(item.date);
			groups.get(item.user_id)!.records.set(dateStr, item);
		}

		// Ensure the actor themselves is in the group if we are a regular user, even if empty
		if (!isAdmin && !isManager && !groups.has(actor.id)) {
			groups.set(actor.id, {
				userId: actor.id,
				userName: `${actor.full_name} (Bạn)`,
				records: new Map<string, AttendanceResponse>()
			});
		}

		return Array.from(groups.values()).sort((a, b) => {
			if (a.userId === actor.id) return -1;
			if (b.userId === actor.id) return 1;
			return a.userName.localeCompare(b.userName);
		});
	});

	get heatmapDays(): Date[] {
		const days: Date[] = [];
		const start = new Date(this.startDate);
		const end = new Date(this.endDate);
		start.setHours(0, 0, 0, 0);
		end.setHours(0, 0, 0, 0);
		const current = new Date(start);
		while (current <= end) {
			days.push(new Date(current));
			current.setDate(current.getDate() + 1);
		}
		return days;
	}

	readonly currentDayItem = computed(() => {
		const userId = this.currentUser()?.id;
		if (userId == null) return null;
		const today = this.toIsoDate(new Date());
		return this.items().find((item) => item.user_id === userId && this.toIsoDateString(item.date) === today) ?? null;
	});

	readonly currentStatusLabel = computed(() => {
		const item = this.currentDayItem();
		if (!item) return 'Chưa chấm công';
		if (item.check_in && !item.check_out) return 'Đang làm việc';
		if (item.check_in && item.check_out) return 'Đã chấm ra';
		return item.status || 'Chưa xác định';
	});

	readonly currentStatusColor = computed(() => {
		const item = this.currentDayItem();
		if (!item) return 'default';
		if (item.check_in && !item.check_out) return 'blue';
		if (item.check_out) return 'green';
		return 'gold';
	});

	readonly currentStatusDetail = computed(() => {
		const item = this.currentDayItem();
		if (!item) return 'Hôm nay chưa có bản ghi chấm công.';
		if (item.check_in && !item.check_out) return `Đã vào lúc ${this.formatDateTime(item.check_in)} · chờ chấm ra.`;
		if (item.check_in && item.check_out) return `Vào ${this.formatDateTime(item.check_in)} · ra ${this.formatDateTime(item.check_out)}.`;
		return `Trạng thái hiện tại: ${item.status || 'không rõ'}.`;
	});

	readonly currentUserName = computed(() => this.currentUser()?.full_name || 'Người dùng hiện tại');
	readonly currentUserRole = computed(() => this.currentUser()?.role_name || 'Vai trò không xác định');
	readonly canCheckIn = computed(() => !this.currentDayItem() || Boolean(this.currentDayItem() && this.currentDayItem()?.check_out));
	readonly canCheckOut = computed(() => Boolean(this.currentDayItem()?.check_in && !this.currentDayItem()?.check_out));

	ngOnInit(): void {
		this.endDate = new Date();
		this.startDate = new Date(this.endDate.getTime() - 30 * 24 * 60 * 60 * 1000);
		void this.load();
		void this.loadDepartments();
	}

	isAdmin(): boolean {
		return this.currentUser()?.role_name === 'admin';
	}

	isManager(): boolean {
		return this.currentUser()?.role_name === 'manager';
	}

	async load(): Promise<void> {
		this.loading.set(true);
		try {
			const data = await firstValueFrom(this.attendanceApi.listAttendance({
				start_date: this.toIsoDate(this.startDate),
				end_date: this.toIsoDate(this.endDate)
			}));
			this.items.set(data);
		} catch (error) {
			const feedback = mapAdminHttpError(error);
			this.message.error(`Không tải được dữ liệu chấm công: ${feedback.message}`);
		} finally {
			this.loading.set(false);
		}
	}

	private async loadDepartments(): Promise<void> {
		const actor = this.currentUser();
		if (!actor || (actor.role_name !== 'admin' && actor.role_name !== 'manager')) {
			return;
		}
		try {
			const depts = await firstValueFrom(this.rbacApi.listDepartments());
			this.allDepartments.set(depts);
		} catch (error) {
			console.error('Failed to load departments', error);
		}
	}

	async checkIn(): Promise<void> {
		await this.runAttendanceAction(() => this.attendanceApi.checkin());
	}

	async checkOut(): Promise<void> {
		await this.runAttendanceAction(() => this.attendanceApi.checkout());
	}

	personLabel(row: AttendanceResponse): string {
		return row.user_id === this.currentUser()?.id ? `${this.currentUserName()} (Bạn)` : `ID:${row.user_id}`;
	}

	statusLabel(row: AttendanceResponse): string {
		if (row.check_in && !row.check_out) return 'Đang làm việc';
		if (row.check_in && row.check_out) return 'Đã chấm ra';
		return row.status || 'unknown';
	}

	statusColor(row: AttendanceResponse): string {
		if (row.check_in && !row.check_out) return 'blue';
		if (row.check_out) return 'green';
		return 'default';
	}

	getHeatmapColorForUser(day: Date, records: Map<string, AttendanceResponse>): string {
		const dateStr = this.toIsoDate(day);
		const record = records.get(dateStr);
		if (!record) {
			return 'rgba(255, 255, 255, 0.04)'; // translucent grey for empty
		}
		if (record.check_in && !record.check_out) {
			return '#4f46e5'; // Indigo (Working)
		}
		if (record.check_in && record.check_out) {
			const minutes = record.total_minutes ?? 0;
			if (minutes >= 480) {
				return '#16a34a'; // Green solid
			}
			if (minutes >= 240) {
				return '#ca8a04'; // Yellow solid
			}
			return '#dc2626'; // Red solid
		}
		if (record.status === 'absent') {
			return '#dc2626'; // Red solid (Absent)
		}
		return 'rgba(255, 255, 255, 0.04)';
	}

	getHeatmapTextColorForUser(day: Date, records: Map<string, AttendanceResponse>): string {
		const dateStr = this.toIsoDate(day);
		const record = records.get(dateStr);
		if (!record) {
			return 'rgba(148, 163, 184, 0.4)'; // dim grey for empty days
		}
		return '#ffffff'; // White text on filled solid background
	}

	isToday(day: Date): boolean {
		const today = new Date();
		return day.getDate() === today.getDate() &&
			day.getMonth() === today.getMonth() &&
			day.getFullYear() === today.getFullYear();
	}

	getInitials(name: string): string {
		if (!name) return 'U';
		const cleanName = name.replace('(Bạn)', '').trim();
		const parts = cleanName.split(' ');
		if (parts.length >= 2) {
			return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
		}
		return cleanName.slice(0, 2).toUpperCase();
	}

	getHeatmapTooltipForUser(day: Date, records: Map<string, AttendanceResponse>, userName: string): string {
		const dateStr = this.toIsoDate(day);
		const formattedDate = day.toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'numeric', day: 'numeric' });
		const record = records.get(dateStr);
		if (!record) {
			return `${userName} · ${formattedDate}: Không có dữ liệu chấm công`;
		}
		let detail = '';
		if (record.check_in) {
			detail += `Vào: ${new Date(record.check_in).toLocaleTimeString('vi-VN')}`;
		}
		if (record.check_out) {
			detail += ` · Ra: ${new Date(record.check_out).toLocaleTimeString('vi-VN')}`;
		}
		if (record.total_minutes != null) {
			detail += ` (${Math.round(record.total_minutes / 60 * 10) / 10} giờ)`;
		}
		const statusText = this.statusLabel(record);
		return `${userName} · ${formattedDate} [${statusText}] ${detail}`;
	}

	showUserIdLabel(userName: string, userId: number): boolean {
		return userName !== `ID:${userId}` && userName !== `ID: ${userId}`;
	}

	private async runAttendanceAction(action: () => ReturnType<AttendanceApiService['checkin'] | AttendanceApiService['checkout']>): Promise<void> {
		this.actionLoading.set(true);
		try {
			await firstValueFrom(action());
			this.message.success('Đã cập nhật trạng thái chấm công.');
			await this.load();
		} catch (error) {
			const feedback = mapAdminHttpError(error);
			this.message.error(feedback.action === 'toast-only' ? feedback.message : 'Không thể cập nhật trạng thái chấm công.');
		} finally {
			this.actionLoading.set(false);
		}
	}

	private toIsoDate(value: Date): string {
		return value.toISOString().slice(0, 10);
	}

	private toIsoDateString(value: string): string {
		return value.slice(0, 10);
	}

	private formatDateTime(value: string): string {
		return new Date(value).toLocaleString('vi-VN');
	}
}
