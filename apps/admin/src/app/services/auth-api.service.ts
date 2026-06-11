import { HttpClient } from '@angular/common/http';
import { Inject, Injectable } from '@angular/core';
import { Observable } from 'rxjs';

import { API_BASE_URL } from '../core/tokens/api-base-url.token';
import { LoginRequest, LoginResponse, UserResponse } from '../models/auth.models';
import { BaseApiService } from './base-api.service';

@Injectable({
	providedIn: 'root'
})
export class AuthApiService extends BaseApiService {
	constructor(http: HttpClient, @Inject(API_BASE_URL) apiBaseUrl: string) {
		super(http, apiBaseUrl);
	}

	login(payload: LoginRequest): Observable<LoginResponse> {
		return this.post<LoginRequest, LoginResponse>('/api/v1/auth/login', payload);
	}

	me(): Observable<UserResponse> {
		return this.get<UserResponse>('/api/v1/auth/me');
	}
}
