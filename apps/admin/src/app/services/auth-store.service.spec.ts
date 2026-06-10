import { TestBed } from '@angular/core/testing';
import { of } from 'rxjs';

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

		expect(authApiMock.login).toHaveBeenCalled();
		expect(authApiMock.me).toHaveBeenCalled();
		expect(service.currentUser()).toEqual(currentUser);
		expect(service.hasPermission('system.config.manage')).toBe(true);
		expect(localStorage.getItem('master-operation.admin.token')).toBe('token-123');
	});
});
