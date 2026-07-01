import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal, computed } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzTagModule } from 'ng-zorro-antd/tag';
import { NzBadgeModule } from 'ng-zorro-antd/badge';
import { firstValueFrom } from 'rxjs';

import { AuthStoreService } from '../../services/auth-store.service';
import { UserApiService } from '../../services/user-api.service';
import { TaskApiService } from '../../services/task-api.service';
import { LeaveApiService } from '../../services/leave-api.service';
import { NotificationApiService } from '../../services/notification-api.service';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';

interface DashboardStat {
	label: string;
	value: number | string;
	icon: string;
	color: string;
	route?: string;
	permission?: string;
}

@Component({
	selector: 'app-dashboard-page',
	standalone: true,
	imports: [CommonModule, NzCardModule, NzButtonModule, NzIconModule, NzTagModule, NzBadgeModule, RouterLink],
	template: `
		<section class="dash-root" data-testid="dashboard-page">
			<div class="welcome-banner surface-card content-panel">
				<div class="welcome-text">
					<p class="eyebrow">Admin Control Plane</p>
					<h2>Xin chào, {{ currentUser()?.full_name || 'Admin' }} 👋</h2>
					<p class="subtitle">{{ today }} — {{ currentUser()?.role_name | titlecase }}</p>
				</div>
				<div class="welcome-badge">
					<span nz-icon nzType="dashboard" class="welcome-icon"></span>
				</div>
			</div>

			<div class="section-heading">
				<p class="eyebrow">Live metrics</p>
				<div>
					<h3>Tổng quan vận hành</h3>
					<p class="subtitle">Các chỉ số chính và lối tắt được trình bày theo cùng nhịp bề mặt với shell.</p>
				</div>
			</div>

			<div class="stat-grid">
				<div class="stat-card surface-card" *ngFor="let s of visibleStats()">
					<div class="stat-icon" [style.background]="s.color + '18'">
						<span nz-icon [nzType]="s.icon" [style.color]="s.color"></span>
					</div>
					<div class="stat-body">
						<div class="stat-val">{{ loading() ? '—' : s.value }}</div>
						<div class="stat-lbl">{{ s.label }}</div>
					</div>
				</div>
			</div>

			<div class="section-heading compact-heading">
				<p class="eyebrow">Shortcuts</p>
				<div>
					<h3>Truy cập nhanh</h3>
					<p class="subtitle">Các điểm vào thường dùng giữ cùng hierarchy với màn hình dữ liệu.</p>
				</div>
			</div>
			<div class="quick-grid">
				<a class="quick-card surface-card" routerLink="/users" *ngIf="authStore.hasPermission('manage_org')">
					<span nz-icon nzType="team" class="qc-icon blue"></span>
					<span class="qc-label">Quản lý người dùng</span>
					<span class="qc-sub">{{ stats().totalUsers }} nhân viên</span>
				</a>
				<a class="quick-card surface-card" routerLink="/tasks" *ngIf="authStore.hasPermission('create_task')">
					<span nz-icon nzType="check-square" class="qc-icon green"></span>
					<span class="qc-label">Công việc</span>
					<span class="qc-sub">{{ stats().tasksInProgress }} đang thực hiện</span>
				</a>
				<a class="quick-card surface-card" routerLink="/leaves" *ngIf="authStore.hasPermission('approve_leave')">
					<span nz-icon nzType="calendar" class="qc-icon orange"></span>
					<span class="qc-label">Đơn nghỉ phép</span>
					<span class="qc-sub">{{ stats().leavesPending }} chờ duyệt</span>
				</a>
				<a class="quick-card surface-card" routerLink="/notifications">
					<span nz-icon nzType="bell" class="qc-icon purple"></span>
					<span class="qc-label">Thông báo</span>
					<span class="qc-sub">{{ stats().unreadNotifs }} chưa đọc</span>
				</a>
				<a class="quick-card surface-card" routerLink="/attendance" *ngIf="authStore.hasPermission('view_attendance_self')">
					<span nz-icon nzType="schedule" class="qc-icon cyan"></span>
					<span class="qc-label">Chấm công</span>
					<span class="qc-sub">Xem lịch sử chấm công</span>
				</a>
				<a class="quick-card surface-card" routerLink="/audit-logs" *ngIf="authStore.hasPermission('audit:view')">
					<span nz-icon nzType="file-search" class="qc-icon red"></span>
					<span class="qc-label">Audit Logs</span>
					<span class="qc-sub">Lịch sử hoạt động hệ thống</span>
				</a>
				<a class="quick-card surface-card" routerLink="/rbac/roles" *ngIf="authStore.hasPermission('manage_org')">
					<span nz-icon nzType="safety-certificate" class="qc-icon indigo"></span>
					<span class="qc-label">Phân quyền (RBAC)</span>
					<span class="qc-sub">Roles & Permissions</span>
				</a>
				<a class="quick-card surface-card" routerLink="/agentic/conversations">
					<span nz-icon nzType="message" class="qc-icon teal"></span>
					<span class="qc-label">AI Assistant</span>
					<span class="qc-sub">Trợ lý thông minh tích hợp</span>
				</a>
			</div>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.dash-root {
			display: grid;
			gap: 1.5rem;
			color: var(--admin-text-primary);
		}

		.welcome-banner {
			display: flex;
			align-items: center;
			justify-content: space-between;
			gap: 1.5rem;
			background:
				radial-gradient(circle at 10% 0%, rgba(129, 140, 248, 0.16), transparent 32%),
				linear-gradient(180deg, rgba(9, 16, 30, 0.82) 0%, rgba(7, 12, 24, 0.78) 100%);
			border-color: rgba(129, 140, 248, 0.14);
		}
		.welcome-text {
			display: grid;
			gap: 0.2rem;
		}
		.welcome-text h2 {
			margin: 0;
			font-size: clamp(1.45rem, 2.6vw, 2rem);
			font-weight: 780;
			letter-spacing: -0.04em;
			color: var(--admin-text-primary);
		}
		.welcome-badge {
			flex-shrink: 0;
			display: grid;
			place-items: center;
			width: 4rem;
			height: 4rem;
			border-radius: 1.25rem;
			background: rgba(10, 15, 24, 0.72);
			border: 1px solid rgba(129, 140, 248, 0.16);
			box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
		}
		.welcome-icon {
			font-size: 2rem;
			color: var(--admin-action-primary-strong);
			filter: drop-shadow(0 8px 16px rgba(129, 140, 248, 0.18));
		}

		.stat-grid {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
			gap: 1rem;
		}
		.stat-card {
			display: flex;
			align-items: center;
			gap: 1rem;
			padding: 1.1rem 1.2rem;
			border-color: var(--admin-border-subtle);
			box-shadow:
				0 1px 0 rgba(255, 255, 255, 0.02),
				0 16px 32px rgba(2, 6, 23, 0.16);
			transition:
				transform 0.2s ease,
				border-color 0.2s ease,
				box-shadow 0.2s ease,
				background 0.2s ease;
		}
		.stat-card:hover {
			border-color: rgba(167, 139, 250, 0.28);
			background: linear-gradient(180deg, rgba(14, 20, 32, 0.9) 0%, rgba(10, 15, 24, 0.82) 100%);
			box-shadow:
				0 0 0 1px rgba(129, 140, 248, 0.08),
				0 18px 44px rgba(2, 6, 23, 0.26),
				0 0 28px rgba(129, 140, 248, 0.08);
			transform: translateY(-1px);
		}
		.stat-icon {
			width: 2.75rem;
			height: 2.75rem;
			border-radius: 0.9rem;
			display: grid;
			place-items: center;
			font-size: 1.35rem;
			flex-shrink: 0;
			border: 1px solid rgba(255, 255, 255, 0.06);
			backdrop-filter: blur(12px);
		}
		.stat-val {
			font-size: 1.65rem;
			font-weight: 800;
			letter-spacing: -0.04em;
			color: var(--admin-text-primary);
			line-height: 1;
		}
		.stat-lbl {
			font-size: 0.8rem;
			color: var(--admin-text-muted);
			margin-top: 0.25rem;
		}

		.section-heading {
			display: grid;
			gap: 0.45rem;
		}
		.section-heading h3 {
			margin: 0;
			font-size: 1.03rem;
			font-weight: 700;
			color: var(--admin-text-primary);
		}
		.compact-heading {
			margin-top: 0.1rem;
		}

		.quick-grid {
			display: grid;
			grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
			gap: 1rem;
		}
		.quick-card {
			display: flex;
			flex-direction: column;
			gap: 0.4rem;
			padding: 1.2rem 1.35rem;
			text-decoration: none;
			cursor: pointer;
			transition:
				transform 0.2s ease,
				border-color 0.2s ease,
				box-shadow 0.2s ease,
				background 0.2s ease;
		}
		.quick-card:hover {
			border-color: rgba(167, 139, 250, 0.34);
			background: linear-gradient(180deg, rgba(14, 20, 32, 0.94) 0%, rgba(10, 15, 24, 0.84) 100%);
			box-shadow:
				0 0 0 1px rgba(129, 140, 248, 0.1),
				0 18px 40px rgba(2, 6, 23, 0.28),
				0 0 30px rgba(129, 140, 248, 0.1);
			transform: translateY(-2px);
		}
		.qc-icon {
			font-size: 1.5rem;
			margin-bottom: 0.3rem;
		}
		.qc-label {
			font-size: 0.94rem;
			font-weight: 700;
			color: var(--admin-text-primary);
		}
		.qc-sub {
			font-size: 0.8rem;
			color: var(--admin-text-muted);
		}

		.blue { color: #818cf8; }
		.green { color: #6366f1; }
		.orange { color: #8b5cf6; }
		.purple { color: #a78bfa; }
		.cyan { color: #818cf8; }
		.red { color: #8b5cf6; }
		.indigo { color: #818cf8; }
		.teal { color: #6366f1; }
	`]
})
export class DashboardPageComponent implements OnInit {
	protected readonly authStore = inject(AuthStoreService);
	private readonly userApi = inject(UserApiService);
	private readonly taskApi = inject(TaskApiService);
	private readonly leaveApi = inject(LeaveApiService);
	private readonly notifApi = inject(NotificationApiService);

