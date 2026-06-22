import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDescriptionsModule } from 'ng-zorro-antd/descriptions';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalService } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import {
	LeaveBalanceResponse,
	LeaveFilters,
	LeaveRequestResponse,
	LeaveStatus,
	LeaveUpdatePayload
} from '../../models/leave.models';
import { LeaveApiService } from '../../services/leave-api.service';
import { runAdminAsync } from '../../shared/async-state';
import { ADMIN_DATE_FORMAT } from '../../shared/date-formats';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

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
			NzButtonModule, NzCardModule, NzDescriptionsModule, NzIconModule, NzInputModule, NzSelectModule,
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
				<div class="detail-toolbar" *ngIf="selectedLeave() as selected">
					<div>
						<p class="detail-title">Chi tiết đơn nghỉ</p>
						<p class="detail-subtitle">{{ selected.user_name || ('ID:' + selected.user_id) }} · {{ statusLabel(selected.status) }}</p>
					</div>
					<div class="detail-actions">
						<button nz-button nzType="default" [disabled]="!canEdit(selected)" (click)="openEdit(selected)">Sửa</button>
						<button nz-button nzType="default" [disabled]="selected.status !== 'pending'" (click)="cancel(selected)">Hủy</button>
						<button nz-button nzType="primary" [disabled]="selected.status !== 'pending'" (click)="review(selected,'approve')">Duyệt</button>
						<button nz-button nzDanger [disabled]="selected.status !== 'pending'" (click)="review(selected,'reject')">Từ chối</button>
					</div>
				</div>
				<nz-descriptions *ngIf="selectedLeave() as selected" nzBordered nzSize="small" class="detail-card">
					<nz-descriptions-item nzTitle="Loại">{{ selected.leave_type }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Từ ngày">{{ selected.start_date | date:ADMIN_DATE_FORMAT }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Đến ngày">{{ selected.end_date | date:ADMIN_DATE_FORMAT }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Lý do" [nzSpan]="3">{{ selected.reason || '—' }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Từ chối" [nzSpan]="3">{{ selected.rejected_reason || '—' }}</nz-descriptions-item>
				</nz-descriptions>
				<nz-descriptions *ngIf="balance() as b" nzBordered nzSize="small" class="detail-card" data-testid="leave-balance-card">
					<nz-descriptions-item nzTitle="Năm">{{ b.year }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Tổng ngày">{{ b.total_days }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Đã dùng">{{ b.used_days }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Đang chờ">{{ b.pending_days }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Còn lại">{{ b.remaining_days }}</nz-descriptions-item>
					<nz-descriptions-item nzTitle="Admin"><button nz-button nzSize="small" (click)="openBalanceEdit(b)">Sửa số dư</button></nz-descriptions-item>
				</nz-descriptions>
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
						<tr *ngFor="let l of leaveTable.data; let i = index" (click)="selectLeave(l)" [class.selected-row]="selectedLeave()?.id === l.id">
							<td class="idx-col">{{ i + 1 }}</td>
							<td class="name-col">{{ l.user_name || 'ID:' + l.user_id }}</td>
							<td><nz-tag nzColor="geekblue">{{ l.leave_type }}</nz-tag></td>
						<td class="muted">{{ l.start_date | date:ADMIN_DATE_FORMAT }}</td>
						<td class="muted">{{ l.end_date | date:ADMIN_DATE_FORMAT }}</td>

							<td class="muted">{{ l.reason || '—' }}</td>
							<td nzAlign="center"><nz-tag [nzColor]="statusColor(l.status)">{{ statusLabel(l.status) }}</nz-tag></td>
							<td nzAlign="right">
							<button *ngIf="l.status === 'pending'" nz-button nzType="text" nzSize="small" (click)="$event.stopPropagation(); review(l,'approve')" nz-tooltip="Duyệt" class="action-success" [attr.aria-label]="'Duyệt đơn nghỉ của ' + (l.user_name || ('ID ' + l.user_id))" [attr.data-testid]="'approve-leave-'+l.id"><span nz-icon nzType="check"></span></button>
							<button *ngIf="l.status === 'pending'" nz-button nzDanger nzType="text" nzSize="small" (click)="$event.stopPropagation(); review(l,'reject')" nz-tooltip="Từ chối" [attr.aria-label]="'Từ chối đơn nghỉ của ' + (l.user_name || ('ID ' + l.user_id))" [attr.data-testid]="'reject-leave-'+l.id"><span nz-icon nzType="close"></span></button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.stat-row { display:flex; gap:.75rem }
		.stat-chip { display:flex; flex-direction:column; align-items:center; padding:.5rem 1rem; border-radius:1rem; min-width:80px; background:var(--admin-surface-field); border:1px solid var(--admin-border-subtle) }
		.stat-chip.pending { background:rgba(251,191,36,.1); border-color:rgba(251,191,36,.25) }
		.stat-chip.approved { background:rgba(52,211,153,.1); border-color:rgba(52,211,153,.25) }
		.sv { font-size:1.3rem; font-weight:700; color:var(--admin-text-primary) }
		.sl { font-size:.74rem; color:var(--admin-text-muted) }
		.name-col { font-weight:600; color:var(--admin-text-primary) }
		.detail-toolbar { display:flex; justify-content:space-between; gap:1rem; align-items:flex-start; flex-wrap:wrap; margin-bottom:1rem }
		.detail-title { margin:0; font-weight:700; color:var(--admin-text-primary) }
		.detail-subtitle { margin:.2rem 0 0; color:var(--admin-text-secondary) }
		.detail-actions { display:flex; gap:.5rem; flex-wrap:wrap }
		.detail-card { margin-bottom:1rem }
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
	readonly selectedLeave = signal<LeaveRequestResponse | null>(null);
	readonly balance = signal<LeaveBalanceResponse | null>(null);
	filters: LeaveFilters = {};
	editDraft: LeaveUpdatePayload | null = null;

	ngOnInit(): void { this.load(); }

	async load(): Promise<void> {
		await runAdminAsync(this.leaveApi.listLeaves(), {
			pending: this.loading,
			fallbackMessage: 'Không thể tải đơn nghỉ phép.',
			onSuccess: (data) => { this.all.set(data); this.applyFilters(); this.selectLeave(data[0] ?? null); },
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	applyFilters(): void {
		let list = this.all();
		if (this.filters.status) list = list.filter(l => l.status === this.filters.status);
		if (this.filters.leave_type) list = list.filter(l => l.leave_type === this.filters.leave_type);
		this.filtered.set(list);
	}

	reset(): void { this.filters = {}; this.applyFilters(); }

	countByStatus(s: LeaveStatus): number { return this.all().filter(l => l.status === s).length; }

	selectLeave(leave: LeaveRequestResponse | null): void {
		this.selectedLeave.set(leave);
		this.editDraft = leave ? { leave_type: leave.leave_type, start_date: leave.start_date, end_date: leave.end_date, reason: leave.reason } : null;
		if (leave) void this.loadBalance(leave.user_id);
	}

	async loadBalance(userId: number): Promise<void> {
		await runAdminAsync(this.leaveApi.getUserLeaveBalance(userId), {
			fallbackMessage: 'Không thể tải số dư nghỉ phép.',
			onSuccess: (balance) => this.balance.set(balance),
			onError: () => this.balance.set(null)
		});
	}

	review(leave: LeaveRequestResponse, action: 'approve' | 'reject'): void {
		this.modal.confirm({
			nzTitle: `${action === 'approve' ? 'Duyệt' : 'Từ chối'} đơn nghỉ của "${leave.user_name || leave.user_id}"?`,
			nzOkDanger: action === 'reject',
			nzOkText: action === 'approve' ? 'Duyệt' : 'Từ chối',
			nzOnOk: async () => {
				const rejected_reason = action === 'reject' ? prompt('Lý do từ chối') ?? undefined : undefined;
				await runAdminAsync(this.leaveApi.reviewLeave(leave.id, { action, rejected_reason }), {
					fallbackMessage: 'Thao tác thất bại.',
					onSuccess: (updated) => {
						this.all.update(list => list.map(l => l.id === updated.id ? updated : l));
						this.applyFilters();
						this.selectLeave(updated);
						this.message.success('Cập nhật thành công.');
					},
					onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
				});
			}
		});
	}

	cancel(leave: LeaveRequestResponse): void {
		this.modal.confirm({
			nzTitle: `Hủy đơn nghỉ của "${leave.user_name || leave.user_id}"?`,
			nzOkDanger: true,
			nzOkText: 'Hủy đơn',
			nzOnOk: async () => {
				await runAdminAsync(this.leaveApi.cancelLeave(leave.id), {
					fallbackMessage: 'Thao tác thất bại.',
					onSuccess: (updated) => {
						this.all.update(list => list.map(l => l.id === updated.id ? updated : l));
						this.applyFilters();
						this.selectLeave(updated);
						this.message.success('Hủy đơn thành công.');
					},
					onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
				});
			}
		});
	}

	openEdit(leave: LeaveRequestResponse): void {
		if (!this.canEdit(leave)) return;

		const leave_type = prompt('Loại nghỉ (annual | sick | unpaid | other)', leave.leave_type)?.trim() as LeaveRequestResponse['leave_type'] | undefined;
		const start_date = prompt('Ngày bắt đầu (YYYY-MM-DD)', leave.start_date)?.trim();
		const end_date = prompt('Ngày kết thúc (YYYY-MM-DD)', leave.end_date)?.trim();
		const reasonInput = prompt('Lý do', leave.reason ?? '')?.trim();
		if (!leave_type || !start_date || !end_date) return;

		const payload: LeaveUpdatePayload = {
			leave_type,
			start_date,
			end_date,
			reason: reasonInput || null
		};

		this.modal.confirm({
			nzTitle: 'Lưu chỉnh sửa đơn nghỉ?',
			nzContent: 'Sẽ cập nhật trực tiếp đơn nghỉ bằng route PUT /api/v1/leaves/{id}.',
			nzOkText: 'Lưu',
			nzOnOk: async () => {
				await runAdminAsync(this.leaveApi.updateLeave(leave.id, payload), {
					fallbackMessage: 'Không thể cập nhật đơn nghỉ.',
					onSuccess: (updated) => {
						this.all.update(list => list.map(item => item.id === updated.id ? updated : item));
						this.applyFilters();
						this.selectLeave(updated);
						this.message.success('Cập nhật đơn nghỉ thành công.');
					},
					onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
				});
			}
		});
	}

	openBalanceEdit(balance: LeaveBalanceResponse): void {
		const total = Number(prompt('Tổng ngày', String(balance.total_days)));
		const used = Number(prompt('Đã dùng', String(balance.used_days)));
		if (Number.isNaN(total) || Number.isNaN(used)) return;
		void runAdminAsync(this.leaveApi.updateUserLeaveBalance(balance.user_id, { year: balance.year, total_days: total, used_days: used }), {
			fallbackMessage: 'Không thể cập nhật số dư.',
			onSuccess: (updated) => this.balance.set(updated),
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	canEdit(leave: LeaveRequestResponse): boolean { return leave.status === 'pending'; }

	statusColor(s: LeaveStatus): string { return STATUS_COLOR[s] ?? 'default'; }
	statusLabel(s: LeaveStatus): string { return STATUS_LABEL[s] ?? s; }

}
