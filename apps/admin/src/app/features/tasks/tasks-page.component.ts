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

import { TaskFilters, TaskResponse, TaskStatus } from '../../models/task.models';
import { TaskApiService } from '../../services/task-api.service';
import { ADMIN_DATE_FORMAT } from '../../shared/date-formats';

const STATUS_COLOR: Record<string, string> = {
	pending: 'orange', in_progress: 'blue', completed: 'green', cancelled: 'default'
};
const STATUS_LABEL: Record<string, string> = {
	pending: 'Chờ xử lý', in_progress: 'Đang thực hiện', completed: 'Hoàn thành', cancelled: 'Đã hủy'
};

@Component({
	selector: 'app-tasks-page',
	standalone: true,
	imports: [
		CommonModule, FormsModule,
		NzButtonModule, NzCardModule, NzIconModule, NzSelectModule,
		NzTableModule, NzTagModule, NzTooltipModule
	],
	template: `
		<section class="page-root" data-testid="tasks-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Operations</p>
					<h2>Quản lý công việc</h2>
					<p class="subtitle">Theo dõi và điều phối các task trong tổ chức.</p>
				</div>
			</div>

			<nz-card class="filter-card" [nzBordered]="false">
				<div class="filter-row">
					<label class="filter-item"><span>Trạng thái</span>
						<nz-select [(ngModel)]="filters.status" (ngModelChange)="applyFilters()" nzPlaceHolder="Tất cả" nzAllowClear style="width:170px">
							<nz-option nzValue="pending" nzLabel="Chờ xử lý"></nz-option>
							<nz-option nzValue="in_progress" nzLabel="Đang thực hiện"></nz-option>
							<nz-option nzValue="completed" nzLabel="Hoàn thành"></nz-option>
							<nz-option nzValue="cancelled" nzLabel="Đã hủy"></nz-option>
						</nz-select>
					</label>
					<button nz-button nzType="dashed" (click)="resetFilters()" id="reset-task-filters-btn">
						<span nz-icon nzType="reload"></span> Đặt lại
					</button>
					<button nz-button nzType="default" (click)="load()" style="margin-left:auto">
						<span nz-icon nzType="sync"></span> Tải lại
					</button>
				</div>
			</nz-card>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #taskTable [nzData]="filtered()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="tasks-table">
					<thead>
						<tr>
							<th nzWidth="50px">#</th>
							<th>Tiêu đề</th>
							<th nzWidth="130px">Trạng thái</th>
							<th nzWidth="110px">Ưu tiên</th>
							<th>Người thực hiện</th>
							<th nzWidth="120px">Hạn chót</th>
							<th nzWidth="180px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let t of taskTable.data; let i = index">
							<td class="idx-col">{{ i + 1 }}</td>
							<td>
								<div class="task-title">{{ t.title }}</div>
								<div class="task-desc" *ngIf="t.description">{{ t.description | slice:0:60 }}{{ t.description.length > 60 ? '...' : '' }}</div>
							</td>
							<td><nz-tag [nzColor]="statusColor(t.status)">{{ statusLabel(t.status) }}</nz-tag></td>
							<td>
								<nz-tag *ngIf="t.priority" [nzColor]="priorityColor(t.priority)">{{ t.priority }}</nz-tag>
								<span *ngIf="!t.priority" class="muted">—</span>
							</td>
							<td class="muted">{{ t.assignee_name || '—' }}</td>
							<td class="muted">{{ t.due_date ? (t.due_date | date:ADMIN_DATE_FORMAT) : '—' }}</td>
							<td nzAlign="right">
								<button *ngIf="t.status === 'pending'" nz-button nzType="text" nzSize="small" (click)="action(t,'start')" nz-tooltip="Bắt đầu" style="color:#60a5fa" [attr.data-testid]="'start-task-'+t.id"><span nz-icon nzType="play-circle"></span></button>
								<button *ngIf="t.status === 'in_progress'" nz-button nzType="text" nzSize="small" (click)="action(t,'complete')" nz-tooltip="Hoàn thành" style="color:#34d399" [attr.data-testid]="'complete-task-'+t.id"><span nz-icon nzType="check-circle"></span></button>
								<button *ngIf="t.status === 'pending' || t.status === 'in_progress'" nz-button nzDanger nzType="text" nzSize="small" (click)="action(t,'cancel')" nz-tooltip="Hủy" [attr.data-testid]="'cancel-task-'+t.id"><span nz-icon nzType="close-circle"></span></button>
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
		.filter-card, .table-card { background:rgba(15,23,42,.72); border-radius:1.2rem }
		.filter-row { display:flex; align-items:flex-end; gap:1rem; flex-wrap:wrap }
		.filter-item { display:grid; gap:.35rem; font-size:.85rem; color:rgba(226,232,240,.75) }
		.idx-col { color:rgba(148,163,184,.6); font-size:.82rem }
		.task-title { font-weight:600; color:#f1f5f9 }
		.task-desc { font-size:.8rem; color:rgba(148,163,184,.6); margin-top:.15rem }
		.muted { color:rgba(226,232,240,.65); font-size:.88rem }
	`]
})
export class TasksPageComponent implements OnInit {
	protected readonly ADMIN_DATE_FORMAT = ADMIN_DATE_FORMAT;
	private readonly taskApi = inject(TaskApiService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly all = signal<TaskResponse[]>([]);
	readonly filtered = signal<TaskResponse[]>([]);
	readonly loading = signal(false);
	filters: TaskFilters = {};

	ngOnInit(): void { this.load(); }

	async load(): Promise<void> {
		this.loading.set(true);
		try {
			const data = await firstValueFrom(this.taskApi.listTasks());
			this.all.set(data); this.applyFilters();
		} catch { this.message.error('Không thể tải danh sách tasks.'); }
		finally { this.loading.set(false); }
	}

	applyFilters(): void {
		let list = this.all();
		if (this.filters.status) list = list.filter(t => t.status === this.filters.status);
		this.filtered.set(list);
	}

	resetFilters(): void { this.filters = {}; this.applyFilters(); }

	action(task: TaskResponse, type: 'start' | 'complete' | 'cancel'): void {
		const labels = { start: 'Bắt đầu', complete: 'Hoàn thành', cancel: 'Hủy' };
		this.modal.confirm({
			nzTitle: `${labels[type]} task "${task.title}"?`,
			nzOkDanger: type === 'cancel',
			nzOkText: labels[type],
			nzOnOk: async () => {
				try {
					const updated = type === 'start'
						? await firstValueFrom(this.taskApi.startTask(task.id))
						: type === 'complete'
						? await firstValueFrom(this.taskApi.completeTask(task.id))
						: await firstValueFrom(this.taskApi.cancelTask(task.id));
					this.all.update(list => list.map(t => t.id === updated.id ? updated : t));
					this.applyFilters();
					this.message.success('Cập nhật thành công.');
				} catch { this.message.error('Thao tác thất bại.'); }
			}
		});
	}

	statusColor(s: TaskStatus): string { return STATUS_COLOR[s] ?? 'default'; }
	statusLabel(s: TaskStatus): string { return STATUS_LABEL[s] ?? s; }
	priorityColor(p: string): string {
		const m: Record<string, string> = { high: 'red', medium: 'orange', low: 'cyan' };
		return m[p.toLowerCase()] ?? 'default';
	}
}
