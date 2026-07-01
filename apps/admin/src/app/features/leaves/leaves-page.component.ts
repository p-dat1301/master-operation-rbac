import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDescriptionsModule } from 'ng-zorro-antd/descriptions';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalModule, NzModalService } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import {
	LeaveBalanceResponse,
	LeaveBalanceUpdatePayload,
	LeaveCreatePayload,
	LeaveFilters,
	LeaveRequestResponse,
	LeaveReviewPayload,
	LeaveStatus,
	LeaveType,
	LeaveUpdatePayload
} from '../../models/leave.models';
import { LeaveApiService } from '../../services/leave-api.service';
import { runAdminAsync } from '../../shared/async-state';
import { ADMIN_DATE_FORMAT } from '../../shared/date-formats';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

type LeaveFormMode = 'create' | 'edit';
type LeaveReviewMode = 'approve' | 'reject';

type LeaveFormState = {
	leave_type: LeaveType;
	start_date: string;
	end_date: string;
	reason: string;
};

type BalanceFormState = {
	year: number | null;
	total_days: number | null;
	used_days: number | null;
};

const STATUS_COLOR: Record<string, string> = { pending: 'orange', approved: 'green', rejected: 'red', cancelled: 'default' };
const STATUS_LABEL: Record<string, string> = { pending: 'Chờ duyệt', approved: 'Đã duyệt', rejected: 'Từ chối', cancelled: 'Đã hủy' };
const LEAVE_TYPE_LABEL: Record<LeaveType, string> = { annual: 'Phép năm', sick: 'Ốm đau', unpaid: 'Không lương', other: 'Khác' };
const EMPTY_LEAVE_FORM: LeaveFormState = { leave_type: 'annual', start_date: '', end_date: '', reason: '' };

