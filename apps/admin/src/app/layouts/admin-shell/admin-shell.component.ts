import { CommonModule } from '@angular/common';
import { Component, HostListener, OnInit, inject } from '@angular/core';
import { NavigationEnd, Router, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { NzBreadCrumbModule } from 'ng-zorro-antd/breadcrumb';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzLayoutModule } from 'ng-zorro-antd/layout';

import { AuthStoreService } from '../../services/auth-store.service';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';
import { AdminShellNavComponent, type ShellNavItem } from './admin-shell-nav.component';

type ShellRouteMeta = {
	route: string;
	title: string;
	breadcrumbs: string[];
};

@Component({
	selector: 'app-admin-shell',
	standalone: true,
	imports: [CommonModule, RouterOutlet, NzLayoutModule, NzButtonModule, NzIconModule, NzBreadCrumbModule, AdminShellNavComponent],
	template: `
		<nz-layout class="shell-layout">
			<nz-sider
				data-testid="admin-sider"
				class="shell-sider"
				[nzCollapsible]="true"
				[nzCollapsed]="siderCollapsed"
				[nzCollapsedWidth]="isMobile ? 0 : 88"
				[nzWidth]="272"
				[nzTrigger]="null"
			>
				<app-admin-shell-nav [navItems]="navItems" [collapsed]="siderCollapsed"></app-admin-shell-nav>
			</nz-sider>

			<nz-layout>
				<nz-header data-testid="admin-header" class="shell-header">
				<div class="header-left">
					<button nz-button nzType="default" nzShape="circle" (click)="toggleSider()" aria-label="Toggle navigation">
						<span nz-icon [nzType]="siderCollapsed ? 'menu-unfold' : 'menu-fold'"></span>
					</button>
					<div>
						<p class="eyebrow header-kicker">Admin control plane</p>
						<h2>{{ pageTitle }}</h2>
					</div>
				</div>


					<div class="header-actions">
						<div class="identity-chip" *ngIf="authStore.currentUser() as user">
							<strong>{{ user.full_name }}</strong>
							<span>{{ user.role_name }}</span>
						</div>
						<button nz-button nzType="default" (click)="logout()">Sign out</button>
						<span class="status-pill">Local workspace</span>
					</div>
				</nz-header>

				<nz-content class="shell-content">
					<div class="content-frame">
						<nz-breadcrumb>
							<nz-breadcrumb-item *ngFor="let crumb of breadcrumbs">{{ crumb }}</nz-breadcrumb-item>
						</nz-breadcrumb>

						<section class="content-panel">
							<router-outlet></router-outlet>
						</section>
					</div>
				</nz-content>
			</nz-layout>
		</nz-layout>
	`,
	styles: [
		ADMIN_PAGE_COMMON_STYLES,
		`
			:host {
				display: block;
				min-height: 100dvh;
			}

			.shell-layout {
				min-height: 100dvh;
				background:
					radial-gradient(circle at 14% 8%, rgba(129, 140, 248, 0.08), transparent 22%),
					radial-gradient(circle at 86% 0%, rgba(167, 139, 250, 0.05), transparent 18%),
					linear-gradient(180deg, #040916 0%, #020814 100%);
				color: var(--admin-text-primary);
			}

			.shell-sider {
				position: sticky;
				top: 0;
				height: 100dvh;
				background: rgba(6, 11, 22, 0.92);
				backdrop-filter: blur(18px);
				border-inline-end: 1px solid var(--admin-border-subtle);
			}

			.header-kicker {
				margin: 0 0 0.2rem;
				font-size: 0.72rem;
				letter-spacing: 0.2em;
				text-transform: uppercase;
				color: var(--admin-action-primary);
				opacity: 0.88;
			}

			.header-left h2 {
				margin: 0;
				font-size: clamp(1.05rem, 1.65vw, 1.35rem);
				font-weight: 750;
				letter-spacing: -0.03em;
				color: var(--admin-text-primary);
			}

				.shell-header {
					height: auto;
					padding: 1rem 1.35rem;
					line-height: normal;
					background: rgba(2, 6, 23, 0.42);
					backdrop-filter: blur(18px) saturate(120%);
					border-bottom: 1px solid var(--admin-border-subtle);
					display: flex;
					align-items: center;
					justify-content: space-between;
					gap: 1rem;
					flex-wrap: wrap;
				}


			.header-left {
				display: flex;
				align-items: center;
				gap: 0.9rem;
				min-width: 0;
			}

				.header-actions {
					display: flex;
					align-items: center;
					gap: 0.75rem;
					flex-wrap: wrap;
					justify-content: flex-end;
					min-width: 0;
				}


			.identity-chip {
				display: grid;
				gap: 0.08rem;
				padding: 0.55rem 0.9rem;
				border-radius: 0.95rem;
				background: rgba(10, 16, 30, 0.78);
				border: 1px solid rgba(148, 163, 184, 0.12);
				box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
			}

			.identity-chip strong {
				color: var(--admin-text-primary);
				font-size: 0.88rem;
				font-weight: 700;
			}

			.identity-chip span {
				color: var(--admin-text-secondary);
				font-size: 0.76rem;
			}

			.status-pill {
				display: inline-flex;
				align-items: center;
				gap: 0.45rem;
				padding: 0.5rem 0.8rem;
				border-radius: 999px;
				background: rgba(129, 140, 248, 0.12);
				border: 1px solid rgba(129, 140, 248, 0.16);
				color: #c7d2fe;
				font-size: 0.78rem;
				font-weight: 700;
				letter-spacing: 0.01em;
			}

			.shell-content {
				padding: 1.15rem;
			}

			.content-frame {
				display: grid;
				gap: 0.95rem;
			}

			.content-panel {
				min-height: calc(100dvh - 10.75rem);
				box-shadow:
					0 1px 0 rgba(255, 255, 255, 0.02),
					0 18px 50px rgba(2, 6, 23, 0.34),
					inset 0 1px 0 rgba(255, 255, 255, 0.02);
				overflow: hidden;
			}

			@media (max-width: 991px) {
				.shell-header {
					padding: 0.9rem 1rem;
					align-items: stretch;
					flex-direction: column;
				}

				.header-left {
					width: 100%;
				}

				.header-actions {
					justify-content: flex-start;
					width: 100%;
				}

				.identity-chip {
					max-width: 100%;
				}

				.shell-content {
					padding: 0.9rem;
				}

				.content-panel {
					min-height: auto;
					border-radius: 1.15rem;
				}
			}

			@media (max-width: 767px) {
				.header-actions > * {
					flex: 1 1 auto;
				}

				.header-actions .status-pill,
				.header-actions button {
					min-width: max-content;
				}
			}
		`
	]
})
export class AdminShellComponent implements OnInit {
	private readonly router = inject(Router);
	protected readonly authStore = inject(AuthStoreService);

