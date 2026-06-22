import { HttpErrorResponse } from '@angular/common/http';

export type AdminHttpFeedback = {
	message: string;
	action: 'redirect-unauthorized' | 'redirect-forbidden' | 'toast-only';
};

export function mapAdminHttpError(error: unknown): AdminHttpFeedback {
	if (error instanceof HttpErrorResponse) {
		if (error.status === 401) {
			return {
				message: 'Phiên đăng nhập không hợp lệ hoặc đã hết hạn. Vui lòng đăng nhập lại.',
				action: 'redirect-unauthorized'
			};
		}

		if (error.status === 403) {
			return {
				message: 'Bạn không có quyền thực hiện thao tác này.',
				action: 'redirect-forbidden'
			};
		}

		if (error.status === 0) {
			return {
				message: 'Không thể kết nối đến máy chủ. Vui lòng kiểm tra mạng hoặc thử lại sau.',
				action: 'toast-only'
			};
		}

		if (typeof error.error === 'string' && error.error.trim()) {
			return { message: error.error, action: 'toast-only' };
		}

		const detail = error.error?.detail;
		if (typeof detail === 'string' && detail.trim()) {
			return { message: detail, action: 'toast-only' };
		}
	}

	return {
		message: 'Thao tác thất bại. Vui lòng thử lại.',
		action: 'toast-only'
	};
}
