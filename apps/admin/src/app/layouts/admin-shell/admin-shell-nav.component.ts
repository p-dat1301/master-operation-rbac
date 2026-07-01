import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { RouterLink, RouterLinkActive } from '@angular/router';
import { NzMenuModule } from 'ng-zorro-antd/menu';
import { NzIconModule } from 'ng-zorro-antd/icon';

export type ShellNavItem = {
	label: string;
	icon: string;
	route: string;
	permission?: string;
	group?: string;
};

@Component({
	selector: 'app-admin-shell-nav',
	standalone: true,
	imports: [CommonModule, RouterLink, RouterLinkActive, NzMenuModule, NzIconModule],
	template: `
		<div class="shell-nav" [class.collapsed]="collapsed">
			<div class="sider-brand">
				<div class="brand-mark">MO</div>
				<div *ngIf="!collapsed" class="brand-copy">
					<p class="brand-eyebrow">RBAC Console</p>
					<h1>Master Operation</h1>
				</div>
			</div>

			<div class="nav-scroll">
				<div class="nav-section" *ngFor="let section of navSections">
					<p *ngIf="section.label && !collapsed" class="nav-section-label">{{ section.label }}</p>
					<ul nz-menu nzTheme="dark" nzMode="inline" [nzInlineCollapsed]="collapsed" class="shell-menu">
						<li *ngFor="let item of section.items" nz-menu-item [routerLink]="item.route" routerLinkActive="ant-menu-item-selected" [routerLinkActiveOptions]="{ exact: item.route === '/' }">
							<span nz-icon [nzType]="item.icon"></span>
							<span>{{ item.label }}</span>
						</li>
					</ul>
				</div>
			</div>

			<div class="sider-footer" *ngIf="!collapsed">
				<p>
					<span class="status-dot"></span>
					Hệ thống trực tuyến
				</p>
				<span>Cấu hình & Giám sát vận hành</span>
			</div>
		</div>
	`,
	styles: [
		`
			.shell-nav {
				display: flex;
				flex-direction: column;
				height: 100%;
				min-height: 100%;
				background: var(--shell-nav-surface);
				backdrop-filter: blur(24px);
				box-shadow: inset -1px 0 0 0 rgba(148, 163, 184, 0.08);
				transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
			}

			:host {
				--shell-nav-surface: linear-gradient(180deg, rgba(8, 12, 24, 0.92) 0%, rgba(10, 16, 32, 0.9) 100%);
			}

			.sider-brand {
				display: flex;
				align-items: center;
				gap: 0.875rem;
				padding: 1.5rem 1rem 1.15rem;
				margin: 0 0.5rem 0.4rem;
				border-bottom: 1px solid rgba(148, 163, 184, 0.08);
				transition: all 0.3s ease;
			}

			.shell-nav.collapsed .sider-brand {
				justify-content: center;
				padding: 1.25rem 0.5rem 1rem;
				margin: 0 0.35rem 0.4rem;
			}

			.brand-mark {
				display: grid;
				place-items: center;
				width: 2.5rem;
				height: 2.5rem;
				border-radius: 0.95rem;
				font-size: 0.92rem;
				font-weight: 850;
				letter-spacing: 0.06em;
				color: var(--admin-color-text-inverse, #ffffff);
				background: linear-gradient(135deg, var(--admin-color-primary, #6366f1) 0%, var(--admin-color-primary-strong, #8b5cf6) 100%);
				box-shadow: 0 12px 28px rgba(99, 102, 241, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.14);
				transition: transform 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275), box-shadow 0.35s ease;
				flex-shrink: 0;
			}

			.sider-brand:hover .brand-mark {
				transform: translateY(-1px) scale(1.05);
				box-shadow: 0 16px 34px rgba(99, 102, 241, 0.34), inset 0 1px 0 rgba(255, 255, 255, 0.16);
			}

			.brand-eyebrow,
			.sider-footer p,
			.sider-footer span,
			.nav-section-label {
				margin: 0;
			}

			.brand-copy h1 {
				margin: 0;
				font-size: 1rem;
				font-weight: 760;
				color: var(--admin-color-text, #f8fafc);
				letter-spacing: -0.03em;
			}

			.brand-eyebrow {
				font-size: 0.68rem;
				font-weight: 700;
				letter-spacing: 0.16em;
				text-transform: uppercase;
				color: var(--admin-color-primary-soft, #a78bfa);
				opacity: 0.88;
				margin-bottom: 0.15rem;
			}

				.nav-scroll {
					flex: 1 1 auto;
					min-height: 0;
					overflow-y: auto;
					overflow-x: hidden;
					overscroll-behavior: contain;
					padding: 0 0.45rem 0.45rem;
					scrollbar-width: thin;
					scrollbar-color: rgba(148, 163, 184, 0.14) transparent;
				}


			.nav-scroll::-webkit-scrollbar {
				width: 4px;
			}

			.nav-scroll::-webkit-scrollbar-thumb {
				background: rgba(148, 163, 184, 0.16);
				border-radius: 99px;
			}

			.nav-scroll::-webkit-scrollbar-thumb:hover {
				background: rgba(148, 163, 184, 0.28);
			}

			.nav-section {
				display: grid;
				margin-bottom: 0.25rem;
			}

			.nav-section-label {
				padding: 0.8rem 0.95rem 0.3rem;
				font-size: 0.62rem;
				font-weight: 750;
				letter-spacing: 0.14em;
				text-transform: uppercase;
				color: var(--admin-color-muted, rgba(148, 163, 184, 0.52));
				transition: color 0.3s ease;
			}

			.shell-menu {
				background: transparent !important;
				border-inline-end: 0 !important;
			}

			::ng-deep .shell-menu.ant-menu {
				background: transparent !important;
				border-right: none !important;
			}

			::ng-deep .shell-menu .ant-menu-item {
				height: 2.5rem !important;
				line-height: 2.5rem !important;
				margin: 0.1rem 0 !important;
				padding-left: 0.95rem !important;
				padding-right: 0.95rem !important;
				border-radius: 0.8rem !important;
				color: rgba(226, 232, 240, 0.76) !important;
				background: transparent !important;
				transition: transform 0.22s ease, background 0.22s ease, color 0.22s ease, box-shadow 0.22s ease !important;
				font-weight: 540 !important;
				display: flex !important;
				align-items: center !important;
				position: relative !important;
			}

			::ng-deep .shell-menu .ant-menu-item::before {
				content: '';
				position: absolute;
				inset: 0;
				border-radius: inherit;
				background: linear-gradient(135deg, rgba(99, 102, 241, 0) 0%, rgba(139, 92, 246, 0) 100%);
				opacity: 0;
				transition: opacity 0.22s ease, background 0.22s ease;
				pointer-events: none;
			}

			::ng-deep .shell-menu .ant-menu-item:hover {
				color: var(--admin-color-text, #ffffff) !important;
				background: rgba(255, 255, 255, 0.045) !important;
				transform: translateX(2px);
				box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.08);
			}

			::ng-deep .shell-menu .ant-menu-item:hover::before {
				opacity: 1;
				background: linear-gradient(135deg, rgba(99, 102, 241, 0.08) 0%, rgba(139, 92, 246, 0.08) 100%);
			}

			::ng-deep .shell-menu .ant-menu-item-selected {
				color: var(--admin-color-text, #ffffff) !important;
				background: linear-gradient(135deg, rgba(79, 70, 229, 0.28) 0%, rgba(124, 58, 237, 0.24) 100%) !important;
				box-shadow: inset 0 0 0 1px rgba(167, 139, 250, 0.24), 0 10px 24px rgba(79, 70, 229, 0.16) !important;
				font-weight: 650 !important;
			}

				::ng-deep .shell-menu .ant-menu-item-selected::after {
					border-right: 3px solid var(--admin-color-primary-soft, #a78bfa) !important;
					right: 0.1rem !important;
					left: auto !important;
					height: 56% !important;
					top: 22% !important;
					border-radius: 99px !important;
				}

				.shell-nav.collapsed .nav-scroll {
					padding: 0 0.55rem 0.55rem;
					scrollbar-gutter: stable;
				}

				.shell-nav.collapsed .nav-section {
					place-items: center;
				}

				.shell-nav.collapsed ::ng-deep .shell-menu.ant-menu-inline-collapsed {
					width: 100% !important;
				}

				.shell-nav.collapsed ::ng-deep .shell-menu .ant-menu-item {
					width: 3rem !important;
					height: 3rem !important;
					line-height: 3rem !important;
					margin: 0.18rem auto !important;
					padding: 0 !important;
					justify-content: center !important;
					transform: none;
				}

				.shell-nav.collapsed ::ng-deep .shell-menu .ant-menu-item:hover {
					transform: translateY(-1px);
				}

				.shell-nav.collapsed ::ng-deep .shell-menu .ant-menu-item-selected::after {
					right: 0.05rem !important;
					height: 48% !important;
					top: 26% !important;
				}

				::ng-deep .shell-menu .ant-menu-item .anticon {
					font-size: 1rem !important;
					margin-right: 0.7rem !important;
					transition: transform 0.22s ease, color 0.22s ease !important;
				}

				.shell-nav.collapsed ::ng-deep .shell-menu .ant-menu-item .anticon {
					margin-right: 0 !important;
				}


			::ng-deep .shell-menu .ant-menu-item:hover .anticon {
				transform: scale(1.08);
				color: var(--admin-color-primary-soft, #a78bfa) !important;
			}

			::ng-deep .shell-menu .ant-menu-item-selected .anticon {
				color: var(--admin-color-primary-soft, #a78bfa) !important;
			}

			.sider-footer {
				margin: auto 0.65rem 0.9rem;
				padding: 0.8rem 0.9rem;
				border: 1px solid rgba(148, 163, 184, 0.1);
				border-radius: 0.95rem;
				background: rgba(15, 23, 42, 0.52);
				backdrop-filter: blur(12px);
				box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
			}

			.sider-footer p {
				font-size: 0.8rem;
				font-weight: 650;
				color: var(--admin-color-text, #f8fafc);
				display: flex;
				align-items: center;
				gap: 0.5rem;
			}

			.sider-footer span {
				display: block;
				margin-top: 0.2rem;
				font-size: 0.73rem;
				line-height: 1.35;
				color: rgba(148, 163, 184, 0.84);
			}

			.status-dot {
				width: 6px;
				height: 6px;
				background-color: var(--admin-color-success, #10b981);
				border-radius: 50%;
				display: inline-block;
				box-shadow: 0 0 8px rgba(16, 185, 129, 0.65);
				animation: pulse 2s infinite;
			}

			@keyframes pulse {
				0% {
					transform: scale(0.95);
					box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
				}
				70% {
					transform: scale(1);
					box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
				}
				100% {
					transform: scale(0.95);
					box-shadow: 0 0 0 0 rgba(16, 185, 129, 0);
				}
			}
		`
	]
})
export class AdminShellNavComponent {
	private _navItems: ShellNavItem[] = [];
	navSections: Array<{ label: string | null; items: ShellNavItem[] }> = [];

	@Input({ required: true })
	set navItems(value: ShellNavItem[]) {
		this._navItems = value;
		this.computeNavSections(value);
	}

	get navItems(): ShellNavItem[] {
		return this._navItems;
	}

	@Input({ required: true }) collapsed = false;

	private computeNavSections(items: ShellNavItem[]): void {
		const sections: Array<{ label: string | null; items: ShellNavItem[] }> = [];
		for (const item of items) {
			const label = item.group ?? null;
			let section = sections.find((candidate) => candidate.label === label);
			if (!section) {
				section = { label, items: [] };
				sections.push(section);
			}
			section.items.push(item);
		}
		this.navSections = sections;
	}
}
