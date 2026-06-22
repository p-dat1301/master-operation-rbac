import { HttpErrorResponse, HttpInterceptorFn } from '@angular/common/http';
import { inject } from '@angular/core';
import { Router } from '@angular/router';
import { NzMessageService } from 'ng-zorro-antd/message';
import { catchError, throwError } from 'rxjs';

import { AuthStoreService } from '../../services/auth-store.service';
import { mapAdminHttpError } from '../../shared/http-error-mapper';

const LOGIN_URL = '/api/v1/auth/login';
const UNAUTHORIZED_ROUTE = '/unauthorized';
const FORBIDDEN_ROUTE = '/forbidden';

export const authInterceptor: HttpInterceptorFn = (request, next) => {
	const authStore = inject(AuthStoreService);
	const router = inject(Router);
	const message = inject(NzMessageService);
	const token = authStore.token();
	const authRequest = token
		? request.clone({
			setHeaders: {
				Authorization: `Bearer ${token}`
			}
		})
		: request;

	return next(authRequest).pipe(
		catchError((error: unknown) => {
			const feedback = mapAdminHttpError(error);

			if (error instanceof HttpErrorResponse && !request.url.includes(LOGIN_URL)) {
				if (feedback.action === 'redirect-unauthorized') {
					authStore.handleUnauthorized();
					message.error(feedback.message);
					void router.navigateByUrl(UNAUTHORIZED_ROUTE);
				} else if (feedback.action === 'redirect-forbidden') {
					message.error(feedback.message);
					void router.navigateByUrl(FORBIDDEN_ROUTE);
				} else if (error.status === 0) {
					message.error(feedback.message);
				}
			}

			return throwError(() => error);
		})
	);
};
