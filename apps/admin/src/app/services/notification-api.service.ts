import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { NotificationResponse } from '../models/notification.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class NotificationApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	listNotifications(): Observable<NotificationResponse[]> {
		return this.get<NotificationResponse[]>('/api/v1/notifications/');
	}

	markAsRead(id: number): Observable<NotificationResponse> {
		return this.http.put<NotificationResponse>(this.buildUrl(`/api/v1/notifications/${id}/read`), {});
	}

	markAllAsRead(): Observable<{ marked_count: number }> {
		return this.http.put<{ marked_count: number }>(this.buildUrl('/api/v1/notifications/read-all'), {});
	}

	private buildUrl(path: string): string {
		return `${(this as unknown as { apiBaseUrl: string }).apiBaseUrl}${path}`;
	}
}
