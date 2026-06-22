import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { DepartmentResponse, PermissionResponse, PermissionWriteRequest, RoleCreateRequest, RoleResponse, RoleUpdateRequest } from '../models/rbac.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class RbacApiService extends BaseApiService {
	private readonly base: string;

	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
		this.base = apiBaseUrl;
	}

	// ── Roles ────────────────────────────────────────────────────────────
	listRoles(): Observable<RoleResponse[]> {
		return this.get<RoleResponse[]>('/api/v1/roles/');
	}

	createRole(data: RoleCreateRequest): Observable<RoleResponse> {
		return this.post<RoleCreateRequest, RoleResponse>('/api/v1/roles/', data);
	}

	updateRole(id: number, data: RoleUpdateRequest): Observable<RoleResponse> {
		return this.http.put<RoleResponse>(`${this.base}/api/v1/roles/${id}`, data);
	}

	deleteRole(id: number): Observable<unknown> {
		return this.http.delete(`${this.base}/api/v1/roles/${id}`);
	}

	// ── Permissions ───────────────────────────────────────────────────────
	listPermissions(): Observable<PermissionResponse[]> {
		return this.get<PermissionResponse[]>('/api/v1/permissions/');
	}

	createPermission(data: PermissionWriteRequest): Observable<PermissionResponse> {
		return this.post<PermissionWriteRequest, PermissionResponse>('/api/v1/permissions/', data);
	}

	updatePermission(id: number, data: PermissionWriteRequest): Observable<PermissionResponse> {
		return this.http.put<PermissionResponse>(`${this.base}/api/v1/permissions/${id}`, data);
	}

	deletePermission(id: number): Observable<unknown> {
		return this.http.delete(`${this.base}/api/v1/permissions/${id}`);
	}

	listRolePermissions(roleId: number): Observable<PermissionResponse[]> {
		return this.get<PermissionResponse[]>(`/api/v1/roles/${roleId}/permissions`);
	}

	addPermissionToRole(roleId: number, permissionId: number): Observable<PermissionResponse[]> {
		return this.post<unknown, PermissionResponse[]>(`/api/v1/roles/${roleId}/permissions/${permissionId}`, {});
	}

	removePermissionFromRole(roleId: number, permissionId: number): Observable<PermissionResponse[]> {
		return this.http.delete<PermissionResponse[]>(`${this.base}/api/v1/roles/${roleId}/permissions/${permissionId}`);
	}

	listDepartments(): Observable<DepartmentResponse[]> {
		return this.get<DepartmentResponse[]>('/api/v1/departments/');
	}
}
