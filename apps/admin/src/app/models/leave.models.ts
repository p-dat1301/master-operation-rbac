export type LeaveStatus = 'pending' | 'approved' | 'rejected' | 'cancelled';
export type LeaveType = 'annual' | 'sick' | 'unpaid' | 'other';

export interface LeaveRequestResponse {
	id: number;
	user_id: number;
	user_name: string | null;
	leave_type: LeaveType;
	start_date: string;
	end_date: string;
	reason: string | null;
	status: LeaveStatus;
	approved_by: number | null;
	created_at: string;
}

export interface LeaveBalanceResponse {
	id: number;
	user_id: number;
	year: number;
	total_days: number;
	used_days: number;
	remaining_days: number;
}

export interface LeaveFilters {
	status?: LeaveStatus;
	user_id?: number;
	leave_type?: LeaveType;
}
