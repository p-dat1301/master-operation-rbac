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
import { DepartmentResponse } from '../../models/rbac.models';
import { TaskCreateRequest, TaskFilters, TaskResponse, TaskStatus, TaskUpdateRequest } from '../../models/task.models';
import { UserListItem } from '../../models/user.models';
import { AuthStoreService } from '../../services/auth-store.service';
import { RbacApiService } from '../../services/rbac-api.service';
import { TaskApiService } from '../../services/task-api.service';
import { UserApiService } from '../../services/user-api.service';
import { runAdminAsync } from '../../shared/async-state';
import { ADMIN_DATE_FORMAT } from '../../shared/date-formats';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

type TaskFormMode = 'create' | 'edit';

type TaskFormState = {
	task_code: string;
	title: string;
	description: string;
	priority: string;
	assignee_id: number | null;
	department_id: number | null;
	start_date: string;
	due_date: string;
	estimated_hours: number | null;
};

type SelectOption = { label: string; value: number };

const STATUS_COLOR: Record<string, string> = { pending: 'orange', in_progress: 'blue', completed: 'green', cancelled: 'default' };
const STATUS_LABEL: Record<string, string> = { pending: 'Chờ xử lý', in_progress: 'Đang thực hiện', completed: 'Hoàn thành', cancelled: 'Đã hủy' };
const PRIORITY_OPTIONS = ['high', 'medium', 'low'] as const;
const EMPTY_TASK_FORM: TaskFormState = { task_code: '', title: '', description: '', priority: '', assignee_id: null, department_id: null, start_date: '', due_date: '', estimated_hours: null };

