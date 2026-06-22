export type TaskStatus = 'pending' | 'in_progress' | 'completed' | 'cancelled';

export interface TaskResponse {
	id: number;
	task_code?: string | null;
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
	start_date?: string | null;
	estimated_hours?: number | null;
}

export interface TaskCreateRequest {
	task_code?: string;
	title: string;
	description?: string;
	priority?: string;
	assignee_id?: number;
	department_id?: number;
	due_date?: string;
	start_date?: string;
	estimated_hours?: number;
}

export interface TaskUpdateRequest {
	title?: string;
	description?: string;
	priority?: string;
	assignee_id?: number | null;
	department_id?: number | null;
	due_date?: string | null;
	start_date?: string | null;
	estimated_hours?: number | null;
}

export interface TaskFilters {
	status?: TaskStatus;
	assignee_id?: number;
	department_id?: number;
}
