import { HttpClient, HttpParams } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { UserCreateRequest, UserFilters, UserListItem, UserUpdateRequest } from '../models/user.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class UserApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	listUsers(filters?: UserFilters): Observable<UserListItem[]> {
		let params = new HttpParams();
		if (filters?.department_id != null) params = params.set('department_id', filters.department_id);
		if (filters?.role_name) params = params.set('role_name', filters.role_name);
		if (filters?.is_active != null) params = params.set('is_active', filters.is_active);
		return this.http.get<UserListItem[]>(this.buildUrl('/api/v1/users/'), { params });
	}

	getUser(id: number): Observable<UserListItem> {
		return this.get<UserListItem>(`/api/v1/users/${id}`);
	}

	createUser(data: UserCreateRequest): Observable<UserListItem> {
		return this.post<UserCreateRequest, UserListItem>('/api/v1/users/', data);
	}

	updateUser(id: number, data: UserUpdateRequest): Observable<UserListItem> {
		return this.http.put<UserListItem>(this.buildUrl(`/api/v1/users/${id}`), data);
	}

	deleteUser(id: number): Observable<UserListItem> {
		return this.http.delete<UserListItem>(this.buildUrl(`/api/v1/users/${id}`));
	}

	activateUser(id: number): Observable<UserListItem> {
		return this.http.put<UserListItem>(this.buildUrl(`/api/v1/users/${id}/activate`), {});
	}

	deactivateUser(id: number): Observable<UserListItem> {
		return this.http.put<UserListItem>(this.buildUrl(`/api/v1/users/${id}/deactivate`), {});
	}

	resetPassword(id: number, new_password: string): Observable<UserListItem> {
		return this.http.put<UserListItem>(this.buildUrl(`/api/v1/users/${id}/reset-password`), { new_password });
	}
}