	readonly loading = signal(true);
	readonly currentUser = this.authStore.currentUser;

	readonly stats = signal({ totalUsers: 0, activeUsers: 0, tasksInProgress: 0, tasksPending: 0, leavesPending: 0, unreadNotifs: 0 });

	readonly today = new Date().toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });

	readonly visibleStats = computed(() => {
		const currentStats = this.stats();
		const all: DashboardStat[] = [
			{ label: 'Nhân viên đang hoạt động', value: currentStats.activeUsers, icon: 'team', color: '#60a5fa', permission: 'manage_org' },
			{ label: 'Tasks đang thực hiện', value: currentStats.tasksInProgress, icon: 'check-square', color: '#34d399', permission: 'create_task' },
			{ label: 'Tasks chờ xử lý', value: currentStats.tasksPending, icon: 'reload', color: '#fb923c', permission: 'create_task' },
			{ label: 'Đơn nghỉ chờ duyệt', value: currentStats.leavesPending, icon: 'calendar', color: '#a78bfa', permission: 'approve_leave' },
			{ label: 'Thông báo chưa đọc', value: currentStats.unreadNotifs, icon: 'bell', color: '#22d3ee' },
			{ label: 'Tổng nhân viên', value: currentStats.totalUsers, icon: 'database', color: '#818cf8', permission: 'manage_org' },
		];
		return all.filter(s => !s.permission || this.authStore.hasPermission(s.permission));
	});

	async ngOnInit(): Promise<void> {
		this.loading.set(true);
		try {
			const [users, tasks, leaves, notifs] = await Promise.allSettled([
				firstValueFrom(this.userApi.listUsers()),
				firstValueFrom(this.taskApi.listTasks()),
				firstValueFrom(this.leaveApi.listLeaves()),
				firstValueFrom(this.notifApi.listNotifications()),
			]);

			const u = users.status === 'fulfilled' ? users.value : [];
			const t = tasks.status === 'fulfilled' ? tasks.value : [];
			const l = leaves.status === 'fulfilled' ? leaves.value : [];
			const n = notifs.status === 'fulfilled' ? notifs.value : [];

			this.stats.set({
				totalUsers: u.length,
				activeUsers: u.filter(x => x.is_active).length,
				tasksInProgress: t.filter(x => x.status === 'in_progress').length,
				tasksPending: t.filter(x => x.status === 'pending').length,
				leavesPending: l.filter(x => x.status === 'pending').length,
				unreadNotifs: n.filter(x => !x.is_read).length,
			});
		} finally {
			this.loading.set(false);
		}
	}
}


