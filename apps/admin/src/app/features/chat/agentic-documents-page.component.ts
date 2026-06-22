import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzDividerModule } from 'ng-zorro-antd/divider';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzInputModule } from 'ng-zorro-antd/input';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzModalModule } from 'ng-zorro-antd/modal';
import { NzSelectModule } from 'ng-zorro-antd/select';
import { NzSpinModule } from 'ng-zorro-antd/spin';
import { NzTableModule } from 'ng-zorro-antd/table';
import { AuthStoreService } from '../../services/auth-store.service';
import { AgenticApiService } from '../../services/agentic-api.service';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';
import { runAdminAsync } from '../../shared/async-state';
import { AgenticDocument, AgenticDocumentUploadPolicy } from '../../models/agentic.models';

@Component({
	selector: 'app-agentic-documents-page',
	standalone: true,
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzDividerModule, NzIconModule, NzInputModule, NzModalModule, NzSelectModule, NzSpinModule, NzTableModule],
	template: `
		<section class="page-root" data-testid="agentic-documents-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Agentic workspace</p>
					<h2>Documents</h2>
					<p class="subtitle">List, inspect, and upload knowledge documents with policy controls.</p>
				</div>
				<div class="header-actions">
					<div class="count-chip surface-field">
						<span nz-icon nzType="file-text"></span>
						<span>{{ documents().length }} documents</span>
					</div>
					<button *ngIf="canUpload()" nz-button nzType="primary" nzSize="large" (click)="openUploadModal()" data-testid="upload-document-btn">
						<span nz-icon nzType="upload"></span> Upload document
					</button>
				</div>
			</div>

			<div class="content-grid">
				<nz-card class="surface-card table-panel" [nzBordered]="false">
					<div class="panel-title-row">
						<div>
							<h3 class="panel-title text-primary">Document list</h3>
							<p class="text-secondary">Browse all agentic documents and open a detail preview.</p>
						</div>
						<button nz-button nzType="default" (click)="loadDocuments()" [nzLoading]="listLoading()"><span nz-icon nzType="reload"></span> Refresh</button>
					</div>

					<nz-spin [nzSpinning]="listLoading()">
						<div *ngIf="listError()" class="state-panel error-state" data-testid="document-list-error">
							<span nz-icon nzType="warning"></span>
							<div><strong>Could not load documents.</strong><p>{{ listError() }}</p></div>
							<button nz-button nzSize="small" nzType="primary" (click)="loadDocuments()">Try again</button>
						</div>

						<div *ngIf="!listError() && !listLoading() && documents().length === 0" class="state-panel" data-testid="document-list-empty">
							<span nz-icon nzType="inbox"></span>
							<div><strong>No documents found yet.</strong><p>Uploaded agentic documents will appear here after a successful upload.</p></div>
						</div>

						<nz-table *ngIf="!listError() && documents().length > 0" #docTable [nzData]="documents()" [nzPageSize]="8" nzSize="middle" data-testid="agentic-documents-table">
							<thead>
								<tr>
									<th nzWidth="60px">#</th>
									<th>Document</th>
									<th nzWidth="140px">Status</th>
									<th nzWidth="180px">Type</th>
									<th nzWidth="140px" nzAlign="right">Action</th>
								</tr>
							</thead>
							<tbody>
								<tr *ngFor="let document of docTable.data; let i = index">
									<td class="idx-col">{{ i + 1 }}</td>
									<td>
										<div class="doc-name">{{ document.filename || document.document_id }}</div>
										<div class="text-muted">ID: {{ document.document_id }}</div>
									</td>
									<td><span class="status-pill" [class.status-pill--active]="document.status === 'ready'">{{ document.status }}</span></td>
									<td class="text-secondary">{{ document.mime_type || '—' }}</td>
									<td nzAlign="right"><button nz-button nzType="link" (click)="openDocument(document)">View detail</button></td>
								</tr>
							</tbody>
						</nz-table>
					</nz-spin>
				</nz-card>

				<nz-card class="surface-card detail-panel" [nzBordered]="false">
					<div class="panel-title-row">
						<div>
							<h3 class="panel-title text-primary">Document detail</h3>
							<p class="text-secondary">Fetch a real document by document_id for operational review.</p>
						</div>
					</div>

					<nz-spin [nzSpinning]="detailLoading()">
						<div *ngIf="detailError()" class="state-panel error-state" data-testid="document-detail-error">
							<span nz-icon nzType="warning"></span>
							<div><strong>Could not load document detail.</strong><p>{{ detailError() }}</p></div>
							<button nz-button nzSize="small" nzType="primary" (click)="refreshSelectedDocument()">Try again</button>
						</div>
						<div *ngIf="selectedDocument() && selectedDocument()?.status === 'not_found'" class="state-panel error-state" data-testid="document-not-found">
							<span nz-icon nzType="disconnect"></span>
							<div><strong>Document not found.</strong><p>The selected document was removed or is no longer accessible.</p></div>
						</div>
						<ng-container *ngIf="!detailError() && selectedDocument(); else noSelection">
							<div class="detail-grid">
								<div><span class="field-label">Document ID</span><div class="field-value">{{ selectedDocument()?.document_id }}</div></div>
								<div><span class="field-label">Filename</span><div class="field-value">{{ selectedDocument()?.filename || '—' }}</div></div>
								<div><span class="field-label">Mime type</span><div class="field-value">{{ selectedDocument()?.mime_type || '—' }}</div></div>
								<div><span class="field-label">Status</span><div class="field-value">{{ selectedDocument()?.status }}</div></div>
							</div>
							<div class="detail-actions">
								<button nz-button nzType="default" (click)="refreshSelectedDocument()" [disabled]="!selectedDocument()"><span nz-icon nzType="reload"></span> Reload detail</button>
							</div>
						</ng-container>
						<ng-template #noSelection>
							<div class="state-panel" data-testid="document-detail-empty">
								<span nz-icon nzType="file-search"></span>
								<div><strong>Select a document.</strong><p>Select a document from the list to inspect it here.</p></div>
							</div>
						</ng-template>
					</nz-spin>
				</nz-card>
			</div>

			<nz-modal [(nzVisible)]="showUploadModal" nzTitle="Upload agentic document" (nzOnCancel)="closeUploadModal()" (nzOnOk)="submitUpload()" [nzOkLoading]="uploading()" nzOkText="Upload" nzWidth="720px">
				<ng-container *nzModalContent>
					<div class="upload-grid">
						<label class="form-field">
							<span class="field-label">File <span class="required">*</span></span>
							<input type="file" (change)="onFileSelected($event)" />
						</label>
						<label class="form-field">
							<span class="field-label">Classification</span>
							<input nz-input [(ngModel)]="uploadForm.classification" placeholder="internal, confidential, ..." />
						</label>
						<label class="form-field">
							<span class="field-label">Visibility scope <span class="required">*</span></span>
							<nz-select [(ngModel)]="uploadForm.visibility_scope">
								<nz-option nzLabel="Public" nzValue="public"></nz-option>
								<nz-option nzLabel="Role" nzValue="role"></nz-option>
								<nz-option nzLabel="Department" nzValue="department"></nz-option>
							</nz-select>
						</label>
						<label class="form-field">
							<span class="field-label">Allowed roles</span>
							<input nz-input [(ngModel)]="allowedRolesInput" placeholder="comma-separated role names" />
						</label>
						<label class="form-field">
							<span class="field-label">Department ID</span>
							<input nz-input type="number" [(ngModel)]="uploadForm.department_id" placeholder="numeric department id" />
						</label>
						<div *ngIf="!canUpload()" class="state-panel error-state" data-testid="document-upload-forbidden">
							<span nz-icon nzType="lock"></span>
							<div><strong>Upload unavailable.</strong><p>You do not have permission to upload documents in this workspace.</p></div>
						</div>
						<div class="hint-box surface-field">
							<p class="text-secondary">Policy rules: role scope requires at least one allowed role; department scope requires a department_id.</p>
						</div>
						<div *ngIf="uploadError()" class="state-panel error-state" data-testid="document-upload-error">
							<span nz-icon nzType="warning"></span>
							<div><strong>Upload failed.</strong><p>{{ uploadError() }}</p></div>
						</div>
					</div>
				</ng-container>
			</nz-modal>
		</section>
	`,
	styles: [ADMIN_PAGE_COMMON_STYLES, `
		.header-actions { display:flex; align-items:center; gap:.75rem; flex-wrap:wrap }
		.count-chip { display:flex; align-items:center; gap:.5rem; padding:.65rem .9rem; border-radius:999px; color:var(--admin-text-secondary) }
		.content-grid { display:grid; grid-template-columns: 1.3fr .9fr; gap:1rem; align-items:start }
		.table-panel, .detail-panel { min-height: 100% }
		.panel-title-row { display:flex; justify-content:space-between; align-items:flex-start; gap:1rem; margin-bottom:1rem }
		.panel-title { margin:0; font-size:1.05rem }
		.doc-name { color:var(--admin-text-primary); font-weight:600 }
		.status-pill { display:inline-flex; align-items:center; padding:.2rem .55rem; border-radius:999px; background:rgba(248,113,113,.12); color:var(--admin-action-warning); font-size:.78rem; text-transform:capitalize }
		.status-pill--active { background:rgba(52,211,153,.12); color:var(--admin-action-success) }
		.detail-grid, .upload-grid { display:grid; gap:.9rem }
		.detail-grid { grid-template-columns: repeat(2, minmax(0, 1fr)); margin-top:.25rem }
		.field-label { display:block; margin-bottom:.25rem; color:var(--admin-text-muted); font-size:.82rem }
		.field-value { color:var(--admin-text-primary); font-weight:600; word-break:break-word }
		.detail-actions { margin-top:1rem }
		.empty-state, .error-state { margin:1rem 0 0; padding:.85rem 1rem; border-radius:.9rem; border:1px dashed var(--admin-border-subtle) }
		.empty-state { color:var(--admin-text-secondary); background:rgba(148,163,184,.04) }
		.error-state { color:#fecaca; background:rgba(248,113,113,.08); border-style:solid }
		.required { color:var(--admin-action-danger) }
		.hint-box { padding:.85rem 1rem; border-radius:.9rem }
		@media (max-width: 1100px) { .content-grid { grid-template-columns: 1fr } }
		@media (max-width: 720px) { .detail-grid { grid-template-columns: 1fr } }
	`]
})
export class AgenticDocumentsPageComponent implements OnInit {
	private readonly agenticApi = inject(AgenticApiService);
	private readonly authStore = inject(AuthStoreService);
	private readonly message = inject(NzMessageService);

