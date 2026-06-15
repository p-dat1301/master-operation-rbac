import { CommonModule } from '@angular/common';
import { Component, OnInit, inject, signal } from '@angular/core';
import { NzBadgeModule } from 'ng-zorro-antd/badge';
import { NzButtonModule } from 'ng-zorro-antd/button';
import { NzCardModule } from 'ng-zorro-antd/card';
import { NzIconModule } from 'ng-zorro-antd/icon';
import { NzMessageService } from 'ng-zorro-antd/message';
import { NzTableModule } from 'ng-zorro-antd/table';
import { NzTooltipModule } from 'ng-zorro-antd/tooltip';
import { firstValueFrom } from 'rxjs';

import { NotificationResponse } from '../../models/notification.models';
import { NotificationApiService } from '../../services/notification-api.service';
import { ADMIN_DATETIME_FORMAT } from '../../shared/date-formats';

@Component({
	selector: 'app-notifications-page',
	standalone: true,
	imports: [CommonModule, NzBadgeModule, NzButtonModule, NzCardModule, NzIconModule, NzTableModule, NzTooltipModule],
	template: `
		<section class="page-root" data-testid="notifications-page">
			<div class="page-header">
				<div>
					<p class="eyebrow">Inbox</p>
					<h2>Thông báo</h2>
					<p class="subtitle">Các thông báo hệ thống gửi đến tài khoản của bạn.</p>
				</div>
				<div class="header-actions">
					<div class="unread-badge" *ngIf="unreadCount() > 0">
						<nz-badge [nzCount]="unreadCount()" nzStandalone [nzStyle]="{ backgroundColor: '#0ea5e9' }"></nz-badge>
						<span>chưa đọc</span>
					</div>
					<button nz-button nzType="dashed" (click)="markAll()" [disabled]="unreadCount() === 0" id="mark-all-read-btn">
						<span nz-icon nzType="check-square"></span> Đánh dấu tất cả đã đọc
					</button>
				</div>
			</div>

			<nz-card class="table-card" [nzBordered]="false">
				<nz-table #notifTable [nzData]="notifications()" [nzLoading]="loading()" [nzPageSize]="20" nzSize="middle" data-testid="notifications-table">
					<thead>
						<tr>
							<th nzWidth="50px"></th>
							<th>Tiêu đề</th>
							<th>Nội dung</th>
							<th nzWidth="160px">Thời gian</th>
							<th nzWidth="120px" nzAlign="right">Hành động</th>
						</tr>
					</thead>
					<tbody>
						<tr *ngFor="let n of notifTable.data" [class.unread-row]="!n.is_read">
							<td nzAlign="center">
								<nz-badge *ngIf="!n.is_read" nzStatus="processing" nz-tooltip="Chưa đọc"></nz-badge>
								<span *ngIf="n.is_read" nz-icon nzType="check-circle" style="color:rgba(148,163,184,.4)"></span>
							</td>
							<td>
								<span [class.notif-title-unread]="!n.is_read" [class.notif-title-read]="n.is_read">{{ n.title }}</span>
							</td>
							<td class="muted">{{ n.body }}</td>
							<td class="time-col">{{ n.created_at | date:ADMIN_DATETIME_FORMAT }}</td>
							<td nzAlign="right">
								<button *ngIf="!n.is_read" nz-button nzType="text" nzSize="small" (click)="markOne(n)" nz-tooltip="Đánh dấu đã đọc" style="color:#60a5fa" [attr.data-testid]="'mark-read-'+n.id">
									<span nz-icon nzType="eye"></span>
								</button>
							</td>
						</tr>
					</tbody>
				</nz-table>
			</nz-card>
		</section>
	`,
	styles: [`
		.page-root { display:grid; gap:1.5rem }
		.page-header { display:flex; align-items:flex-start; justify-content:space-between; gap:1rem; flex-wrap:wrap }
		h2 { margin:.2rem 0 0; font-size:clamp(1.4rem,2.5vw,2rem); color:#f8fafc }
		.eyebrow { margin:0; font-size:.76rem; font-weight:700; letter-spacing:.18em; text-transform:uppercase; color:#7dd3fc }
		.subtitle { margin:.4rem 0 0; color:rgba(226,232,240,.65); font-size:.9rem }
		.header-actions { display:flex; align-items:center; gap:1rem }
		.unread-badge { display:flex; align-items:center; gap:.5rem; color:rgba(226,232,240,.75); font-size:.9rem }
		.table-card { background:rgba(15,23,42,.72); border-radius:1.2rem }
		.unread-row { background:rgba(14,165,233,.04) }
		.notif-title-unread { font-weight:700; color:#f8fafc }
		.notif-title-read { color:rgba(226,232,240,.6) }
		.muted { color:rgba(226,232,240,.65); font-size:.88rem }
		.time-col { font-size:.82rem; color:rgba(148,163,184,.7); font-family:monospace }
	`]
})
export class NotificationsPageComponent implements OnInit {
	protected readonly ADMIN_DATETIME_FORMAT = ADMIN_DATETIME_FORMAT;
	private readonly notifApi = inject(NotificationApiService);
	private readonly message = inject(NzMessageService);

	readonly notifications = signal<NotificationResponse[]>([]);
	readonly loading = signal(false);

	readonly unreadCount = () => this.notifications().filter(n => !n.is_read).length;

	ngOnInit(): void { this.load(); }

	async load(): Promise<void> {
		this.loading.set(true);
		try {
			const data = await firstValueFrom(this.notifApi.listNotifications());
			this.notifications.set(data);
		} catch { this.message.error('Không thể tải thông báo.'); }
		finally { this.loading.set(false); }
	}

	async markOne(n: NotificationResponse): Promise<void> {
		try {
			const updated = await firstValueFrom(this.notifApi.markAsRead(n.id));
			this.notifications.update(list => list.map(item => item.id === updated.id ? updated : item));
		} catch { this.message.error('Không thể cập nhật thông báo.'); }
	}

	async markAll(): Promise<void> {
		try {
			const res = await firstValueFrom(this.notifApi.markAllAsRead());
			this.notifications.update(list => list.map(n => ({ ...n, is_read: true })));
			this.message.success(`Đã đánh dấu ${res.marked_count} thông báo đã đọc.`);
		} catch { this.message.error('Thao tác thất bại.'); }
	}
}
