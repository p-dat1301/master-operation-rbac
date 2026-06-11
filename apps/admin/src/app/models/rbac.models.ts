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

export interface RoleCreateRequest {
	name: string;
	display_name: string;
}

export interface RoleUpdateRequest {
	name: string;
	display_name: string;
}
