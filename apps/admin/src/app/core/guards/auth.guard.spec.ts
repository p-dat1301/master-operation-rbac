import { TestBed } from '@angular/core/testing';
import { Router } from '@angular/router';

import { AuthStoreService } from '../../services/auth-store.service';
import { authGuard } from './auth.guard';
import { permissionGuard } from './permission.guard';

describe('auth guards', () => {
	const authStoreMock = {
		ensureAuthenticated: vi.fn(),
		hasPermission: vi.fn()
	};

	const routerMock = {
		createUrlTree: vi.fn((commands: string[]) => commands.join('/'))
	};

	beforeEach(() => {
		authStoreMock.ensureAuthenticated.mockReset();
		authStoreMock.hasPermission.mockReset();
		routerMock.createUrlTree.mockClear();

		TestBed.configureTestingModule({
			providers: [
				{ provide: AuthStoreService, useValue: authStoreMock },
				{ provide: Router, useValue: routerMock }
			]
		});
	});

	it('redirects unauthenticated users to unauthorized', async () => {
		authStoreMock.ensureAuthenticated.mockResolvedValue(false);

		const result = await TestBed.runInInjectionContext(() => authGuard({} as never, {} as never));

		expect(result).toBe('/unauthorized');
		expect(authStoreMock.ensureAuthenticated).toHaveBeenCalledTimes(1);
		expect(routerMock.createUrlTree).toHaveBeenCalledWith(['/unauthorized']);
	});

	it('redirects authenticated users without permission to forbidden', async () => {
		authStoreMock.ensureAuthenticated.mockResolvedValue(true);
		authStoreMock.hasPermission.mockReturnValue(false);

		const result = await TestBed.runInInjectionContext(() => permissionGuard('system.config.manage')({} as never, {} as never));

		expect(result).toBe('/forbidden');
		expect(authStoreMock.hasPermission).toHaveBeenCalledWith('system.config.manage');
	});

	it('allows authenticated users with permission', async () => {
		authStoreMock.ensureAuthenticated.mockResolvedValue(true);
		authStoreMock.hasPermission.mockReturnValue(true);

		const result = await TestBed.runInInjectionContext(() => permissionGuard('system.config.manage')({} as never, {} as never));

		expect(result).toBe(true);
	});
});
