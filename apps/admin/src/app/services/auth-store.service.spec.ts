import { TestBed } from '@angular/core/testing';
import { of, throwError } from 'rxjs';

import { LoginResponse, UserResponse } from '../models/auth.models';
import { AuthApiService } from './auth-api.service';
import { AuthStoreService } from './auth-store.service';

describe('AuthStoreService', () => {
	const loginResponse: LoginResponse = {
		access_token: 'token-123',
		token_type: 'bearer',
		expires_in: 3600
	};

	const currentUser: UserResponse = {
		id: 1,
		employee_code: 'EMP001',
		email: 'admin@company.vn',
		full_name: 'Admin User',
		role_name: 'admin',
		permissions: ['system.config.manage'],
		phone: null,
		job_title: null,
		department_id: null,
		manager_id: null,
		is_active: true
	};

	const authApiMock = {
		login: vi.fn(() => of(loginResponse)),
		me: vi.fn(() => of(currentUser))
	};

	beforeEach(() => {
		localStorage.clear();
		authApiMock.login.mockClear();
		authApiMock.me.mockClear();

		TestBed.configureTestingModule({
			providers: [
				AuthStoreService,
				{ provide: AuthApiService, useValue: authApiMock }
			]
		});
	});

	it('stores token and current user after login', async () => {
		const service = TestBed.inject(AuthStoreService);

		await service.login({ email: 'admin@company.vn', password: 'Admin@123' });

		expect(authApiMock.login).toHaveBeenCalledWith({ email: 'admin@company.vn', password: 'Admin@123' });
		expect(authApiMock.me).toHaveBeenCalledTimes(1);
		expect(service.currentUser()).toEqual(currentUser);
		expect(service.hasPermission('system.config.manage')).toBe(true);
		expect(localStorage.getItem('master-operation.admin.token')).toBe('token-123');
		expect(service.isAuthenticated()).toBe(true);
	});

	it('clears stored session when ensureAuthenticated cannot load current user', async () => {
		localStorage.setItem('master-operation.admin.token', 'token-123');
		authApiMock.me.mockReturnValueOnce(throwError(() => new Error('boom')));

		const service = TestBed.inject(AuthStoreService);

		expect(await service.ensureAuthenticated()).toBe(false);
		expect(service.token()).toBeNull();
		expect(service.currentUser()).toBeNull();
		expect(localStorage.getItem('master-operation.admin.token')).toBeNull();
	});

	it('reads token from storage on initialization', () => {
		localStorage.setItem('master-operation.admin.token', 'persisted-token');

		const service = TestBed.inject(AuthStoreService);

		expect(service.hasSession()).toBe(true);
		expect(service.token()).toBe('persisted-token');
	});
});
