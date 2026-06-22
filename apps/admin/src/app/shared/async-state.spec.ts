import { signal } from '@angular/core';
import { of, throwError } from 'rxjs';

import { runAdminAsync } from './async-state';

describe('runAdminAsync', () => {
	it('toggles pending state and runs success/finally handlers', async () => {
		const pending = signal(false);
		const onSuccess = vi.fn();
		const onFinally = vi.fn();

		const result = await runAdminAsync(of('ok'), {
			pending,
			fallbackMessage: 'fallback',
			onSuccess,
			onFinally
		});

		expect(result).toBe('ok');
		expect(onSuccess).toHaveBeenCalledWith('ok');
		expect(pending()).toBe(false);
		expect(onFinally).toHaveBeenCalledTimes(1);
	});

	it('maps errors and returns null when request fails', async () => {
		const pending = signal(false);
		const onError = vi.fn();

		const result = await runAdminAsync(throwError(() => new Error('boom')), {
			pending,
			fallbackMessage: 'fallback',
			onError
		});

		expect(result).toBeNull();
		expect(pending()).toBe(false);
		expect(onError).toHaveBeenCalledWith(
			expect.objectContaining({ message: 'Thao tác thất bại. Vui lòng thử lại.', action: 'toast-only' }),
			'fallback'
		);
	});
});