@Component({
	selector: 'app-tasks-page',
	standalone: true,
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzDescriptionsModule, NzIconModule, NzInputModule, NzModalModule, NzSelectModule, NzTableModule, NzTagModule, NzTooltipModule],
	template: `
		<section class="page-root" data-testid="tasks-page">
			<div class="page-header">
				<div><p class="eyebrow">Operations</p><h2>Quản lý công việc</h2><p class="subtitle">Theo dõi và điều phối công việc trong tổ chức.</p></div>
				<button *ngIf="canCreateTask()" nz-button nzType="primary" (click)="openCreateTask()" data-testid="create-task-btn"><span nz-icon nzType="plus"></span> Tạo công việc</button>
			</div>

			<nz-card class="filter-card" [nzBordered]="false"><div class="filter-row">
				<label class="filter-item"><span>Trạng thái</span><nz-select [(ngModel)]="filters.status" (ngModelChange)="applyFilters()" nzPlaceHolder="Tất cả" nzAllowClear style="width:170px">
					<nz-option nzValue="pending" nzLabel="Chờ xử lý"></nz-option><nz-option nzValue="in_progress" nzLabel="Đang thực hiện"></nz-option><nz-option nzValue="completed" nzLabel="Hoàn thành"></nz-option><nz-option nzValue="cancelled" nzLabel="Đã hủy"></nz-option>
				</nz-select></label>
				<button nz-button nzType="dashed" (click)="resetFilters()" id="reset-task-filters-btn"><span nz-icon nzType="reload"></span> Đặt lại</button>
				<button nz-button nzType="default" (click)="load()" style="margin-left:auto"><span nz-icon nzType="sync"></span> Tải lại</button>
			</div></nz-card>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #taskTable [nzData]="filtered()" [nzLoading]="loading()" [nzPageSize]="15" nzSize="middle" data-testid="tasks-table">
					<thead><tr><th nzWidth="50px">#</th><th>Tiêu đề</th><th nzWidth="130px">Trạng thái</th><th nzWidth="110px">Ưu tiên</th><th>Người thực hiện</th><th nzWidth="120px">Hạn chót</th><th nzWidth="300px" nzAlign="right">Hành động</th></tr></thead>
					<tbody><tr *ngFor="let t of taskTable.data; let i = index"><td class="idx-col">{{ i + 1 }}</td><td><div class="task-title">{{ t.title }}</div><div class="task-meta">{{ t.task_code || '—' }}</div><div class="task-desc" *ngIf="t.description">{{ t.description | slice:0:60 }}{{ t.description.length > 60 ? '...' : '' }}</div></td><td><nz-tag [nzColor]="statusColor(t.status)">{{ statusLabel(t.status) }}</nz-tag></td><td><nz-tag *ngIf="t.priority" [nzColor]="priorityColor(t.priority)">{{ t.priority }}</nz-tag><span *ngIf="!t.priority" class="muted">—</span></td><td class="muted">{{ t.assignee_name || (t.assignee_id ? ('ID: ' + t.assignee_id) : '—') }}</td><td class="muted">{{ t.due_date ? (t.due_date | date:ADMIN_DATE_FORMAT) : '—' }}</td><td nzAlign="right">
						<button nz-button nzType="text" nzSize="small" (click)="openTaskDetail(t)" nz-tooltip="Chi tiết" [attr.aria-label]="'Xem chi tiết công việc ' + t.title" [attr.data-testid]="'detail-task-'+t.id"><span nz-icon nzType="eye"></span></button>
						<button nz-button nzType="text" nzSize="small" (click)="openEditTask(t)" nz-tooltip="Chỉnh sửa" class="action-primary" [attr.aria-label]="'Chỉnh sửa công việc ' + t.title" [attr.data-testid]="'edit-task-'+t.id"><span nz-icon nzType="edit"></span></button>
						<button nz-button nzType="text" nzSize="small" (click)="openAssignTask(t)" nz-tooltip="Phân công" class="action-primary-strong" [attr.aria-label]="'Phân công công việc ' + t.title" [attr.data-testid]="'assign-task-'+t.id"><span nz-icon nzType="swap"></span></button>
						<button *ngIf="t.status === 'pending'" nz-button nzType="text" nzSize="small" (click)="action(t,'start')" nz-tooltip="Bắt đầu" class="action-primary" [attr.aria-label]="'Bắt đầu công việc ' + t.title" [attr.data-testid]="'start-task-'+t.id"><span nz-icon nzType="play-circle"></span></button>
						<button *ngIf="t.status === 'in_progress'" nz-button nzType="text" nzSize="small" (click)="action(t,'complete')" nz-tooltip="Hoàn thành" class="action-success" [attr.aria-label]="'Hoàn thành công việc ' + t.title" [attr.data-testid]="'complete-task-'+t.id"><span nz-icon nzType="check-circle"></span></button>
						<button *ngIf="t.status === 'pending' || t.status === 'in_progress'" nz-button nzDanger nzType="text" nzSize="small" (click)="action(t,'cancel')" nz-tooltip="Hủy" [attr.aria-label]="'Hủy công việc ' + t.title" [attr.data-testid]="'cancel-task-'+t.id"><span nz-icon nzType="close-circle"></span></button>
						<button *ngIf="canDeleteTask()" nz-button nzDanger nzType="text" nzSize="small" (click)="confirmDeleteTask(t)" nz-tooltip="Xóa" [attr.aria-label]="'Xóa công việc ' + t.title" [attr.data-testid]="'delete-task-'+t.id"><span nz-icon nzType="delete"></span></button>
					</td></tr></tbody>
				</nz-table>
			</nz-card>

			<nz-modal [(nzVisible)]="showFormModal" [nzTitle]="formMode === 'create' ? 'Tạo công việc' : 'Chỉnh sửa công việc'" (nzOnOk)="submitTaskForm()" (nzOnCancel)="closeTaskForm()" [nzOkLoading]="saving()" [nzOkText]="formMode === 'create' ? 'Tạo' : 'Lưu'" data-testid="task-form-modal"><ng-container *nzModalContent><div class="form-grid">
				<label class="form-field"><span>Mã công việc *</span><input nz-input [(ngModel)]="taskForm.task_code" data-testid="task-form-code" [disabled]="formMode === 'edit'" /></label>
				<label class="form-field"><span>Tiêu đề *</span><input nz-input [(ngModel)]="taskForm.title" data-testid="task-form-title" /></label>
				<label class="form-field field-span-2"><span>Mô tả</span><textarea nz-input rows="3" [(ngModel)]="taskForm.description" data-testid="task-form-description"></textarea></label>
				<label class="form-field"><span>Ưu tiên</span><nz-select [(ngModel)]="taskForm.priority" nzAllowClear nzPlaceHolder="Chọn ưu tiên" data-testid="task-form-priority"><nz-option *ngFor="let priority of priorityOptions" [nzValue]="priority" [nzLabel]="priority"></nz-option></nz-select></label>
				<label class="form-field"><span>Người thực hiện</span><nz-select [(ngModel)]="taskForm.assignee_id" nzAllowClear nzShowSearch nzPlaceHolder="Chọn người thực hiện" [nzLoading]="usersLoading()" [nzNotFoundContent]="usersLoading() ? 'Đang tải người dùng...' : 'Không có người dùng phù hợp'" data-testid="task-form-assignee"><nz-option *ngFor="let user of assigneeOptions()" [nzValue]="user.value" [nzLabel]="user.label"></nz-option></nz-select></label>
				<label class="form-field"><span>Phòng ban</span><nz-select [(ngModel)]="taskForm.department_id" nzAllowClear nzShowSearch nzPlaceHolder="Chọn phòng ban" [nzLoading]="departmentsLoading()" [nzNotFoundContent]="departmentsLoading() ? 'Đang tải phòng ban...' : 'Không có phòng ban phù hợp'" data-testid="task-form-department"><nz-option *ngFor="let department of departmentOptions()" [nzValue]="department.value" [nzLabel]="department.label"></nz-option></nz-select></label>
				<label class="form-field"><span>Ngày bắt đầu</span><input nz-input type="date" [(ngModel)]="taskForm.start_date" data-testid="task-form-start-date" /></label>
				<label class="form-field"><span>Hạn chót</span><input nz-input type="date" [(ngModel)]="taskForm.due_date" data-testid="task-form-due-date" /></label>
				<label class="form-field"><span>Giờ ước tính</span><input nz-input type="number" [(ngModel)]="taskForm.estimated_hours" data-testid="task-form-estimated-hours" /></label>
			</div></ng-container></nz-modal>

			<nz-modal [(nzVisible)]="showDetailModal" nzTitle="Chi tiết công việc" (nzOnCancel)="showDetailModal = false" [nzFooter]="null" data-testid="task-detail-modal"><ng-container *nzModalContent><nz-descriptions *ngIf="selectedTask() as task" nzSize="small" [nzColumn]="1" nzBordered><nz-descriptions-item nzTitle="Mã công việc">{{ task.task_code || '—' }}</nz-descriptions-item><nz-descriptions-item nzTitle="Tiêu đề">{{ task.title }}</nz-descriptions-item><nz-descriptions-item nzTitle="Trạng thái">{{ statusLabel(task.status) }}</nz-descriptions-item><nz-descriptions-item nzTitle="Ưu tiên">{{ task.priority || '—' }}</nz-descriptions-item><nz-descriptions-item nzTitle="Người thực hiện">{{ task.assignee_name || (task.assignee_id ? ('ID: ' + task.assignee_id) : '—') }}</nz-descriptions-item><nz-descriptions-item nzTitle="Phòng ban">{{ task.department_id || '—' }}</nz-descriptions-item><nz-descriptions-item nzTitle="Ngày bắt đầu">{{ task.start_date ? (task.start_date | date:ADMIN_DATE_FORMAT) : '—' }}</nz-descriptions-item><nz-descriptions-item nzTitle="Hạn chót">{{ task.due_date ? (task.due_date | date:ADMIN_DATE_FORMAT) : '—' }}</nz-descriptions-item><nz-descriptions-item nzTitle="Giờ ước tính">{{ task.estimated_hours ?? '—' }}</nz-descriptions-item><nz-descriptions-item nzTitle="Mô tả">{{ task.description || '—' }}</nz-descriptions-item></nz-descriptions></ng-container></nz-modal>

			<nz-modal [(nzVisible)]="showAssignModal" nzTitle="Phân công công việc" (nzOnOk)="submitAssignTask()" (nzOnCancel)="closeAssignModal()" [nzOkLoading]="saving()" nzOkText="Lưu" data-testid="task-assign-modal"><ng-container *nzModalContent><p class="muted" style="margin-bottom:1rem">Cập nhật assignee cho <strong class="text-strong">{{ selectedTask()?.title }}</strong></p><label class="form-field"><span>Người thực hiện</span><nz-select [(ngModel)]="assignAssigneeId" nzAllowClear nzShowSearch nzPlaceHolder="Chọn người thực hiện" [nzLoading]="usersLoading()" [nzNotFoundContent]="usersLoading() ? 'Đang tải người dùng...' : 'Không có người dùng phù hợp'" data-testid="task-assign-assignee"><nz-option *ngFor="let user of assigneeOptions()" [nzValue]="user.value" [nzLabel]="user.label"></nz-option></nz-select></label></ng-container></nz-modal>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.task-title { font-weight:600; color:var(--admin-text-primary) }
		.task-meta { font-size:.78rem; color:var(--admin-text-muted); margin-top:.1rem }
		.task-desc { font-size:.8rem; color:var(--admin-text-muted); margin-top:.15rem }
		.form-grid { display:grid; gap:.95rem; grid-template-columns:repeat(2, minmax(0, 1fr)) }
		.field-span-2 { grid-column:span 2 }
		.modal-grid-tight { gap: .8rem }
		@media (max-width: 768px) { .form-grid { grid-template-columns:1fr } .field-span-2 { grid-column:span 1 } }
	`]
})
export class TasksPageComponent implements OnInit {
	protected readonly ADMIN_DATE_FORMAT = ADMIN_DATE_FORMAT;
	readonly priorityOptions = PRIORITY_OPTIONS;
	readonly usersLoading = signal(false);
	readonly departmentsLoading = signal(false);
	readonly assigneeOptions = signal<SelectOption[]>([]);
	readonly departmentOptions = signal<SelectOption[]>([]);
	private readonly taskApi = inject(TaskApiService);
	private readonly userApi = inject(UserApiService);
	private readonly rbacApi = inject(RbacApiService);
	private readonly authStore = inject(AuthStoreService);
	private readonly message = inject(NzMessageService);
	private readonly modal = inject(NzModalService);

