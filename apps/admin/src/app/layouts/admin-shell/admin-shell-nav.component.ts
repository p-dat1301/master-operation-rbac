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
		<div class="sider-brand">
			<div class="brand-mark">MO</div>
			<div *ngIf="!collapsed" class="brand-copy">
				<p class="brand-eyebrow">RBAC Console</p>
				<h1>Master Operation</h1>
			</div>
		</div>

		<div class="nav-section" *ngFor="let section of navSections">
			<p *ngIf="section.label && !collapsed" class="nav-section-label">{{ section.label }}</p>
			<ul nz-menu nzTheme="dark" nzMode="inline" [nzInlineCollapsed]="collapsed" class="shell-menu">
				<li *ngFor="let item of section.items" nz-menu-item [routerLink]="item.route" routerLinkActive="ant-menu-item-selected" [routerLinkActiveOptions]="{ exact: item.route === '/' }">
					<span nz-icon [nzType]="item.icon"></span>
					<span>{{ item.label }}</span>
				</li>
			</ul>
		</div>

		<div class="sider-footer" *ngIf="!collapsed">
			<p>Angular 21 + NG ZORRO</p>
			<span>System config workspace</span>
		</div>
	`,
	styles: ['.sider-brand { display:flex; align-items:center; gap:.9rem; padding:1.5rem 1.25rem 1rem } .brand-mark { display:grid; place-items:center; width:2.75rem; height:2.75rem; border-radius:1rem; font-size:.9rem; font-weight:800; letter-spacing:.12em; color:#eff6ff; background:linear-gradient(135deg,#0ea5e9,#2563eb); box-shadow:0 14px 38px rgba(37,99,235,.35) } .brand-eyebrow, .sider-footer p, .sider-footer span, .nav-section-label { margin:0 } .brand-copy h1 { margin:0; font-size:1rem; font-weight:700; color:#f8fafc } .brand-eyebrow { font-size:.76rem; letter-spacing:.18em; text-transform:uppercase; color:rgba(125,211,252,.72) } .nav-section { display:grid; gap:.15rem } .nav-section-label { padding:.7rem 1.5rem .15rem; font-size:.68rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; color:rgba(125,211,252,.6) } .shell-menu { background:transparent; border-inline-end:0; padding:.2rem .75rem .55rem } .sider-footer { margin:auto 1rem 1rem; padding:1rem; border:1px solid rgba(125,211,252,.12); border-radius:1rem; background:rgba(15,23,42,.55) } .sider-footer p { font-size:.95rem; font-weight:600; color:#f8fafc } .sider-footer span { display:block; margin-top:.3rem; font-size:.85rem; line-height:1.5; color:rgba(226,232,240,.72) }']
})
export class AdminShellNavComponent {
	@Input({ required: true }) navItems: ShellNavItem[] = [];
	@Input({ required: true }) collapsed = false;

	get navSections(): Array<{ label: string | null; items: ShellNavItem[] }> {
		const sections: Array<{ label: string | null; items: ShellNavItem[] }> = [];
		for (const item of this.navItems) {
			const label = item.group ?? null;
			let section = sections.find((candidate) => candidate.label === label);
			if (!section) {
				section = { label, items: [] };
				sections.push(section);
			}
			section.items.push(item);
		}
		return sections;
	}
}
