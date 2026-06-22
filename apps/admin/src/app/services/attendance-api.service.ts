import { HttpClient, HttpParams } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { AttendanceFilters, AttendanceResponse } from '../models/attendance.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class AttendanceApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	listAttendance(filters: AttendanceFilters): Observable<AttendanceResponse[]> {
		let params = new HttpParams()
			.set('start_date', filters.start_date)
			.set('end_date', filters.end_date);

		if (filters.user_id != null) {
			params = params.set('user_id', filters.user_id);
		}

		if (filters.department_id != null) {
			params = params.set('department_id', filters.department_id);
		}

		return this.http.get<AttendanceResponse[]>(this.buildUrl('/api/v1/attendance/heatmap'), { params });
	}
}
