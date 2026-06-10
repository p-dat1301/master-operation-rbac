import { inject } from '@angular/core';
import { CanActivateFn, Router } from '@angular/router';

import { AuthStoreService } from '../../services/auth-store.service';

export const authGuard: CanActivateFn = async () => {
	const authStore = inject(AuthStoreService);
	const router = inject(Router);
	const isAllowed = await authStore.ensureAuthenticated();

	return isAllowed ? true : router.createUrlTree(['/unauthorized']);
};
