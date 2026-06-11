export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface TaskResponse {
	id: number;
	title: string;
	description: string | null;
	status: TaskStatus;
	priority: string | null;
	assignee_id: number | null;
	assignee_name: string | null;
	department_id: number | null;
	created_by: number | null;
	due_date: string | null;
	created_at: string;
	updated_at: string;
}

export interface TaskCreateRequest {
	title: string;
	description?: string;
	priority?: string;
	assignee_id?: number;
	department_id?: number;
	due_date?: string;
}

export interface TaskFilters {
	status?: TaskStatus;
	assignee_id?: number;
	department_id?: number;
}
