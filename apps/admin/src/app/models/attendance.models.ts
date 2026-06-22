export interface AttendanceResponse {
	id: number;
	user_id: number;
	date: string;
	check_in: string;
	check_out: string | null;
	total_minutes: number | null;
	ip_address: string | null;
	note: string | null;
	department_id: number | null;
	status: string | null;
}

export interface AttendanceFilters {
	start_date: string;
	end_date: string;
	user_id?: number;
	department_id?: number;
}