	readonly documents = signal<AgenticDocument[]>([]);
	readonly selectedDocument = signal<AgenticDocument | null>(null);
	readonly listLoading = signal(false);
	readonly detailLoading = signal(false);
	readonly uploading = signal(false);
	readonly listError = signal('');
	readonly detailError = signal('');
	readonly uploadError = signal('');
	readonly showUploadModal = signal(false);
	readonly canUpload = signal(this.authStore.hasPermission('manage_org'));

	uploadForm: AgenticDocumentUploadPolicy = { classification: '', visibility_scope: 'public', allowed_roles: [], department_id: undefined };
	allowedRolesInput = '';
	selectedFile: File | null = null;

	ngOnInit(): void {
		void this.loadDocuments();
	}

	async loadDocuments(): Promise<void> {
		this.listError.set('');
		await runAdminAsync(this.agenticApi.getDocuments(), {
			pending: this.listLoading,
			fallbackMessage: 'Could not load agentic documents.',
			onSuccess: (result) => {
				this.documents.set(result.documents ?? []);
				if (this.selectedDocument()) {
					const currentId = this.selectedDocument()?.document_id;
					const refreshed = result.documents.find((doc) => doc.document_id === currentId);
					if (refreshed) {
						this.selectedDocument.set(refreshed);
					} else {
						this.selectedDocument.set({
							...(this.selectedDocument() as AgenticDocument),
							status: 'not_found'
						});
						this.detailError.set('The selected document is no longer available in the refreshed list.');
					}
				}
			},
			onError: (feedback, fallbackMessage) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallbackMessage;
				this.documents.set([]);
				this.listError.set(message);
				this.message.error(message);
			}
		});
	}

	async openDocument(document: AgenticDocument): Promise<void> {
		this.selectedDocument.set(document);
		this.detailError.set('');
		await runAdminAsync(this.agenticApi.getDocument(document.document_id), {
			pending: this.detailLoading,
			fallbackMessage: 'Could not load document detail.',
			onSuccess: (detail) => this.selectedDocument.set(detail),
			onError: (feedback, fallbackMessage) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallbackMessage;
				this.detailError.set(message);
				if (this.isNotFoundMessage(message)) {
					this.selectedDocument.set({ ...document, status: 'not_found' });
				}
				this.message.error(message);
			}
		});
	}

	async refreshSelectedDocument(): Promise<void> {
		const document = this.selectedDocument();
		if (!document) return;
		await this.openDocument(document);
	}

	openUploadModal(): void {
		if (!this.canUpload()) {
			this.uploadError.set('You do not have permission to upload documents in this workspace.');
			this.showUploadModal.set(true);
			return;
		}
		this.uploadForm = { classification: '', visibility_scope: 'public', allowed_roles: [], department_id: undefined };
		this.allowedRolesInput = '';
		this.selectedFile = null;
		this.uploadError.set('');
		this.showUploadModal.set(true);
	}

	closeUploadModal(): void {
		this.showUploadModal.set(false);
	}

	onFileSelected(event: Event): void {
		const target = event.target as HTMLInputElement;
		this.selectedFile = target.files?.[0] ?? null;
	}

	async submitUpload(): Promise<void> {
		if (!this.canUpload()) {
			this.uploadError.set('You do not have permission to upload documents in this workspace.');
			return;
		}

		if (!this.selectedFile) {
			this.uploadError.set('Please choose a file before uploading.');
			return;
		}

		const policy = this.buildValidatedPolicy();
		if (!policy) return;

		this.uploadError.set('');
		await runAdminAsync(this.agenticApi.uploadDocument(this.selectedFile, policy), {
			pending: this.uploading,
			fallbackMessage: 'Upload failed.',
			onSuccess: async () => {
				this.message.success('Document uploaded successfully.');
				this.showUploadModal.set(false);
				await this.loadDocuments();
			},
			onError: (feedback, fallbackMessage) => {
				const message = feedback.action === 'toast-only' ? feedback.message : fallbackMessage;
				this.uploadError.set(message);
				this.message.error(message);
			}
		});
	}

	private isNotFoundMessage(message: string): boolean {
		return message.toLowerCase().includes('not found') || message.includes('404');
	}

	private buildValidatedPolicy(): AgenticDocumentUploadPolicy | null {
		const allowedRoles = this.allowedRolesInput.split(',').map((role) => role.trim()).filter(Boolean);
		const policy: AgenticDocumentUploadPolicy = {
			classification: this.uploadForm.classification?.trim() || undefined,
			visibility_scope: this.uploadForm.visibility_scope,
			allowed_roles: allowedRoles.length ? allowedRoles : undefined,
			department_id: this.uploadForm.department_id ?? undefined
		};

		if (policy.visibility_scope === 'role' && (!policy.allowed_roles || policy.allowed_roles.length === 0)) {
			this.uploadError.set('Role-scoped uploads require at least one allowed role.');
			return null;
		}

		if (policy.visibility_scope === 'department' && policy.department_id === undefined) {
			this.uploadError.set('Department-scoped uploads require a department_id.');
			return null;
		}

		return policy;
	}

}
