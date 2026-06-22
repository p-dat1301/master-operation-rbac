import { WritableSignal } from '@angular/core';
import { firstValueFrom, Observable } from 'rxjs';

import { AdminHttpFeedback, mapAdminHttpError } from './http-error-mapper';

export type AdminAsyncErrorHandler = (feedback: AdminHttpFeedback, fallbackMessage: string) => void;

export type AdminAsyncOptions<T> = {
	pending?: WritableSignal<boolean>;
	fallbackMessage: string;
	onSuccess?: (value: T) => void | Promise<void>;
	onError?: AdminAsyncErrorHandler;
	onFinally?: () => void | Promise<void>;
};

export async function runAdminAsync<T>(
	request: Observable<T>,
	options: AdminAsyncOptions<T>
): Promise<T | null> {
	const { pending, fallbackMessage, onSuccess, onError, onFinally } = options;

	pending?.set(true);

	try {
		const value = await firstValueFrom(request);
		await onSuccess?.(value);
		return value;
	} catch (error) {
		const feedback = mapAdminHttpError(error);
		onError?.(feedback, fallbackMessage);
		return null;
	} finally {
		pending?.set(false);
		await onFinally?.();
	}
}