	private readonly allNavItems: ShellNavItem[] = [
		{ label: 'Bảng điều khiển', icon: 'dashboard', route: '/', group: 'Không gian làm việc' },
		{ label: 'Thông báo', icon: 'bell', route: '/notifications', group: 'Không gian làm việc' },
		{ label: 'Trò chuyện AI', icon: 'message', route: '/chat', group: 'Trợ lý AI & Tri thức' },
		{ label: 'Lịch sử chat', icon: 'comment', route: '/agentic/conversations', group: 'Trợ lý AI & Tri thức' },
		{ label: 'Tài liệu & Tri thức', icon: 'file-text', route: '/agentic/documents', group: 'Trợ lý AI & Tri thức' },
		{ label: 'Nhân sự', icon: 'team', route: '/users', permission: 'manage_org', group: 'Tổ chức & Phân quyền' },
		{ label: 'Phòng ban', icon: 'apartment', route: '/system/departments', permission: 'manage_org', group: 'Tổ chức & Phân quyền' },
		{ label: 'Vai trò', icon: 'safety-certificate', route: '/rbac/roles', permission: 'manage_org', group: 'Tổ chức & Phân quyền' },
		{ label: 'Quyền hạn', icon: 'key', route: '/rbac/permissions', permission: 'manage_org', group: 'Tổ chức & Phân quyền' },
		{ label: 'Công việc', icon: 'check-square', route: '/tasks', permission: 'create_task', group: 'Hoạt động & Vận hành' },
		{ label: 'Điểm danh', icon: 'schedule', route: '/attendance', permission: 'view_attendance_self', group: 'Hoạt động & Vận hành' },
		{ label: 'Đơn nghỉ phép', icon: 'calendar', route: '/leaves', permission: 'approve_leave', group: 'Hoạt động & Vận hành' },
		{ label: 'Nhật ký hệ thống', icon: 'history', route: '/audit-logs', permission: 'audit:view', group: 'Quản trị hệ thống' },
		{ label: 'Đồng bộ Menu', icon: 'sync', route: '/config/menu-sync', permission: 'system.config.manage', group: 'Quản trị hệ thống' },
		{ label: 'Đồng bộ i18n', icon: 'global', route: '/config/i18n-sync', permission: 'system.config.manage', group: 'Quản trị hệ thống' }
	];

