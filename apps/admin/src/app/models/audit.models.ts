export interface AuditLogResponse {
	id: number;
	actor_id: number | null;
	actor_name: string | null;
	action: string;
	resource_type: string;
	resource_id: string | null;
	detail: Record<string, unknown> | null;
	ip_address: string | null;
	created_at: string;
}
