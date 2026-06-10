export interface LoginRequest {
	email: string;
	password: string;
}

export interface LoginResponse {
	access_token: string;
	token_type: string;
	expires_in: number;
}

export interface UserResponse {
	id: number;
	employee_code: string;
	email: string;
	full_name: string;
	role_name: string;
	permissions: string[];
	phone: string | null;
	job_title: string | null;
	department_id: number | null;
	manager_id: number | null;
	is_active: boolean;
}