	private readonly routeMeta: ShellRouteMeta[] = [
		{ route: '/', title: 'Bảng điều khiển', breadcrumbs: ['Hệ thống', 'Không gian làm việc', 'Bảng điều khiển'] },
		{ route: '/agentic/conversations', title: 'Lịch sử chat', breadcrumbs: ['Hệ thống', 'Trợ lý AI & Tri thức', 'Lịch sử chat'] },
		{ route: '/agentic/documents', title: 'Tài liệu & Tri thức', breadcrumbs: ['Hệ thống', 'Trợ lý AI & Tri thức', 'Tài liệu & Tri thức'] },
		{ route: '/users', title: 'Quản lý nhân sự', breadcrumbs: ['Hệ thống', 'Tổ chức & Phân quyền', 'Nhân sự'] },
		{ route: '/system/departments', title: 'Quản lý phòng ban', breadcrumbs: ['Hệ thống', 'Tổ chức & Phân quyền', 'Phòng ban'] },
		{ route: '/rbac/roles', title: 'Quản lý vai trò', breadcrumbs: ['Hệ thống', 'Tổ chức & Phân quyền', 'Vai trò'] },
		{ route: '/rbac/permissions', title: 'Quản lý quyền hạn', breadcrumbs: ['Hệ thống', 'Tổ chức & Phân quyền', 'Quyền hạn'] },
		{ route: '/tasks', title: 'Quản lý công việc', breadcrumbs: ['Hệ thống', 'Hoạt động & Vận hành', 'Công việc'] },
		{ route: '/attendance', title: 'Điểm danh', breadcrumbs: ['Hệ thống', 'Hoạt động & Vận hành', 'Điểm danh'] },
		{ route: '/leaves', title: 'Đơn nghỉ phép', breadcrumbs: ['Hệ thống', 'Hoạt động & Vận hành', 'Đơn nghỉ phép'] },
		{ route: '/notifications', title: 'Thông báo', breadcrumbs: ['Hệ thống', 'Không gian làm việc', 'Thông báo'] },
		{ route: '/chat', title: 'Trò chuyện AI', breadcrumbs: ['Hệ thống', 'Trợ lý AI & Tri thức', 'Trò chuyện AI'] },
		{ route: '/audit-logs', title: 'Nhật ký hệ thống', breadcrumbs: ['Hệ thống', 'Quản trị hệ thống', 'Nhật ký hệ thống'] },
		{ route: '/config/menu-sync', title: 'Đồng bộ Menu', breadcrumbs: ['Hệ thống', 'Quản trị hệ thống', 'Đồng bộ Menu'] },
		{ route: '/config/i18n-sync', title: 'Đồng bộ i18n', breadcrumbs: ['Hệ thống', 'Quản trị hệ thống', 'Đồng bộ i18n'] },
		{ route: '/unauthorized', title: 'Không có quyền truy cập', breadcrumbs: ['Hệ thống', 'Lỗi truy cập'] },
		{ route: '/forbidden', title: 'Bị cấm truy cập', breadcrumbs: ['Hệ thống', 'Lỗi truy cập'] },
		{ route: '/not-found', title: 'Không tìm thấy trang', breadcrumbs: ['Hệ thống', 'Lỗi truy cập'] }
	];

	breadcrumbs: string[] = ['Admin'];
	pageTitle = 'Dashboard';
	isMobile = false;
	siderCollapsed = false;
	navItems: ShellNavItem[] = [];

	ngOnInit(): void {
		this.updateViewportState();
		this.syncRouteMeta(this.router.url);
		this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe((event) => {
			this.syncRouteMeta((event as NavigationEnd).urlAfterRedirects);
			if (this.isMobile) {
				this.siderCollapsed = true;
			}
		});
		this.navItems = this.allNavItems.filter((item) => !item.permission || this.authStore.hasPermission(item.permission));
	}

	@HostListener('window:resize')
	updateViewportState(): void {
		this.isMobile = window.innerWidth < 992;
		if (this.isMobile) {
			this.siderCollapsed = true;
		}
	}

	toggleSider(): void {
		this.siderCollapsed = !this.siderCollapsed;
	}

	logout(): void {
		this.authStore.logout();
		void this.router.navigateByUrl('/login');
	}

	private syncRouteMeta(url: string): void {
		const cleanUrl = url.split('?')[0] || '/';
		const matched = this.routeMeta.find((item) => item.route === cleanUrl) ?? this.routeMeta[0];
		this.breadcrumbs = matched.breadcrumbs;
		this.pageTitle = matched.title;
	}
}
