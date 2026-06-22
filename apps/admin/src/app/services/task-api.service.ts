import { HttpClient, HttpParams } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { TaskCreateRequest, TaskFilters, TaskResponse, TaskUpdateRequest } from '../models/task.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class TaskApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	listTasks(filters?: TaskFilters): Observable<TaskResponse[]> {
		let params = new HttpParams();
		if (filters?.status) params = params.set('status', filters.status);
		if (filters?.assignee_id != null) params = params.set('assignee_id', filters.assignee_id);
		if (filters?.department_id != null) params = params.set('department_id', filters.department_id);
		return this.http.get<TaskResponse[]>(this.buildUrl('/api/v1/tasks/'), { params });
	}

	getTask(id: number): Observable<TaskResponse> {
		return this.get<TaskResponse>(`/api/v1/tasks/${id}`);
	}

	createTask(data: TaskCreateRequest): Observable<TaskResponse> {
		return this.http.post<TaskResponse>(this.buildUrl('/api/v1/tasks/'), data);
	}

	updateTask(id: number, data: TaskUpdateRequest): Observable<TaskResponse> {
		return this.http.put<TaskResponse>(this.buildUrl(`/api/v1/tasks/${id}`), data);
	}

	assignTask(id: number, assignee_id: number): Observable<TaskResponse> {
		return this.http.put<TaskResponse>(this.buildUrl(`/api/v1/tasks/${id}/assign`), { assignee_id });
	}

	startTask(id: number): Observable<TaskResponse> {
		return this.http.put<TaskResponse>(this.buildUrl(`/api/v1/tasks/${id}/start`), {});
	}

	completeTask(id: number): Observable<TaskResponse> {
		return this.http.put<TaskResponse>(this.buildUrl(`/api/v1/tasks/${id}/complete`), {});
	}

	cancelTask(id: number): Observable<TaskResponse> {
		return this.http.put<TaskResponse>(this.buildUrl(`/api/v1/tasks/${id}/cancel`), {});
	}

	deleteTask(id: number): Observable<unknown> {
		return this.http.delete(this.buildUrl(`/api/v1/tasks/${id}`));
	}
}
