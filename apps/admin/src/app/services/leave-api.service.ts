import { HttpClient, HttpParams } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { LeaveBalanceResponse, LeaveBalanceUpdatePayload, LeaveFilters, LeaveRequestResponse, LeaveReviewPayload, LeaveUpdatePayload } from '../models/leave.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class LeaveApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	// ── Leave Requests ────────────────────────────────────────────────────
	listLeaves(filters?: LeaveFilters): Observable<LeaveRequestResponse[]> {
		let params = new HttpParams();
		if (filters?.status) params = params.set('status', filters.status);
		if (filters?.user_id != null) params = params.set('user_id', filters.user_id);
		if (filters?.leave_type) params = params.set('leave_type', filters.leave_type);
		return this.http.get<LeaveRequestResponse[]>(this.buildUrl('/api/v1/leaves/'), { params });
	}

	reviewLeave(id: number, payload: LeaveReviewPayload): Observable<LeaveRequestResponse> {
		return this.http.put<LeaveRequestResponse>(this.buildUrl(`/api/v1/leaves/${id}/review`), payload);
	}

	updateLeave(id: number, payload: LeaveUpdatePayload): Observable<LeaveRequestResponse> {
		return this.http.put<LeaveRequestResponse>(this.buildUrl(`/api/v1/leaves/${id}`), payload);
	}

	cancelLeave(id: number): Observable<LeaveRequestResponse> {
		return this.http.put<LeaveRequestResponse>(this.buildUrl(`/api/v1/leaves/${id}/cancel`), {});
	}

	// ── Leave Balances ────────────────────────────────────────────────────
	getMyLeaveBalance(year?: number): Observable<LeaveBalanceResponse> {
		let params = new HttpParams();
		if (year != null) params = params.set('year', year);
		return this.http.get<LeaveBalanceResponse>(this.buildUrl('/api/v1/leave-balances/me'), { params });
	}

	getUserLeaveBalance(userId: number, year?: number): Observable<LeaveBalanceResponse> {
		let params = new HttpParams();
		if (year != null) params = params.set('year', year);
		return this.http.get<LeaveBalanceResponse>(this.buildUrl(`/api/v1/leave-balances/users/${userId}`), { params });
	}

	updateUserLeaveBalance(userId: number, payload: LeaveBalanceUpdatePayload): Observable<LeaveBalanceResponse> {
		return this.http.put<LeaveBalanceResponse>(this.buildUrl(`/api/v1/leave-balances/users/${userId}`), payload);
	}
}
