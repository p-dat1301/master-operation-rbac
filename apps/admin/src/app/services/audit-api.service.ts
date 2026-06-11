import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { AuditLogResponse } from '../models/audit.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class AuditApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	listAuditLogs(): Observable<AuditLogResponse[]> {
		return this.get<AuditLogResponse[]>('/api/v1/audit_logs/');
	}
}