	readonly all = signal<TaskResponse[]>([]);
	readonly filtered = signal<TaskResponse[]>([]);
	readonly loading = signal(false);
	readonly saving = signal(false);
	readonly selectedTask = signal<TaskResponse | null>(null);
	filters: TaskFilters = {};

	showFormModal = false;
	showDetailModal = false;
	showAssignModal = false;
	formMode: TaskFormMode = 'create';
	taskForm: TaskFormState = { ...EMPTY_TASK_FORM };
	assignAssigneeId: number | null = null;

	ngOnInit(): void {
		this.loadOptions();
		this.load();
	}

	async loadOptions(): Promise<void> {
		await Promise.all([this.loadUsers(), this.loadDepartments()]);
	}

	async load(): Promise<void> {
		await runAdminAsync(this.taskApi.listTasks(), {
			pending: this.loading,
			fallbackMessage: 'Không thể tải danh sách công việc.',
			onSuccess: (data) => { this.all.set(data); this.applyFilters(); },
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	applyFilters(): void { let list = this.all(); if (this.filters.status) list = list.filter(t => t.status === this.filters.status); this.filtered.set(list); }
	resetFilters(): void { this.filters = {}; this.applyFilters(); }
	openCreateTask(): void { if (!this.canCreateTask()) return; this.formMode = 'create'; this.selectedTask.set(null); this.taskForm = { ...EMPTY_TASK_FORM }; this.showFormModal = true; }
	openEditTask(task: TaskResponse): void { this.formMode = 'edit'; this.selectedTask.set(task); this.taskForm = { task_code: task.task_code ?? '', title: task.title, description: task.description ?? '', priority: task.priority ?? '', assignee_id: task.assignee_id, department_id: task.department_id, start_date: task.start_date ?? '', due_date: task.due_date ?? '', estimated_hours: task.estimated_hours ?? null }; this.showFormModal = true; }
	openTaskDetail(task: TaskResponse): void { this.selectedTask.set(task); this.showDetailModal = true; }
	openAssignTask(task: TaskResponse): void { this.selectedTask.set(task); this.assignAssigneeId = task.assignee_id; this.showAssignModal = true; }
	closeTaskForm(): void { this.showFormModal = false; this.saving.set(false); }
	closeAssignModal(): void { this.showAssignModal = false; this.saving.set(false); }

	async submitTaskForm(): Promise<void> {
		if (!this.taskForm.title.trim() || (this.formMode === 'create' && !this.taskForm.task_code.trim())) { this.message.warning(this.formMode === 'create' ? 'Vui lòng nhập mã task và tiêu đề.' : 'Vui lòng nhập tiêu đề task.'); return; }
		if (this.taskForm.estimated_hours != null && this.taskForm.estimated_hours < 0) { this.message.warning('Giờ ước tính không được âm.'); return; }
		if (this.taskForm.start_date && this.taskForm.due_date && this.taskForm.start_date > this.taskForm.due_date) { this.message.warning('Ngày bắt đầu phải sớm hơn hoặc bằng hạn chót.'); return; }
		const fallbackMessage = this.formMode === 'create' ? 'Tạo task thất bại.' : 'Cập nhật task thất bại.';
		const successMessage = this.formMode === 'create' ? 'Đã tạo task.' : 'Đã cập nhật task.';
		const request = this.formMode === 'create'
			? this.taskApi.createTask(this.toCreatePayload())
			: this.taskApi.updateTask(this.selectedTask()!.id, this.toUpdatePayload());
		await runAdminAsync(request, {
			pending: this.saving,
			fallbackMessage,
			onSuccess: (saved) => {
				this.all.update(list => this.formMode === 'create' ? [saved, ...list] : list.map(t => t.id === saved.id ? saved : t));
				this.applyFilters();
				this.showFormModal = false;
				this.message.success(successMessage);
			},
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	async submitAssignTask(): Promise<void> {
		if (this.assignAssigneeId == null) { this.message.warning('Vui lòng chọn người thực hiện.'); return; }
		await runAdminAsync(this.taskApi.assignTask(this.selectedTask()!.id, this.assignAssigneeId), {
			pending: this.saving,
			fallbackMessage: 'Phân công task thất bại.',
			onSuccess: (updated) => {
				this.upsert(updated);
				this.applyFilters();
				this.showAssignModal = false;
				this.message.success('Đã phân công task.');
			},
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	confirmDeleteTask(task: TaskResponse): void { if (!this.canDeleteTask()) return; this.modal.confirm({ nzTitle: `Xóa task "${task.title}"?`, nzOkDanger: true, nzOkText: 'Xóa', nzOnOk: async () => { await runAdminAsync(this.taskApi.deleteTask(task.id), { fallbackMessage: 'Xóa task thất bại.', onSuccess: () => { this.all.update(list => list.filter(t => t.id !== task.id)); this.applyFilters(); this.message.success('Đã xóa task.'); }, onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message) }); } }); }
	action(task: TaskResponse, type: 'start' | 'complete' | 'cancel'): void { const labels = { start: 'Bắt đầu', complete: 'Hoàn thành', cancel: 'Hủy' }; this.modal.confirm({ nzTitle: `${labels[type]} task "${task.title}"?`, nzOkDanger: type === 'cancel', nzOkText: labels[type], nzOnOk: async () => { const request = type === 'start' ? this.taskApi.startTask(task.id) : type === 'complete' ? this.taskApi.completeTask(task.id) : this.taskApi.cancelTask(task.id); await runAdminAsync(request, { fallbackMessage: 'Thao tác thất bại.', onSuccess: (updated) => { this.upsert(updated); this.applyFilters(); this.message.success('Cập nhật thành công.'); }, onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message) }); } }); }
	canCreateTask(): boolean { return this.authStore.hasPermission('create_task'); }
	canDeleteTask(): boolean { return this.canCreateTask(); }
	statusColor(s: TaskStatus): string { return STATUS_COLOR[s] ?? 'default'; }
	statusLabel(s: TaskStatus): string { return STATUS_LABEL[s] ?? s; }
	priorityColor(p: string): string { const m: Record<string, string> = { high: 'red', medium: 'orange', low: 'cyan' }; return m[p.toLowerCase()] ?? 'default'; }

	private async loadUsers(): Promise<void> {
		await runAdminAsync(this.userApi.listUsers({ is_active: true }), {
			pending: this.usersLoading,
			fallbackMessage: 'Không thể tải danh sách người thực hiện.',
			onSuccess: (users) => this.assigneeOptions.set(users.map((user) => this.toUserOption(user))),
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	private async loadDepartments(): Promise<void> {
		await runAdminAsync(this.rbacApi.listDepartments(), {
			pending: this.departmentsLoading,
			fallbackMessage: 'Không thể tải danh sách phòng ban.',
			onSuccess: (departments) => this.departmentOptions.set(departments.map((department) => this.toDepartmentOption(department))),
			onError: (feedback, message) => this.message.error(feedback.action === 'toast-only' ? feedback.message : message)
		});
	}

	private toUserOption(user: UserListItem): SelectOption { return { value: user.id, label: `${user.full_name} · ${user.employee_code}` }; }
	private toDepartmentOption(department: DepartmentResponse): SelectOption { return { value: department.id, label: department.name }; }
	private upsert(task: TaskResponse): void { this.all.update(list => list.map(t => t.id === task.id ? task : t)); }
	private toCreatePayload(): TaskCreateRequest { return { task_code: this.taskForm.task_code.trim(), title: this.taskForm.title.trim(), description: this.taskForm.description.trim() || undefined, priority: this.taskForm.priority || undefined, assignee_id: this.taskForm.assignee_id ?? undefined, department_id: this.taskForm.department_id ?? undefined, start_date: this.taskForm.start_date || undefined, due_date: this.taskForm.due_date || undefined, estimated_hours: this.taskForm.estimated_hours ?? undefined }; }
	private toUpdatePayload(): TaskUpdateRequest { return { title: this.taskForm.title.trim(), description: this.taskForm.description.trim() || undefined, priority: this.taskForm.priority || undefined, assignee_id: this.taskForm.assignee_id, department_id: this.taskForm.department_id, start_date: this.taskForm.start_date || undefined, due_date: this.taskForm.due_date || undefined, estimated_hours: this.taskForm.estimated_hours }; }
}
