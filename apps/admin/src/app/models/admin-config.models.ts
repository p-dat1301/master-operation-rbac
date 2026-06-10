export interface SyncSummary {
	resource: 'menu' | 'i18n' | string;
	created: number;
	updated: number;
	skipped: number;
	errors: string[];
	dry_run: boolean;
}
