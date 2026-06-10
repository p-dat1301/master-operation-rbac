import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';

@Injectable({
	providedIn: 'root'
})
export class BaseApiService {
	constructor(
		protected readonly http: HttpClient,
		@Inject(API_BASE_URL) protected readonly apiBaseUrl: string
	) {}

	protected get<T>(path: string): Observable<T> {
		return this.http.get<T>(this.resolveUrl(path));
	}

	protected post<TRequest, TResponse>(path: string, body: TRequest): Observable<TResponse> {
		return this.http.post<TResponse>(this.resolveUrl(path), body);
	}

	private resolveUrl(path: string): string {
		return `${this.apiBaseUrl}${path}`;
	}
}
