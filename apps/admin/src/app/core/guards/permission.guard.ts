import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthStoreService } from '../../services/auth-store.service';

export const permissionGuard = (permission: string): CanActivateFn => {
	return async () => {
		const authStore = inject(AuthStoreService);
		const router = inject(Router);
		const isAuthenticated = await authStore.ensureAuthenticated();

		if (!isAuthenticated) {
			return router.createUrlTree(['/unauthorized']);
		}

		return authStore.hasPermission(permission) ? true : router.createUrlTree(['/forbidden']);
	};
};
