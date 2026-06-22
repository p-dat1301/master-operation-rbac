export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type LeaveType = 'annual' | 'sick' | 'unpaid' | 'other';

export interface LeaveRequestResponse {
	id: number;
	requester_id?: number;
	user_id: number;
	user_name: string | null;
	leave_type: LeaveType;
	start_date: string;
	end_date: string;
	reason: string | null;
	status: LeaveStatus;
	department_id?: number | null;
	reviewed_by?: number | null;
	approved_by: number | null;
	rejected_reason?: string | null;
	reviewed_at?: string | null;
	created_at: string | null;
}

export interface LeaveReviewPayload {
	action: 'approve' | 'reject';
	rejected_reason?: string;
}

export interface LeaveUpdatePayload {
	leave_type: LeaveType;
	start_date: string;
	end_date: string;
	reason?: string | null;
}

export interface LeaveBalanceResponse {
	id: number;
	user_id: number;
	year: number;
	total_days: number;
	used_days: number;
	pending_days: number;
	remaining_days: number;
}

export interface LeaveBalanceUpdatePayload {
	year: number;
	total_days: number;
	used_days: number;
}

export interface LeaveFilters {
	status?: LeaveStatus;
	user_id?: number;
	leave_type?: LeaveType;
}
