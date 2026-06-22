export interface RoleResponse {
	id: number;
	name: string;
	display_name: string;
}

export interface PermissionResponse {
	id: number;
	code: string;
	description: string | null;
}

export interface PermissionWriteRequest {
	code: string;
	description: string | null;
}

export interface DepartmentResponse {
	id: number;
	name: string;
	level: number;
	parent_id: number | null;
}

export interface RoleCreateRequest {
	name: string;
	display_name: string;
}

export interface RoleUpdateRequest {
	name: string;
	display_name: string;
}
