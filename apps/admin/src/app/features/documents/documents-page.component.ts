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
import { firstValueFrom } from 'rxjs';
import { AuthStoreService } from '../../services/auth-store.service';
import { AgenticApiService } from '../../services/agentic-api.service';
import { RbacApiService } from '../../services/rbac-api.service';
import { ADMIN_PAGE_COMMON_STYLES } from '../../shared/admin-page-styles';
import { runAdminAsync } from '../../shared/async-state';
import { AgenticDocument, AgenticDocumentUploadPolicy } from '../../models/agentic.models';

@Component({
	selector: 'app-documents-page',
	standalone: true,
	imports: [CommonModule, FormsModule, NzButtonModule, NzCardModule, NzDividerModule, NzIconModule, NzInputModule, NzModalModule, NzSelectModule, NzSpinModule, NzTableModule],
	templateUrl: './documents-page.component.html',
	styleUrls: ['../../shared/admin-page-styles.css', './documents-page.component.css']
})
export class DocumentsPageComponent implements OnInit {
	private readonly agenticApi = inject(AgenticApiService);
	private readonly authStore = inject(AuthStoreService);
	private readonly message = inject(NzMessageService);
	private readonly rbacApi = inject(RbacApiService);

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
	readonly roles = signal<{ name: string; display_name: string }[]>([]);
	readonly departments = signal<{ id: number; name: string }[]>([]);

	uploadForm: AgenticDocumentUploadPolicy = { classification: '', visibility_scope: 'global', allowed_roles: [], department_id: undefined };
	selectedFile: File | null = null;

	ngOnInit(): void {
		void this.loadDocuments();
		void this.loadUploadMetadataOptions();
	}

	async loadUploadMetadataOptions(): Promise<void> {
		try {
			const [rolesList, deptsList] = await Promise.all([
				firstValueFrom(this.rbacApi.listRoles()),
				firstValueFrom(this.rbacApi.listDepartments())
			]);
			this.roles.set(rolesList);
			this.departments.set(deptsList);
		} catch (err) {
			console.error('Failed to load roles and departments:', err);
		}
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
		this.uploadForm = { classification: 'internal', visibility_scope: 'global', allowed_roles: [], department_id: undefined };
		this.selectedFile = null;
		this.uploadError.set('');
		void this.loadUploadMetadataOptions();
		this.showUploadModal.set(true);
	}

	closeUploadModal(): void {
		this.showUploadModal.set(false);
	}

	onFileSelected(event: Event): void {
		const target = event.target as HTMLInputElement;
		this.selectedFile = target.files?.[0] ?? null;
	}

	submitUpload(): void {
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
		const fileToUpload = this.selectedFile;
		this.showUploadModal.set(false);

		const loadingMsg = this.message.loading(`Đang tải lên và phân tích tài liệu "${fileToUpload.name}" trong nền...`, { nzDuration: 0 });

		this.agenticApi.uploadDocument(fileToUpload, policy).subscribe({
			next: async () => {
				this.message.remove(loadingMsg.messageId);
				this.message.success(`Tài liệu "${fileToUpload.name}" đã được tải lên và lập chỉ mục (index) thành công.`);
				await this.loadDocuments();
			},
			error: (err) => {
				this.message.remove(loadingMsg.messageId);
				const errMsg = err?.error?.message || err?.message || 'Lỗi không xác định.';
				this.message.error(`Tải lên tài liệu "${fileToUpload.name}" thất bại: ${errMsg}`, { nzDuration: 8000 });
			}
		});
	}

	private isNotFoundMessage(message: string): boolean {
		return message.toLowerCase().includes('not found') || message.includes('404');
	}

	private buildValidatedPolicy(): AgenticDocumentUploadPolicy | null {
		const policy: AgenticDocumentUploadPolicy = {
			classification: this.uploadForm.classification?.trim() || undefined,
			visibility_scope: this.uploadForm.visibility_scope
		};

		if (policy.visibility_scope === 'role') {
			const allowedRoles = this.uploadForm.allowed_roles ?? [];
			if (allowedRoles.length === 0) {
				this.uploadError.set('Role-scoped uploads require at least one allowed role.');
				return null;
			}
			policy.allowed_roles = allowedRoles;
		} else if (policy.visibility_scope === 'department') {
			if (this.uploadForm.department_id === undefined || this.uploadForm.department_id === null) {
				this.uploadError.set('Department-scoped uploads require a department.');
				return null;
			}
			policy.department_id = this.uploadForm.department_id;
		}

		return policy;
	}
}
