import { CommonModule } from '@angular/common';
import { Component, OnInit, computed, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDatePickerModule } from 'ng-zorro-antd/date-picker';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { firstValueFrom } from 'rxjs';

import { AttendanceResponse } from '../../models/attendance.models';
import { AuthStoreService } from '../../services/auth-store.service';
import { AttendanceApiService } from '../../services/attendance-api.service';
import { ADMIN_DATE_FORMAT, ADMIN_DATETIME_FORMAT } from '../../shared/date-formats';
import { mapAdminHttpError } from '../../shared/http-error-mapper';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

@Component({
	selector: 'app-attendance-page',
	standalone: true,
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzDatePickerModule, NzIconModule, NzTableModule, NzTagModule],
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
					<button nz-button nzType="default" (click)="load()" aria-label="Tải lại dữ liệu chấm công"><span nz-icon nzType="sync"></span> Tải lại</button>
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
	`]
})
export class AttendancePageComponent implements OnInit {
	protected readonly ADMIN_DATE_FORMAT = ADMIN_DATE_FORMAT;
	protected readonly ADMIN_DATETIME_FORMAT = ADMIN_DATETIME_FORMAT;
	private readonly attendanceApi = inject(AttendanceApiService);
	private readonly authStore = inject(AuthStoreService);
	private readonly message = inject(NzMessageService);

	readonly items = signal<AttendanceResponse[]>([]);
	readonly loading = signal(false);
	readonly actionLoading = signal(false);
	readonly currentUser = this.authStore.currentUser;
	startDate = new Date();
	endDate = new Date();

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
		this.startDate = new Date(this.endDate.getTime() - 7 * 24 * 60 * 60 * 1000);
		void this.load();
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
			this.message.error(feedback.action === 'toast-only' ? feedback.message : 'Không thể tải dữ liệu chấm công.');
		} finally {
			this.loading.set(false);
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
