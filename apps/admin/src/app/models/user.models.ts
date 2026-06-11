export interface UserListItem {
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

export interface UserCreateRequest {
	employee_code: string;
	email: string;
	full_name: string;
	password: string;
	role_name: string;
	phone?: string;
	job_title?: string;
	department_id?: number;
	manager_id?: number;
}

export interface UserUpdateRequest {
	full_name?: string;
	phone?: string;
	job_title?: string;
	department_id?: number;
	manager_id?: number;
	role_name?: string;
}

export interface UserFilters {
	department_id?: number;
	role_name?: string;
	is_active?: boolean;
}
