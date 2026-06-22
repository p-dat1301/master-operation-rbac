import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
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
				</div>
			</div>

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
							<td class="muted">ID:{{ row.user_id }}</td>
							<td class="muted">{{ row.date | date:ADMIN_DATE_FORMAT }}</td>
							<td class="muted">{{ row.check_in | date:ADMIN_DATETIME_FORMAT }}</td>
							<td class="muted">{{ row.check_out ? (row.check_out | date:ADMIN_DATETIME_FORMAT) : '—' }}</td>
							<td nzAlign="right" class="muted">{{ row.total_minutes ?? '—' }}</td>
							<td><nz-tag [nzColor]="row.status === 'checked_out' ? 'green' : 'blue'">{{ row.status || 'unknown' }}</nz-tag></td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.header-stats { display:flex; gap:.75rem }
		.stat-chip { display:flex; flex-direction:column; align-items:center; padding:.6rem 1.2rem; border-radius:1rem; min-width:90px; background:var(--admin-surface-field); border:1px solid var(--admin-border-subtle) }
		.stat-value { font-size:1.4rem; font-weight:700; color:var(--admin-text-primary) }
		.stat-label { font-size:.74rem; color:var(--admin-text-muted) }
	`]
})
export class AttendancePageComponent implements OnInit {
	protected readonly ADMIN_DATE_FORMAT = ADMIN_DATE_FORMAT;
	protected readonly ADMIN_DATETIME_FORMAT = ADMIN_DATETIME_FORMAT;
	private readonly attendanceApi = inject(AttendanceApiService);
	private readonly message = inject(NzMessageService);

	readonly items = signal<AttendanceResponse[]>([]);
	readonly loading = signal(false);
	startDate = new Date();
	endDate = new Date();

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

	private toIsoDate(value: Date): string {
		return value.toISOString().slice(0, 10);
	}
}
