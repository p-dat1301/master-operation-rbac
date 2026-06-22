export const ADMIN_PAGE_COMMON_STYLES = `
	:host {
		--admin-text-primary: #f8fafc;
		--admin-text-secondary: rgba(226, 232, 240, .82);
		--admin-text-muted: rgba(148, 163, 184, .84);
		--admin-text-strong: #e2e8f0;
		--admin-surface-card: rgba(15, 23, 42, .72);
		--admin-surface-card-strong: rgba(8, 15, 28, .82);
		--admin-surface-table: rgba(8, 15, 28, .6);
		--admin-surface-field: rgba(15, 23, 42, .56);
		--admin-border-subtle: rgba(148, 163, 184, .14);
		--admin-action-primary: #7dd3fc;
		--admin-action-primary-strong: #38bdf8;
		--admin-action-success: #34d399;
		--admin-action-warning: #fbbf24;
		--admin-action-danger: #f87171;
	}

	.page-root {
		display: grid;
		gap: 1.5rem;
	}

	.page-header {
		display: flex;
		align-items: flex-start;
		justify-content: space-between;
		gap: 1rem;
		flex-wrap: wrap;
	}

	h2,
	.text-primary {
		margin: .2rem 0 0;
		font-size: clamp(1.4rem, 2.5vw, 2rem);
		color: var(--admin-text-primary);
	}

	.eyebrow,
	.text-action {
		margin: 0;
		font-size: .76rem;
		font-weight: 700;
		letter-spacing: .18em;
		text-transform: uppercase;
		color: var(--admin-action-primary);
	}

	.subtitle,
	.text-secondary {
		margin: .4rem 0 0;
		color: var(--admin-text-secondary);
		font-size: .9rem;
	}

	.text-muted {
		color: var(--admin-text-muted);
	}

	.text-strong {
		color: var(--admin-text-strong);
		font-weight: 600;
	}

	.surface-card,
	.filter-card,
	.table-card,
	.modal-surface {
		background: var(--admin-surface-card);
		border: 1px solid var(--admin-border-subtle);
		border-radius: 1.2rem;
	}

	.surface-card-strong {
		background: var(--admin-surface-card-strong);
	}

	.surface-table {
		background: var(--admin-surface-table);
	}

	.surface-field {
		background: var(--admin-surface-field);
	}

	.filter-row {
		display: flex;
		align-items: flex-end;
		gap: 1rem;
		flex-wrap: wrap;
	}

	.filter-item,
	.form-field {
		display: grid;
		gap: .35rem;
		font-size: .85rem;
		color: var(--admin-text-secondary);
	}

	.idx-col,
	.idx {
		color: var(--admin-text-muted);
		font-size: .82rem;
	}

	.muted,
	.desc {
		color: var(--admin-text-secondary);
		font-size: .88rem;
	}

	.form-grid {
		display: grid;
		gap: .85rem;
	}

	.action-primary { color: var(--admin-action-primary); }
	.action-primary-strong { color: var(--admin-action-primary-strong); }
	.action-success { color: var(--admin-action-success); }
	.action-warning { color: var(--admin-action-warning); }
	.action-danger { color: var(--admin-action-danger); }
`;