@Component({
	selector: 'app-leaves-page',
	standalone: true,
	imports: [
		CommonModule, FormsModule,
		NzButtonModule, NzCardModule, NzDescriptionsModule, NzIconModule, NzInputModule, NzModalModule, NzSelectModule,
		NzTableModule, NzTagModule, NzTooltipModule
	],
	template: `
		<section class="page-root" data-testid="leaves-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Leave Management</p>
					<h2>Đơn nghỉ phép</h2>
					<p class="subtitle">Duyệt, tạo và cập nhật yêu cầu nghỉ phép của nhân viên.</p>
				</div>
				<div class="header-actions">
					<div class="stat-row">
						<div class="stat-chip pending"><span class="sv">{{ countByStatus('pending') }}</span><span class="sl">Chờ duyệt</span></div>
						<div class="stat-chip approved"><span class="sv">{{ countByStatus('approved') }}</span><span class="sl">Đã duyệt</span></div>
					</div>
					<button nz-button nzType="primary" (click)="openCreateLeave()" data-testid="create-leave-btn"><span nz-icon nzType="plus"></span> Tạo đơn nghỉ</button>
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
							<nz-option nzValue="other" nzLabel="Khác"></nz-option>
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
						<button nz-button nzDanger [disabled]="selected.status !== 'pending'" (click)="review(selected,'reject')">Không duyệt</button>
					</div>
				</div>
				<nz-descriptions *ngIf="selectedLeave() as selected" nzBordered nzSize="small" class="detail-card">
					<nz-descriptions-item nzTitle="Loại">{{ leaveTypeLabel(selected.leave_type) }}</nz-descriptions-item>
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
							<th nzWidth="150px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let l of leaveTable.data; let i = index" (click)="selectLeave(l)" [class.selected-row]="selectedLeave()?.id === l.id">
							<td class="idx-col">{{ i + 1 }}</td>
							<td class="name-col">{{ l.user_name || 'ID:' + l.user_id }}</td>
							<td><nz-tag nzColor="geekblue">{{ leaveTypeLabel(l.leave_type) }}</nz-tag></td>
							<td class="muted">{{ l.start_date | date:ADMIN_DATE_FORMAT }}</td>
							<td class="muted">{{ l.end_date | date:ADMIN_DATE_FORMAT }}</td>
							<td class="muted">{{ l.reason || '—' }}</td>
							<td nzAlign="center"><nz-tag [nzColor]="statusColor(l.status)">{{ statusLabel(l.status) }}</nz-tag></td>
							<td nzAlign="right">
								<button nz-button nzType="text" nzSize="small" (click)="$event.stopPropagation(); openEdit(l)" nz-tooltip="Sửa" [disabled]="!canEdit(l)" [attr.aria-label]="'Sửa đơn nghỉ của ' + (l.user_name || ('ID ' + l.user_id))" [attr.data-testid]="'edit-leave-'+l.id"><span nz-icon nzType="edit"></span></button>
								<button *ngIf="l.status === 'pending'" nz-button nzType="text" nzSize="small" (click)="$event.stopPropagation(); review(l,'approve')" nz-tooltip="Duyệt" class="action-success" [attr.aria-label]="'Duyệt đơn nghỉ của ' + (l.user_name || ('ID ' + l.user_id))" [attr.data-testid]="'approve-leave-'+l.id"><span nz-icon nzType="check"></span></button>
								<button *ngIf="l.status === 'pending'" nz-button nzDanger nzType="text" nzSize="small" (click)="$event.stopPropagation(); review(l,'reject')" nz-tooltip="Không duyệt" [attr.aria-label]="'Không duyệt đơn nghỉ của ' + (l.user_name || ('ID ' + l.user_id))" [attr.data-testid]="'reject-leave-'+l.id"><span nz-icon nzType="close"></span></button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>

			<nz-modal [(nzVisible)]="showLeaveModal" [nzTitle]="leaveModalTitle" (nzOnOk)="submitLeaveForm()" (nzOnCancel)="closeLeaveModal()" [nzOkLoading]="saving()" [nzOkText]="leaveModalOkText" data-testid="leave-form-modal">
				<ng-container *nzModalContent>
					<div class="form-grid modal-grid-tight">
						<label class="form-field">
							<span>Loại nghỉ <span class="required">*</span></span>
							<nz-select [(ngModel)]="leaveForm.leave_type" data-testid="leave-form-type">
								<nz-option nzValue="annual" nzLabel="Phép năm"></nz-option>
								<nz-option nzValue="sick" nzLabel="Ốm đau"></nz-option>
								<nz-option nzValue="unpaid" nzLabel="Không lương"></nz-option>
								<nz-option nzValue="other" nzLabel="Khác"></nz-option>
							</nz-select>
						</label>
						<label class="form-field">
							<span>Từ ngày <span class="required">*</span></span>
							<input nz-input type="date" [(ngModel)]="leaveForm.start_date" data-testid="leave-form-start-date" />
						</label>
						<label class="form-field">
							<span>Đến ngày <span class="required">*</span></span>
							<input nz-input type="date" [(ngModel)]="leaveForm.end_date" data-testid="leave-form-end-date" />
						</label>
						<label class="form-field field-span-2">
							<span>Lý do</span>
							<textarea nz-input rows="3" [(ngModel)]="leaveForm.reason" data-testid="leave-form-reason"></textarea>
						</label>
					</div>
				</ng-container>
			</nz-modal>

			<nz-modal [(nzVisible)]="showBalanceModal" nzTitle="Sửa số dư nghỉ phép" (nzOnOk)="submitBalanceForm()" (nzOnCancel)="closeBalanceModal()" [nzOkLoading]="saving()" nzOkText="Lưu" data-testid="leave-balance-modal">
				<ng-container *nzModalContent>
					<div class="form-grid modal-grid-tight">
						<label class="form-field">
							<span>Năm <span class="required">*</span></span>
							<input nz-input type="number" [(ngModel)]="balanceForm.year" data-testid="leave-balance-year" />
						</label>
						<label class="form-field">
							<span>Tổng ngày <span class="required">*</span></span>
							<input nz-input type="number" [(ngModel)]="balanceForm.total_days" data-testid="leave-balance-total" />
						</label>
						<label class="form-field">
							<span>Đã dùng <span class="required">*</span></span>
							<input nz-input type="number" [(ngModel)]="balanceForm.used_days" data-testid="leave-balance-used" />
						</label>
					</div>
				</ng-container>
			</nz-modal>

			<nz-modal [(nzVisible)]="showReviewModal" [nzTitle]="reviewModalTitle" (nzOnOk)="submitReview()" (nzOnCancel)="closeReviewModal()" [nzOkLoading]="saving()" [nzOkText]="reviewMode === 'approve' ? 'Duyệt' : 'Từ chối'" [nzOkDanger]="reviewMode === 'reject'">
				<ng-container *nzModalContent>
					<div data-testid="leave-review-modal">
						<p class="muted">Xác nhận {{ reviewMode === 'approve' ? 'duyệt' : 'từ chối' }} đơn nghỉ của <strong class="text-strong">{{ selectedLeave()?.user_name || selectedLeave()?.user_id }}</strong>.</p>
						<label *ngIf="reviewMode === 'reject'" class="form-field review-reason">
							<span>Lý do từ chối</span>
							<textarea nz-input rows="3" [(ngModel)]="reviewReason" data-testid="leave-review-reason"></textarea>
						</label>
					</div>
				</ng-container>
			</nz-modal>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.header-actions { display:flex; gap:1rem; align-items:flex-start; flex-wrap:wrap }
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
		.form-grid { display:grid; gap:.95rem; grid-template-columns:repeat(2, minmax(0, 1fr)) }
		.field-span-2 { grid-column:span 2 }
		.modal-grid-tight { gap:.8rem }
		.review-reason { margin-top:.9rem }
		.required { color:var(--admin-action-danger) }
		@media (max-width: 768px) { .form-grid { grid-template-columns:1fr } .field-span-2 { grid-column:span 1 } }
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
	readonly saving = signal(false);
	readonly selectedLeave = signal<LeaveRequestResponse | null>(null);
	readonly balance = signal<LeaveBalanceResponse | null>(null);
	filters: LeaveFilters = {};

	showLeaveModal = false;
	showBalanceModal = false;
	showReviewModal = false;
	leaveModalMode: LeaveFormMode = 'create';
	reviewMode: LeaveReviewMode = 'approve';
	leaveForm: LeaveFormState = { ...EMPTY_LEAVE_FORM };
	balanceForm: BalanceFormState = { year: null, total_days: null, used_days: null };
	reviewReason = '';

	ngOnInit(): void { this.load(); }

	get leaveModalTitle(): string { return this.leaveModalMode === 'create' ? 'Tạo đơn nghỉ' : 'Sửa đơn nghỉ'; }
	get leaveModalOkText(): string { return this.leaveModalMode === 'create' ? 'Tạo' : 'Lưu'; }
	get reviewModalTitle(): string { return this.reviewMode === 'approve' ? 'Duyệt đơn nghỉ' : 'Từ chối đơn nghỉ'; }

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
	leaveTypeLabel(type: LeaveType): string { return LEAVE_TYPE_LABEL[type] ?? type; }

	selectLeave(leave: LeaveRequestResponse | null): void {
		this.selectedLeave.set(leave);
		if (leave) void this.loadBalance(leave.user_id);
		else this.balance.set(null);
	}

	async loadBalance(userId: number): Promise<void> {
		await runAdminAsync(this.leaveApi.getUserLeaveBalance(userId), {
			fallbackMessage: 'Không thể tải số dư nghỉ phép.',
			onSuccess: (balance) => this.balance.set(balance),
			onError: () => this.balance.set(null)
		});
	}

	review(leave: LeaveRequestResponse, action: LeaveReviewMode): void {
		this.selectedLeave.set(leave);
		this.reviewMode = action;
		this.reviewReason = action === 'reject' ? (leave.rejected_reason ?? '') : '';
		this.showReviewModal = true;
	}

	closeReviewModal(): void { this.showReviewModal = false; this.saving.set(false); }

	async submitReview(): Promise<void> {
		const leave = this.selectedLeave();
		if (!leave) { this.message.warning('Không có đơn nghỉ được chọn.'); return; }
		if (this.reviewMode === 'reject' && !this.reviewReason.trim()) {
			this.message.warning('Vui lòng nhập lý do từ chối.');
			return;
		}
		const payload: LeaveReviewPayload = this.reviewMode === 'reject' ? { action: 'reject', rejected_reason: this.reviewReason.trim() } : { action: 'approve' };
		await runAdminAsync(this.leaveApi.reviewLeave(leave.id, payload), {
			pending: this.saving,
			fallbackMessage: 'Thao tác thất bại.',
			onSuccess: (updated) => { this.applyLeaveMutation(updated, 'Cập nhật thành công.'); this.showReviewModal = false; },
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
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
					onSuccess: (updated) => this.applyLeaveMutation(updated, 'Hủy đơn thành công.'),
					onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
				});
			}
		});
	}

	openCreateLeave(): void {
		this.leaveModalMode = 'create';
		this.leaveForm = { ...EMPTY_LEAVE_FORM };
		this.showLeaveModal = true;
	}

	openEdit(leave: LeaveRequestResponse): void {
		if (!this.canEdit(leave)) return;
		this.leaveModalMode = 'edit';
		this.selectedLeave.set(leave);
		this.leaveForm = {
			leave_type: leave.leave_type,
			start_date: leave.start_date,
			end_date: leave.end_date,
			reason: leave.reason ?? ''
		};
		this.showLeaveModal = true;
	}

	closeLeaveModal(): void { this.showLeaveModal = false; this.saving.set(false); }

	async submitLeaveForm(): Promise<void> {
		if (!this.leaveForm.start_date || !this.leaveForm.end_date) { this.message.warning('Vui lòng nhập ngày bắt đầu và kết thúc.'); return; }
		if (this.leaveForm.start_date > this.leaveForm.end_date) { this.message.warning('Ngày bắt đầu phải sớm hơn hoặc bằng ngày kết thúc.'); return; }

		const payload: LeaveCreatePayload | LeaveUpdatePayload = {
			leave_type: this.leaveForm.leave_type,
			start_date: this.leaveForm.start_date,
			end_date: this.leaveForm.end_date,
			reason: this.leaveForm.reason.trim() || null
		};
		const selected = this.selectedLeave();
		const request = this.leaveModalMode === 'create' ? this.leaveApi.createLeave(payload as LeaveCreatePayload) : this.leaveApi.updateLeave(selected!.id, payload as LeaveUpdatePayload);
		await runAdminAsync(request, {
			pending: this.saving,
			fallbackMessage: this.leaveModalMode === 'create' ? 'Không thể tạo đơn nghỉ.' : 'Không thể cập nhật đơn nghỉ.',
			onSuccess: (saved) => {
				this.upsertLeave(saved);
				this.applyFilters();
				this.selectLeave(saved);
				this.showLeaveModal = false;
				this.message.success(this.leaveModalMode === 'create' ? 'Đã tạo đơn nghỉ.' : 'Đã cập nhật đơn nghỉ.');
			},
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	openBalanceEdit(balance: LeaveBalanceResponse): void {
		this.balanceForm = { year: balance.year, total_days: balance.total_days, used_days: balance.used_days };
		this.showBalanceModal = true;
	}

	closeBalanceModal(): void { this.showBalanceModal = false; this.saving.set(false); }

	async submitBalanceForm(): Promise<void> {
		const selected = this.selectedLeave();
		if (!selected) { this.message.warning('Không có nhân viên được chọn.'); return; }
		if (this.balanceForm.year == null || this.balanceForm.total_days == null || this.balanceForm.used_days == null) { this.message.warning('Vui lòng nhập đầy đủ số dư.'); return; }
		if (this.balanceForm.total_days < 0 || this.balanceForm.used_days < 0) { this.message.warning('Số ngày không được âm.'); return; }
		if (this.balanceForm.used_days > this.balanceForm.total_days) { this.message.warning('Đã dùng không được lớn hơn tổng ngày.'); return; }

		const payload: LeaveBalanceUpdatePayload = { year: this.balanceForm.year, total_days: this.balanceForm.total_days, used_days: this.balanceForm.used_days };
		await runAdminAsync(this.leaveApi.updateUserLeaveBalance(selected.user_id, payload), {
			pending: this.saving,
			fallbackMessage: 'Không thể cập nhật số dư.',
			onSuccess: (updated) => { this.balance.set(updated); this.showBalanceModal = false; this.message.success('Đã cập nhật số dư.'); },
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	canEdit(leave: LeaveRequestResponse): boolean { return leave.status === 'pending'; }
	statusColor(s: LeaveStatus): string { return STATUS_COLOR[s] ?? 'default'; }
	statusLabel(s: LeaveStatus): string { return STATUS_LABEL[s] ?? s; }

	private upsertLeave(leave: LeaveRequestResponse): void {
		this.all.update(list => list.some(item => item.id === leave.id) ? list.map(item => item.id === leave.id ? leave : item) : [leave, ...list]);
	}

	private applyLeaveMutation(leave: LeaveRequestResponse, successMessage: string): void {
		this.upsertLeave(leave);
		this.applyFilters();
		this.selectLeave(leave);
		this.message.success(successMessage);
	}

}
