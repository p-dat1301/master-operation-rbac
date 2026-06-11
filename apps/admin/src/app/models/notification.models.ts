export interface NotificationResponse {
	id: number;
	recipient_id: number;
	title: string;
	body: string;
	is_read: boolean;
	created_at: string;
}
