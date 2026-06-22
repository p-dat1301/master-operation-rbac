import { HttpErrorResponse } from '@angular/common/http';

import { mapAdminHttpError } from './http-error-mapper';

describe('mapAdminHttpError', () => {
	it('maps auth and network errors to the expected feedback', () => {
		expect(mapAdminHttpError(new HttpErrorResponse({ status: 401 }))).toEqual({
			message: 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.',
			action: 'redirect-unauthorized'
		});
		expect(mapAdminHttpError(new HttpErrorResponse({ status: 403 }))).toEqual({
			message: 'Bạn không có quyền thực hiện thao tác này.',
			action: 'redirect-forbidden'
		});
		expect(mapAdminHttpError(new HttpErrorResponse({ status: 0 }))).toEqual({
			message: 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra mạng hoặc thử lại sau.',
			action: 'toast-only'
		});
	});

	it('prefers server error strings and details before fallback', () => {
		expect(mapAdminHttpError(new HttpErrorResponse({ status: 400, error: 'Invalid payload' }))).toEqual({
			message: 'Invalid payload',
			action: 'toast-only'
		});
		expect(mapAdminHttpError(new HttpErrorResponse({ status: 400, error: { detail: 'Bad request detail' } }))).toEqual({
			message: 'Bad request detail',
			action: 'toast-only'
		});
		expect(mapAdminHttpError(new HttpErrorResponse({ status: 400, error: '   ' }))).toEqual({
			message: 'Thao tác thất bại. Vui lòng thử lại.',
			action: 'toast-only'
		});
	});
});
