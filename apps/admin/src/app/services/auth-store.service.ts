import { computed, Injectable, signal } from '@angular/core';
import { firstValueFrom } from 'rxjs';

import { LoginRequest, LoginResponse, UserResponse } from '../models/auth.models';
import { AuthApiService } from './auth-api.service';

const AUTH_TOKEN_KEY = 'master-operation.admin.token';

@Injectable({
	providedIn: 'root'
})
export class AuthStoreService {
	private readonly tokenState = signal<string | null>(this.readStoredToken());
	private readonly currentUserState = signal<UserResponse | null>(null);
	private readonly initializedState = signal(false);
	private readonly loadingState = signal(false);

	readonly token = computed(() => this.tokenState());
	readonly currentUser = computed(() => this.currentUserState());
	readonly initialized = computed(() => this.initializedState());
	readonly loading = computed(() => this.loadingState());
	readonly isAuthenticated = computed(() => Boolean(this.tokenState() && this.currentUserState()));
	readonly hasSession = computed(() => Boolean(this.tokenState()));

	constructor(private readonly authApi: AuthApiService) {}

	async login(payload: LoginRequest): Promise<UserResponse> {
		this.loadingState.set(true);
		try {
			const response = await firstValueFrom(this.authApi.login(payload));
			this.persistToken(response);
			return await this.loadCurrentUser();
		} finally {
			this.loadingState.set(false);
		}
	}

	async ensureAuthenticated(): Promise<boolean> {
		if (!this.tokenState()) {
			this.initializedState.set(true);
			return false;
		}

		if (!this.currentUserState()) {
			try {
				await this.loadCurrentUser();
			} catch {
				this.clearSession();
				return false;
			}
		}

		this.initializedState.set(true);
		return Boolean(this.currentUserState());
	}

	hasPermission(permission: string): boolean {
		const user = this.currentUserState();
		if (!user) return false;
		if (user.role_name === 'admin') return true;
		return user.permissions.includes(permission);
	}

	logout(): void {
		this.clearSession();
	}

	handleUnauthorized(): void {
		this.clearSession();
	}

	private async loadCurrentUser(): Promise<UserResponse> {
		const user = await firstValueFrom(this.authApi.me());
		this.currentUserState.set(user);
		this.initializedState.set(true);
		return user;
	}

	private persistToken(response: LoginResponse): void {
		this.tokenState.set(response.access_token);
		localStorage.setItem(AUTH_TOKEN_KEY, response.access_token);
	}

	private clearSession(): void {
		this.tokenState.set(null);
		this.currentUserState.set(null);
		this.initializedState.set(true);
		localStorage.removeItem(AUTH_TOKEN_KEY);
	}

	private readStoredToken(): string | null {
		return typeof window !== 'undefined' ? localStorage.getItem(AUTH_TOKEN_KEY) : null;
	}
}
