import { Component } from '@angular/core';
import { RouterLink } from '@angular/router';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';

@Component({
	selector: 'app-dashboard-page',
	standalone: true,
	imports: [NzCardModule, NzButtonModule, RouterLink],
	template: `
		<section class="grid gap-6 lg:grid-cols-[1.5fr_1fr]" data-testid="dashboard-page">
			<nz-card class="surface-card" [nzBordered]="false">
				<p class="eyebrow">Admin shell ready</p>
				<h3>System configuration workspace</h3>
				<p>
					This shell is prepared for protected admin flows: authentication,
					permission-aware navigation, and menu/i18n sync actions.
				</p>
				<div class="mt-6 flex flex-wrap gap-3">
					<button nz-button nzType="primary" routerLink="/config/menu-sync">Go to menu sync</button>
					<button nz-button nzType="default" routerLink="/config/i18n-sync">Go to i18n sync</button>
				</div>
			</nz-card>

			<nz-card class="surface-card" [nzBordered]="false">
				<p class="eyebrow">MVP scope</p>
				<ul class="space-y-3 text-slate-300">
					<li>Responsive admin shell</li>
					<li>Config sync pages</li>
					<li>Permission-aware routing</li>
					<li>Backend contract verification</li>
				</ul>
			</nz-card>
		</section>
	`,
	styles: [
		`
			:host {
				display: block;
			}

			h3 {
				margin: 0;
				font-size: clamp(1.6rem, 2.8vw, 2.2rem);
				color: #f8fafc;
			}

			p,
			li {
				font-size: 0.96rem;
				line-height: 1.7;
			}

			.eyebrow {
				margin: 0 0 0.8rem;
				font-size: 0.78rem;
				font-weight: 700;
				letter-spacing: 0.16em;
				text-transform: uppercase;
				color: #7dd3fc;
			}

			.surface-card {
				background: rgba(15, 23, 42, 0.78);
				border-radius: 1.4rem;
				box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.03);
			}
		`
	]
})
export class DashboardPageComponent {}
