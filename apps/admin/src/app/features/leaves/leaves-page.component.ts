import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalService } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { LeaveFilters, LeaveRequestResponse, LeaveStatus } from '../../models/leave.models';
import { LeaveApiService } from '../../services/leave-api.service';
import { ADMIN_DATE_FORMAT } from '../../shared/date-formats';

const STATUS_COLOR: Record<string, string> = {
	pending: 'orange', approved: 'green', rejected: 'red', cancelled: 'default'
};
const STATUS_LABEL: Record<string, string> = {
	pending: 'Chờ duyệt', approved: 'Đã duyệt', rejected: 'Từ chối', cancelled: 'Đã hủy'
};

@Component({
	selector: 'app-leaves-page',
	standalone: true,
	imports: [
		CommonModule, FormsModule,
		NzButtonModule, NzCardModule, NzIconModule, NzSelectModule,
		NzTableModule, NzTagModule, NzTooltipModule
	],
	template: `
		<section class="page-root" data-testid="leaves-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Leave Management</p>
					<h2>Đơn nghỉ phép</h2>
					<p class="subtitle">Duyệt và quản lý yêu cầu nghỉ phép của nhân viên.</p>
				</div>
				<div class="stat-row">
					<div class="stat-chip pending"><span class="sv">{{ countByStatus('pending') }}</span><span class="sl">Chờ duyệt</span></div>
					<div class="stat-chip approved"><span class="sv">{{ countByStatus('approved') }}</span><span class="sl">Đã duyệt</span></div>
				</div>
			</div>

			<nz-card class="filter-card" [nzBordered]="false">
				<div class="filter-row">
					<label class="filter-item"><span>Trạng thái</span>
						<nz-select [(ngModel)]="filters.status" (ngModelChange)="applyFilters()" nzPlaceHolder="Tất cả" nzAllowClear style="width:160px">
							<nz-option nzValue="pending" nzLabel="Chờ duyệt"></nz-option>
							<nz-option nzValue="approved" nzLabel="Đã duyệt"></nz-option>
							<nz-option nzValue="rejected" nzLabel="Từ chối"></nz-option>
							<nz-option nzValue="cancelled" nzLabel="Đã hủy"></nz-option>
						</nz-select>
					</label>
					<label class="filter-item"><span>Loại nghỉ</span>
						<nz-select [(ngModel)]="filters.leave_type" (ngModelChange)="applyFilters()" nzPlaceHolder="Tất cả" nzAllowClear style="width:140px">
							<nz-option nzValue="annual" nzLabel="Phép năm"></nz-option>
							<nz-option nzValue="sick" nzLabel="Ốm đau"></nz-option>
							<nz-option nzValue="unpaid" nzLabel="Không lương"></nz-option>
						</nz-select>
					</label>
					<button nz-button nzType="dashed" (click)="reset()"><span nz-icon nzType="reload"></span> Đặt lại</button>
				</div>
			</nz-card>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #leaveTable [nzData]="filtered()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="leaves-table">
					<thead>
						<tr>
							<th nzWidth="50px">#</th>
							<th>Nhân viên</th>
							<th nzWidth="120px">Loại</th>
							<th nzWidth="110px">Từ ngày</th>
							<th nzWidth="110px">Đến ngày</th>
							<th>Lý do</th>
							<th nzWidth="120px" nzAlign="center">Trạng thái</th>
							<th nzWidth="130px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let l of leaveTable.data; let i = index">
							<td class="idx-col">{{ i + 1 }}</td>
							<td class="name-col">{{ l.user_name || 'ID:' + l.user_id }}</td>
							<td><nz-tag nzColor="geekblue">{{ l.leave_type }}</nz-tag></td>
						<td class="muted">{{ l.start_date | date:ADMIN_DATE_FORMAT }}</td>
						<td class="muted">{{ l.end_date | date:ADMIN_DATE_FORMAT }}</td>

							<td class="muted">{{ l.reason || '—' }}</td>
							<td nzAlign="center"><nz-tag [nzColor]="statusColor(l.status)">{{ statusLabel(l.status) }}</nz-tag></td>
							<td nzAlign="right">
								<button *ngIf="l.status === 'pending'" nz-button nzType="text" nzSize="small" (click)="doAction(l,'approve')" nz-tooltip="Duyệt" style="color:#34d399" [attr.data-testid]="'approve-leave-'+l.id"><span nz-icon nzType="check"></span></button>
								<button *ngIf="l.status === 'pending'" nz-button nzDanger nzType="text" nzSize="small" (click)="doAction(l,'reject')" nz-tooltip="Từ chối" [attr.data-testid]="'reject-leave-'+l.id"><span nz-icon nzType="close"></span></button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [`
		.page-root { display:grid; gap:1.5rem }
		.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap }
		h2 { margin:.2rem 0 0; font-size:clamp(1.4rem,2.5vw,2rem); color:#f8fafc }
		.eyebrow { margin:0; font-size:.76rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#7dd3fc }
		.subtitle { margin:.4rem 0 0; color:rgba(226,232,240,.65); font-size:.9rem }
		.stat-row { display:flex; gap:.75rem }
		.stat-chip { display:flex; flex-direction:column; align-items:center; padding:.5rem 1rem; border-radius:1rem; min-width:80px }
		.stat-chip.pending { background:rgba(251,191,36,.1); border:1px solid rgba(251,191,36,.25) }
		.stat-chip.approved { background:rgba(52,211,153,.1); border:1px solid rgba(52,211,153,.25) }
		.sv { font-size:1.3rem; font-weight:700; color:#f8fafc }
		.sl { font-size:.74rem; color:rgba(148,163,184,.7) }
		.filter-card, .table-card { background:rgba(15,23,42,.72); border-radius:1.2rem }
		.filter-row { display:flex; align-items:flex-end; gap:1rem; flex-wrap:wrap }
		.filter-item { display:grid; gap:.35rem; font-size:.85rem; color:rgba(226,232,240,.75) }
		.idx-col { color:rgba(148,163,184,.6); font-size:.82rem }
		.name-col { font-weight:600; color:#f1f5f9 }
		.muted { color:rgba(226,232,240,.65); font-size:.88rem }
	`]
})
export class LeavesPageComponent implements OnInit {
	protected readonly ADMIN_DATE_FORMAT = ADMIN_DATE_FORMAT;
	private readonly leaveApi = inject(LeaveApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly all = signal<LeaveRequestResponse[]>([]);
	readonly filtered = signal<LeaveRequestResponse[]>([]);
	readonly loading = signal(false);
	filters: LeaveFilters = {};

	ngOnInit(): void { this.load(); }

	async load(): Promise<void> {
		this.loading.set(true);
		try {
			const data = await firstValueFrom(this.leaveApi.listLeaves());
			this.all.set(data); this.applyFilters();
		} catch { this.message.error('Không thể tải đơn nghỉ phép.'); }
		finally { this.loading.set(false); }
	}

	applyFilters(): void {
		let list = this.all();
		if (this.filters.status) list = list.filter(l => l.status === this.filters.status);
		if (this.filters.leave_type) list = list.filter(l => l.leave_type === this.filters.leave_type);
		this.filtered.set(list);
	}

	reset(): void { this.filters = {}; this.applyFilters(); }

	countByStatus(s: LeaveStatus): number { return this.all().filter(l => l.status === s).length; }

	doAction(leave: LeaveRequestResponse, type: 'approve' | 'reject'): void {
		const label = type === 'approve' ? 'Duyệt' : 'Từ chối';
		this.modal.confirm({
			nzTitle: `${label} đơn nghỉ của "${leave.user_name || leave.user_id}"?`,
			nzOkDanger: type === 'reject', nzOkText: label,
			nzOnOk: async () => {
				try {
					const updated = type === 'approve'
						? await firstValueFrom(this.leaveApi.approveLeave(leave.id))
						: await firstValueFrom(this.leaveApi.rejectLeave(leave.id));
					this.all.update(list => list.map(l => l.id === updated.id ? updated : l));
					this.applyFilters();
					this.message.success(`${label} thành công.`);
				} catch { this.message.error('Thao tác thất bại.'); }
			}
		});
	}

	statusColor(s: LeaveStatus): string { return STATUS_COLOR[s] ?? 'default'; }
	statusLabel(s: LeaveStatus): string { return STATUS_LABEL[s] ?? s; }
}
