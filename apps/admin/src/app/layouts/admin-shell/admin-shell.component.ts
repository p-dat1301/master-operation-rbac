import { CommonModule } from '@angular/common';
import { Component, HostListener, OnInit, inject } from '@angular/core';
import { NavigationEnd, Router, RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { filter } from 'rxjs';
import { NzBreadCrumbModule } from 'ng-zorro-antd/breadcrumb';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzLayoutModule } from 'ng-zorro-antd/layout';
import { NzMenuModule } from 'ng-zorro-antd/menu';

import { AuthStoreService } from '../../services/auth-store.service';

type ShellNavItem = {
	label: string;
	icon: string;
	route: string;
	permission?: string;
};

@Component({
	selector: 'app-admin-shell',
	standalone: true,
	imports: [
		CommonModule,
		RouterOutlet,
		RouterLink,
		RouterLinkActive,
		NzLayoutModule,
		NzMenuModule,
		NzIconModule,
		NzBreadCrumbModule,
		NzButtonModule
	],
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
				<div class="sider-brand">
					<div class="brand-mark">MO</div>
					<div *ngIf="!siderCollapsed" class="brand-copy">
						<p class="brand-eyebrow">RBAC Console</p>
						<h1>Master Operation</h1>
					</div>
				</div>

				<ul nz-menu nzTheme="dark" nzMode="inline" [nzInlineCollapsed]="siderCollapsed" class="shell-menu">
					<li *ngFor="let item of navItems" nz-menu-item [routerLink]="item.route" routerLinkActive="ant-menu-item-selected" [routerLinkActiveOptions]="{ exact: item.route === '/' }">
						<span nz-icon [nzType]="item.icon"></span>
						<span>{{ item.label }}</span>
					</li>
				</ul>

				<div class="sider-footer" *ngIf="!siderCollapsed">
					<p>Angular 21 + NG ZORRO</p>
					<span>System config workspace</span>
				</div>
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
			}

			.shell-sider {
				position: sticky;
				top: 0;
				height: 100dvh;
				background: rgba(6, 11, 22, 0.92);
				backdrop-filter: blur(18px);
				border-inline-end: 1px solid rgba(148, 163, 184, 0.12);
			}

			.sider-brand {
				display: flex;
				align-items: center;
				gap: 0.9rem;
				padding: 1.5rem 1.25rem 1rem;
			}

			.brand-mark {
				display: grid;
				place-items: center;
				width: 2.75rem;
				height: 2.75rem;
				border-radius: 1rem;
				font-size: 0.9rem;
				font-weight: 800;
				letter-spacing: 0.12em;
				color: #eff6ff;
				background: linear-gradient(135deg, #0ea5e9, #2563eb);
				box-shadow: 0 14px 38px rgba(37, 99, 235, 0.35);
			}

			.brand-eyebrow,
			.sider-footer p,
			.sider-footer span,
			.header-kicker {
				margin: 0;
			}

			.brand-copy h1,
			.header-left h2 {
				margin: 0;
			}

			.brand-eyebrow,
			.header-kicker {
				font-size: 0.76rem;
				letter-spacing: 0.18em;
				text-transform: uppercase;
				color: rgba(125, 211, 252, 0.72);
			}

			.brand-copy h1 {
				font-size: 1rem;
				font-weight: 700;
				color: #f8fafc;
			}

			.shell-menu {
				background: transparent;
				border-inline-end: 0;
				padding: 0.75rem;
			}

			.sider-footer {
				margin: auto 1rem 1rem;
				padding: 1rem;
				border: 1px solid rgba(125, 211, 252, 0.12);
				border-radius: 1rem;
				background: rgba(15, 23, 42, 0.55);
			}

			.sider-footer p {
				font-size: 0.95rem;
				font-weight: 600;
				color: #f8fafc;
			}

			.sider-footer span {
				display: block;
				margin-top: 0.3rem;
				font-size: 0.85rem;
				line-height: 1.5;
				color: rgba(226, 232, 240, 0.72);
			}

			.shell-header {
				height: auto;
				padding: 1.25rem 1.5rem;
				line-height: normal;
				background: rgba(2, 6, 23, 0.35);
				backdrop-filter: blur(16px);
				border-bottom: 1px solid rgba(148, 163, 184, 0.12);
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

			.header-left h2 {
				font-size: clamp(1.2rem, 2vw, 1.6rem);
				font-weight: 700;
				color: #f8fafc;
			}

			.header-actions {
				display: flex;
				align-items: center;
				gap: 0.75rem;
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
				border: 1px solid rgba(148, 163, 184, 0.12);
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
		{ label: 'Dashboard', icon: 'dashboard', route: '/' },
		{ label: 'Menu sync', icon: 'appstore', route: '/config/menu-sync', permission: 'system.config.manage' },
		{ label: 'i18n sync', icon: 'translation', route: '/config/i18n-sync', permission: 'system.config.manage' }
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
		const matched = this.routeMeta.find((item) => item.route === cleanUrl) ?? this.routeMeta.at(0)!;
		this.breadcrumbs = matched.breadcrumbs;
		this.pageTitle = matched.title;
	}

	private readonly routeMeta = [
		{ route: '/', title: 'Dashboard', breadcrumbs: ['Admin', 'Dashboard'] },
		{ route: '/config/menu-sync', title: 'Menu sync', breadcrumbs: ['Admin', 'Configuration', 'Menu sync'] },
		{ route: '/config/i18n-sync', title: 'i18n sync', breadcrumbs: ['Admin', 'Configuration', 'i18n sync'] },
		{ route: '/unauthorized', title: 'Unauthorized', breadcrumbs: ['Admin', 'Unauthorized'] },
		{ route: '/forbidden', title: 'Forbidden', breadcrumbs: ['Admin', 'Forbidden'] },
		{ route: '/not-found', title: 'Not found', breadcrumbs: ['Admin', 'Not found'] }
	];
}
