import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { SyncSummary } from '../models/admin-config.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class AdminConfigSyncService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	syncMenu(dryRun = false): Observable<SyncSummary> {
		return this.post<{ dry_run: boolean }, SyncSummary>('/api/v1/admin/config/menu/sync', { dry_run: dryRun });
	}

	syncI18n(dryRun = false): Observable<SyncSummary> {
		return this.post<{ dry_run: boolean }, SyncSummary>('/api/v1/admin/config/i18n/sync', { dry_run: dryRun });
	}
}
