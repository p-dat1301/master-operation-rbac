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
							<p class="header-kicker">Admin control plane</p>
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
					radial-gradient(circle at top left, rgba(59, 130, 246, 0.2), transparent 26%),
					radial-gradient(circle at 100% 0%, rgba(14, 165, 233, 0.14), transparent 22%),
					#020817;
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
				margin: 0;
				font-size: 0.76rem;
				letter-spacing: 0.18em;
				text-transform: uppercase;
				color: var(--admin-action-primary);
			}

			.header-left h2 {
				margin: 0;
				font-size: clamp(1.2rem, 2vw, 1.6rem);
				font-weight: 700;
				color: var(--admin-text-primary);
			}

			.shell-header {
				height: auto;
				padding: 1.25rem 1.5rem;
				line-height: normal;
				background: rgba(2, 6, 23, 0.35);
				backdrop-filter: blur(16px);
				border-bottom: 1px solid var(--admin-border-subtle);
				display: flex;
				align-items: center;
				justify-content: space-between;
				gap: 1rem;
			}

			.header-left {
				display: flex;
				align-items: center;
				gap: 1rem;
			}

			.header-actions {
				display: flex;
				align-items: center;
				gap: 0.75rem;
			}

			.identity-chip {
				display: grid;
				gap: 0.1rem;
				padding: 0.5rem 0.85rem;
				border-radius: 1rem;
				background: rgba(15, 23, 42, 0.72);
				border: 1px solid var(--admin-border-subtle);
			}

			.identity-chip strong {
				color: var(--admin-text-primary);
				font-size: 0.88rem;
			}

			.identity-chip span {
				color: var(--admin-text-secondary);
				font-size: 0.78rem;
			}

			.status-pill {
				display: inline-flex;
				align-items: center;
				gap: 0.45rem;
				padding: 0.55rem 0.85rem;
				border-radius: 999px;
				background: rgba(14, 165, 233, 0.14);
				color: #bae6fd;
				font-size: 0.82rem;
				font-weight: 700;
			}

			.shell-content {
				padding: 1.5rem;
			}

			.content-frame {
				display: grid;
				gap: 1rem;
			}

			.content-panel {
				min-height: calc(100dvh - 11rem);
				padding: clamp(1rem, 2vw, 1.5rem);
				border: 1px solid var(--admin-border-subtle);
				border-radius: 1.5rem;
				background: rgba(8, 15, 28, 0.72);
				box-shadow: 0 30px 80px rgba(2, 6, 23, 0.4);
			}

			@media (max-width: 991px) {
				.shell-header {
					padding: 1rem;
					align-items: flex-start;
					flex-direction: column;
				}

				.shell-content {
					padding: 1rem;
				}
			}
		`
	]
})
export class AdminShellComponent implements OnInit {
	private readonly router = inject(Router);
	protected readonly authStore = inject(AuthStoreService);

	private readonly allNavItems: ShellNavItem[] = [
		{ label: 'Dashboard', icon: 'dashboard', route: '/', group: 'Workspace' },
		{ label: 'Thông báo', icon: 'bell', route: '/notifications', group: 'Workspace' },
		{ label: 'Chat', icon: 'message', route: '/chat', group: 'Agent/AI' },
		{ label: 'Conversations', icon: 'comment', route: '/agentic/conversations', group: 'Agent/AI' },
		{ label: 'Documents', icon: 'file-text', route: '/agentic/documents', group: 'Agent/AI' },
		{ label: 'Người dùng', icon: 'team', route: '/users', permission: 'manage_org', group: 'Organization' },
		{ label: 'Departments', icon: 'team', route: '/system/departments', permission: 'manage_org', group: 'Organization' },
		{ label: 'Roles', icon: 'safety-certificate', route: '/rbac/roles', permission: 'manage_org', group: 'Access Control' },
		{ label: 'Permissions', icon: 'key', route: '/rbac/permissions', permission: 'manage_org', group: 'Access Control' },
		{ label: 'Công việc', icon: 'check-square', route: '/tasks', permission: 'create_task', group: 'Operations' },
		{ label: 'Attendance', icon: 'schedule', route: '/attendance', permission: 'view_attendance_self', group: 'Operations' },
		{ label: 'Nghỉ phép', icon: 'calendar', route: '/leaves', permission: 'approve_leave', group: 'Operations' },
		{ label: 'Audit Logs', icon: 'file-search', route: '/audit-logs', permission: 'audit:view', group: 'Security' },
		{ label: 'Menu sync', icon: 'appstore', route: '/config/menu-sync', permission: 'system.config.manage', group: 'Advanced/Admin tools' },
		{ label: 'i18n sync', icon: 'translation', route: '/config/i18n-sync', permission: 'system.config.manage', group: 'Advanced/Admin tools' }
	];

	private readonly routeMeta: ShellRouteMeta[] = [
		{ route: '/', title: 'Dashboard', breadcrumbs: ['Admin', 'Workspace', 'Dashboard'] },
		{ route: '/agentic/conversations', title: 'Conversations', breadcrumbs: ['Admin', 'Agent/AI', 'Conversations'] },
		{ route: '/agentic/documents', title: 'Documents', breadcrumbs: ['Admin', 'Agent/AI', 'Documents'] },
		{ route: '/users', title: 'Quản lý người dùng', breadcrumbs: ['Admin', 'Organization', 'Quản lý người dùng'] },
		{ route: '/system/departments', title: 'Departments', breadcrumbs: ['Admin', 'Organization', 'Departments'] },
		{ route: '/rbac/roles', title: 'Roles', breadcrumbs: ['Admin', 'Access Control', 'Roles'] },
		{ route: '/rbac/permissions', title: 'Permissions', breadcrumbs: ['Admin', 'Access Control', 'Permissions'] },
		{ route: '/tasks', title: 'Công việc', breadcrumbs: ['Admin', 'Operations', 'Công việc'] },
		{ route: '/attendance', title: 'Attendance', breadcrumbs: ['Admin', 'Operations', 'Attendance'] },
		{ route: '/leaves', title: 'Đơn nghỉ phép', breadcrumbs: ['Admin', 'Operations', 'Đơn nghỉ phép'] },
		{ route: '/notifications', title: 'Thông báo', breadcrumbs: ['Admin', 'Workspace', 'Thông báo'] },
		{ route: '/chat', title: 'Chat', breadcrumbs: ['Admin', 'Agent/AI', 'Chat'] },
		{ route: '/audit-logs', title: 'Audit Logs', breadcrumbs: ['Admin', 'Security', 'Audit Logs'] },
		{ route: '/config/menu-sync', title: 'Menu sync', breadcrumbs: ['Admin', 'Advanced/Admin tools', 'Menu sync'] },
		{ route: '/config/i18n-sync', title: 'i18n sync', breadcrumbs: ['Admin', 'Advanced/Admin tools', 'i18n sync'] },
		{ route: '/unauthorized', title: 'Unauthorized', breadcrumbs: ['Admin', 'Unauthorized'] },
		{ route: '/forbidden', title: 'Forbidden', breadcrumbs: ['Admin', 'Forbidden'] },
		{ route: '/not-found', title: 'Not found', breadcrumbs: ['Admin', 'Not found'] }
	];

	breadcrumbs: string[] = ['Admin'];
	pageTitle = 'Dashboard';
	isMobile = false;
	siderCollapsed = false;

	ngOnInit(): void {
		this.updateViewportState();
		this.syncRouteMeta(this.router.url);
		this.router.events.pipe(filter((event) => event instanceof NavigationEnd)).subscribe((event) => {
			this.syncRouteMeta((event as NavigationEnd).urlAfterRedirects);
			if (this.isMobile) {
				this.siderCollapsed = true;
			}
		});
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

	get navItems(): ShellNavItem[] {
		return this.allNavItems.filter((item) => !item.permission || this.authStore.hasPermission(item.permission));
	}

	private syncRouteMeta(url: string): void {
		const cleanUrl = url.split('?')[0] || '/';
		const matched = this.routeMeta.find((item) => item.route === cleanUrl) ?? this.routeMeta[0];
		this.breadcrumbs = matched.breadcrumbs;
		this.pageTitle = matched.title;
	}
}
