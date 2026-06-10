import { CommonModule } from '@angular/common';
import { Component, inject, signal } from '@angular/core';
import { FormBuilder, ReactiveFormsModule, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { NzAlertModule } from 'ng-zorro-antd/alert';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzFormModule } from 'ng-zorro-antd/form';
import { NzInputModule } from 'ng-zorro-antd/input';

import { AuthStoreService } from '../../services/auth-store.service';

@Component({
	selector: 'app-login-page',
	standalone: true,
	imports: [CommonModule, ReactiveFormsModule, NzAlertModule, NzButtonModule, NzCardModule, NzFormModule, NzInputModule],
	template: `
		<section class="login-shell">
			<nz-card class="login-card" [nzBordered]="false">
				<p class="eyebrow">System access</p>
				<h1>Sign in to the admin workspace</h1>
				<p class="summary">
					Use an account with <code>system.config.manage</code> to access sync routes.
				</p>

				<nz-alert
					*ngIf="errorMessage()"
					nzType="error"
					[nzMessage]="errorMessage()"
					class="mb-4"
				></nz-alert>

				<form [formGroup]="form" (ngSubmit)="submit()" class="grid gap-4">
					<label nz-form-item class="grid gap-2">
						<span>Email</span>
						<input nz-input type="email" formControlName="email" placeholder="admin@company.vn" />
					</label>

					<label nz-form-item class="grid gap-2">
						<span>Password</span>
						<input nz-input type="password" formControlName="password" placeholder="Admin@123" />
					</label>

					<button nz-button nzType="primary" [nzLoading]="authStore.loading()" [disabled]="form.invalid">
						Sign in
					</button>
				</form>
			</nz-card>
		</section>
	`,
	styles: [
		`
			:host {
				display: block;
				min-height: 100dvh;
				background:
					radial-gradient(circle at top left, rgba(59, 130, 246, 0.22), transparent 30%),
					radial-gradient(circle at bottom right, rgba(14, 165, 233, 0.18), transparent 26%),
					#020817;
			}

			.login-shell {
				min-height: 100dvh;
				display: grid;
				place-items: center;
				padding: 1.5rem;
			}

			.login-card {
				width: min(100%, 28rem);
				border-radius: 1.5rem;
				background: rgba(15, 23, 42, 0.84);
			}

			h1 {
				margin: 0;
				font-size: clamp(1.8rem, 4vw, 2.5rem);
				color: #f8fafc;
			}

			.summary,
			span,
			code {
				color: rgba(226, 232, 240, 0.8);
			}

			.summary {
				margin: 0.8rem 0 1.5rem;
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
		`
	]
})
export class LoginPageComponent {
	private readonly formBuilder = inject(FormBuilder);

	readonly errorMessage = signal<string | null>(null);
	readonly form = this.formBuilder.nonNullable.group({
		email: ['admin@company.vn', [Validators.required, Validators.email]],
		password: ['Admin@123', [Validators.required]]
	});

	constructor(
		protected readonly authStore: AuthStoreService,
		private readonly router: Router
	) {}

	async submit(): Promise<void> {
		if (this.form.invalid) {
			return;
		}

		this.errorMessage.set(null);

		try {
			await this.authStore.login(this.form.getRawValue());
			await this.router.navigateByUrl('/');
		} catch {
			this.errorMessage.set('Invalid credentials or session bootstrap failed.');
		}
	}
}
